import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# ---------------------------------------------------------
# 1. ICT US Equity Glassmorphic UI & Sparkle CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="ICT US Equity Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

css_style = """
<style>
    /* 슬레이트 다크 네이비 프리미엄 배경 */
    .stApp {
        background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* 사이드바 스타일링 */
    section[data-testid="stSidebar"] {
        background-color: #1c2541 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* 반짝이는 네온 헤더 */
    .shimmer-header {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc, #38bdf8);
        background-size: 200% auto;
        color: transparent;
        -webkit-background-clip: text;
        animation: shine 3.5s linear infinite;
        font-weight: 800;
        letter-spacing: -1px;
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }

    /* 둥그런 매수 버튼 (에메랄드 네온) */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 28px !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.7);
    }

    /* 둥그런 Glassmorphism 타점 카드 */
    .trade-card {
        background: rgba(28, 37, 65, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }

    /* 수치 박스 (진입가/손절가/목표가) */
    .metric-box-entry {
        background: rgba(16, 185, 129, 0.12);
        border: 1.5px solid #10b981;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }
    .metric-box-sl {
        background: rgba(239, 68, 68, 0.12);
        border: 1.5px solid #ef4444;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
    }
    .metric-box-tp {
        background: rgba(59, 130, 246, 0.12);
        border: 1.5px solid #3b82f6;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
    }

    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .metric-val {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 로그인 비밀번호
# ---------------------------------------------------------
MY_PASSWORD = "1234"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; margin-top: 100px;'>🔐 ICT US DAY TRADING TERMINAL</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd_input = st.text_input("액세스 암호를 입력하세요:", type="password")
        if st.button("터미널 접속"):
            if pwd_input == MY_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("암호가 일치하지 않습니다.")
    st.stop()

# ---------------------------------------------------------
# 3. 100% ICT (Smart Money Concepts) 미국 급등주 전용 프롬프트
# ---------------------------------------------------------
SYSTEM_PROMPT = """
당신은 ICT(Inner Circle Trader) / SMC(Smart Money Concepts) 전문 트레이더 AI입니다.
업로드된 미국 급등주 차트 이미지(1개~4개 자유 업로드)를 시각적으로 정밀 분석하여 오직 'Long(매수)' 진입 타점만을 산출하세요.

[ICT 필수 분석 체크리스트]
1. NY Morning Kill Zone (9:30 AM EST 개장 유동성) 및 BSL/SSL Sweep (스윕/개미털기) 여부
2. MSS (Market Structure Shift) / CHoCH (구조 전환) 발생 및 Displacement (기관 장대양봉) 확인
3. FVG (Fair Value Gap / 비효율 갭) 및 Bullish Order Block (불리쉬 오더블록) 진입 타점 설정
4. Target Liquidity (상단 BSL / 전고점 / 유동성 풀) 목표가 설정

응답은 장문의 부연 설명 없이, 아래 JSON 포맷으로만 정밀하게 출력하세요:

```json
{
  "ticker_info": "$SOUN (1시간/15분/5분 ICT 중첩)",
  "killzone_status": "NY Morning Killzone (적합)",
  "ict_setup": "SSL 스윕 후 FVG + Order Block 재테스트 매수",
  "entry": "$5.45",
  "stop_loss": "$5.20",
  "tp1": "$5.85",
  "tp2": "$6.30",
  "risk_reward": "1 : 2.6",
  "ict_reasons": [
    "SSL(장초반 손절 물량) 청산 스윕 완료",
    "강력한 Displacement(기관 장대양봉) 및 MSS(구조 전환) 확인",
    "5분봉 FVG(비효율 갭) 및 Bullish Order Block 지지 테스트"
  ],
  "invalidation": "FVG 하단 및 오더블록 훼손 시($5.20 하향 종가 이탈) 즉시 손절"
}
