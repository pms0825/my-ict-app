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

st.markdown("""
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
""", unsafe_allow_html=True)

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
"""

---------------------------------------------------------
4. 0% 에러 자동 모델 복구 엔진
---------------------------------------------------------
def call_gemini_ai(api_key, contents):
genai.configure(api_key=api_key)

# 1차 시도: 최신 속도 우수 모델
priority_models = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-1.5-pro'
]

for m_name in priority_models:
    try:
        model = genai.GenerativeModel(m_name)
        res = model.generate_content(contents)
        return res.text, m_name
    except Exception:
        continue

# 2차 시도: 계정에서 사용 가능한 모델 수동 검색 Fallback
try:
    available_models = [
        m.name for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods
    ]
    for m_name in available_models:
        try:
            model = genai.GenerativeModel(m_name)
            res = model.generate_content(contents)
            return res.text, m_name
        except Exception:
            continue
except Exception as e:
    raise Exception(f"사용 가능한 AI 모델 탐색 실패: {e}")

raise Exception("모든 AI 모델 호출 실패. API 키 권한을 확인하세요.")
---------------------------------------------------------
5. 사이드바 설정
---------------------------------------------------------
st.sidebar.markdown("## ⚙️ SETTINGS")

if "GEMINI_API_KEY" in st.secrets:
api_key = st.secrets["GEMINI_API_KEY"]
st.sidebar.success("🔑 API Key 자동 연결됨")
else:
api_key = st.sidebar.text_input("Gemini API Key:", type="password")

st.sidebar.markdown("---")
st.sidebar.markdown("## 💬 ICT CONSULTING")

---------------------------------------------------------
6. 메인 UI - 드래그 & 드롭 한 번으로 해결되는 업로더
---------------------------------------------------------
st.markdown("⚡ ICT US EQUITY DAY TRADING TERMINAL", unsafe_allow_html=True)
st.caption("미국 급등주 차트(1시간, 15분, 5분, 1분봉 등)를 1개~4개 자유롭게 드래그해서 넣으세요. ICT 스마트머니 프레임워크 기반 최적 타점을 산출합니다.")

uploaded_files = st.file_uploader(
"📸 미국주식 차트 이미지 drag & drop (1개~4개 한번에 업로드 가능)",
type=["png", "jpg", "jpeg"],
accept_multiple_files=True
)

images = []
if uploaded_files:
cols = st.columns(min(len(uploaded_files), 4))
for idx, file in enumerate(uploaded_files):
img = Image.open(file)
images.append(img)
with cols[idx % 4]:
st.image(img, caption=f"차트 #{idx+1}", use_container_width=True)

st.markdown("


", unsafe_allow_html=True)

---------------------------------------------------------
7. 분석 실행 및 시각 카드 UI 출력
---------------------------------------------------------
if st.button("🚀 ICT 롱 타점 분석 실행", type="primary"):
if not api_key:
st.error("사이드바에 API Key를 입력하거나 Secrets에 등록해주세요!")
elif not images:
st.warning("분석할 미국주식 차트 이미지를 업로드해주세요!")
else:
with st.spinner("⚡ ICT 스마트머니(Sweep, FVG, OrderBlock) 분석 중..."):
try:
raw_text, used_model = call_gemini_ai(api_key, [SYSTEM_PROMPT] + images)

            # JSON 정제 및 파싱
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
            else:
                data = None

            st.success(f"분석 완료! (엔진: {used_model})")

            if data:
                # 1) 헤더 정보 카드
                st.markdown(f"""
                <div class="trade-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 13px; color: #94a3b8;">종목 및 타임프레임</span>
                            <h3 style="margin:0; color: #38bdf8 !important;">{data.get('ticker_info', 'US Stock')}</h3>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: rgba(16,185,129,0.2); color: #10b981; padding: 6px 14px; border-radius: 20px; font-weight: 700;">
                                {data.get('ict_setup', 'BUY')}
                            </span>
                            <div style="font-size: 13px; color: #cbd5e1; margin-top: 6px;">{data.get('killzone_status', '')}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 2) 핵심 수치 4종 카드 (한눈에 확인)
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(f"""
                    <div class="metric-box-entry">
                        <div class="metric-label">🟢 매수 진입가 (Entry)</div>
                        <div class="metric-val" style="color: #10b981;">{data.get('entry', '-')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="metric-box-sl">
                        <div class="metric-label">🔴 손절가 (Stop Loss)</div>
                        <div class="metric-val" style="color: #ef4444;">{data.get('stop_loss', '-')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div class="metric-box-tp">
                        <div class="metric-label">🔵 1차 목표가 (TP1)</div>
                        <div class="metric-val" style="color: #3b82f6;">{data.get('tp1', '-')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c4:
                    st.markdown(f"""
                    <div class="metric-box-tp">
                        <div class="metric-label">🟣 2차 목표가 / 손익비</div>
                        <div class="metric-val" style="color: #a855f7;">{data.get('tp2', '-')} <span style="font-size:14px; color:#cbd5e1;">({data.get('risk_reward', '-')})</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # 3) ICT 분석 근거 및 무효화 조건
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("<div class='trade-card'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='color:#10b981 !important; margin-top:0;'>🧠 ICT 핵심 근거 (SMC Confluence)</h4>", unsafe_allow_html=True)
                    for r in data.get('ict_reasons', []):
                        st.markdown(f"• {r}")
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_b:
                    st.markdown("<div class='trade-card'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='color:#ef4444 !important; margin-top:0;'>🚨 손절 / 무효화 기준 (Invalidation)</h4>", unsafe_allow_html=True)
                    st.write(data.get('invalidation', '지정 손절가 이탈 시 즉시 손절'))
                    st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.markdown(raw_text)

        except Exception as e:
            st.error(f"분석 오류: {e}")
---------------------------------------------------------
8. 사이드바 대화창
---------------------------------------------------------
if api_key:
if "messages" not in st.session_state:
st.session_state.messages = []

for msg in st.session_state.messages:
    with st.sidebar.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.sidebar.chat_input("ICT / 종목 질문..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.sidebar.chat_message("user"):
        st.markdown(user_input)

    with st.sidebar.chat_message("assistant"):
        try:
            res_text, _ = call_gemini_ai(api_key, [f"{SYSTEM_PROMPT}\n\n질문: {user_input}"])
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
        except Exception as e:
            st.error(f"대화 오류: {e}")
