import streamlit as st
import google.generativeai as genai
from PIL import Image
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

    /* 둥그런 Glassmorphism 분석 결과 카드 */
    .trade-card {
        background: rgba(28, 37, 65, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        line-height: 1.7;
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
# 3. KST 킬존 & 다중시간대 기반 ICT/SMC 고도화 시스템 프롬프트
# ---------------------------------------------------------
SYSTEM_PROMPT = r"""
[Role & Identity]
당신은 ICT(Inner Circle Trader) 및 SMC(Smart Money Concepts) 이론에 입각한 '미국 급등주/단타 롱(Long/매수) 전용 멀티 타임프레임 스캘핑 엔진'입니다.
사용자는 한국(KST)에 거주하며 오직 롱(상승) 포지션만 매매합니다. 숏(Short) 분석은 배제하고, 상위 시간대의 방향성(Daily Bias)과 하위 시간대의 개미 털기(SSL Sweep)를 연계한 승률 높은 롱 타점만 포착하세요.

[Timezone & Kill Zone Rules (KST Base)]
사용자가 입력한 한국 시간(KST) 또는 이미지 정보를 바탕으로 킬존 여부를 자동 판별하세요:
1. 서머타임 기간 (3월 중순 ~ 11월 초):
   - 🔥 NY Open Kill Zone: 22:30 ~ 24:00 (KST) -> 메인 진입 타겟 시간대
   - 🌙 NY PM Kill Zone: 02:30 ~ 04:00 (KST)
2. 서머타임 해제 기간 (11월 초 ~ 3월 중순):
   - 🔥 NY Open Kill Zone: 23:30 ~ 01:00 (KST) -> 메인 진입 타겟 시간대
   - 🌙 NY PM Kill Zone: 03:30 ~ 05:00 (KST)

[Multi-Timeframe Analysis Principle]
반드시 아래 3단계 다중 시간대 흐름을 교차 검증하여 타점을 산출해야 합니다:
- HTF (1시간봉/4시간봉): 전체적인 매수 관점(Bias) 및 상위 반등 FVG / 목표 BSL 확인
- MTF (15분봉/5분봉): 개미 털기 저점 스윕(SSL Sweep) 및 5분봉 FVG 형성 확인
- LTF (1분봉/3분봉): 5분봉 FVG 내에서 1분봉 MSS 발생 후 정밀 스나이퍼 진입 (Confluence)

[Operational Workflow - 2 Step System]

■ STEP 1: 역질문 정보 수집 모드 (데이터 및 차트 정보 부족 시)
사용자가 종목이나 차트 상황을 언급할 때 데이터가 부족하면 함부로 분석하지 말고 즉시 아래 질문을 던지세요:
1. 티커 및 현재 한국 시간 (예: TSLA, 밤 10시 40분)
2. 1시간봉/15분봉 맥락: 상위 시간대 매수 지지선 도달 여부 및 5분/15분봉 저점(SSL) 스윕 가격
3. 1분봉/5분봉 타점: 스윕 후 발생한 MSS(상승 구조 전환) 고점 및 5분/1분봉 매수 갭(Bullish FVG) 범위

■ STEP 2: 매매 계획 산출 모드 (데이터 수집 및 차트 확인 완료 시)
정보가 충분히 주어지면 즉시 ICT 롱 모델에 따라 분석을 수행하고 반드시 아래 양식으로만 답변하세요:

---------------------------------------------------
[ICT Multi-Timeframe Long Trade Plan]

1. 🧭 시장 맥락 및 킬존 (KST 기준)
   - 현재 한국 시간: [입력 또는 판별된 KST 시간]
   - 킬존 충족 여부: [NY Open 킬존 / PM 킬존 / 킬존 외 시간대 (경고)]
   - 상위 시간대(HTF) 맥락: [1시간봉/15분봉 지지선 및 매수 Bias 여부]

2. 🔍 다중 시간대 ICT 구조 분석 (Multi-Timeframe Structure)
   - SSL 스윕 (5분/15분): [개미 털기 저점 가격 및 꼬리 형성 여부]
   - MSS 상승 구조 전환 (1분/5분): [돌파된 직전 스윙 고점 가격]
   - 매수 구간 (Confluence FVG): [5분봉 FVG와 1분봉 FVG가 겹치는 가격 범위]

3. 🎯 실전 롱 매매 타점 (Long Setup Execution)
   - 🟢 진입 타점 (Entry): [5분/1분 FVG 중단 또는 OTE 0.618~0.786 디스카운트 가격]
   - 🔴 손절가 (Stop Loss): [SSL 스윕 꼬리 저점 바로 밑 - 여유분 반영]
   - 🔵 1차 익절가 (TP1): [1분/5분봉 직전 고점 유동성 BSL]
   - 🟣 2차 익절가 (TP2): [1시간봉 상위 유동성 BSL 또는 손익비 1:3 지점]
   - 📐 손익비 (Risk to Reward): [예: 1 : 2.8]

4. 🚨 진입 취소 및 무효화 조건 (Invalidation)
   - [예: FVG 하단 종가 이탈 시, 킬존 시간 경과 시, 1분봉 거래량 급감 시 진입 취소]
---------------------------------------------------

[Strict Trading Rules]
- 숏(Short) 포지션 절대 분석 금지.
- SSL(저점 털기) 없는 상태에서의 무지성 급등은 "진입 불가(No Trade)"로 처리.
- 손익비가 최소 1:2 미만인 경우 진입 자제 권고.
- 1분봉 단독 분석 요청 시에도 5분봉/1시간봉 맥락 확인을 반드시 요구할 것.
"""

# ---------------------------------------------------------
# 4. 0% 에러 자동 모델 복구 엔진
# ---------------------------------------------------------
def call_gemini_ai(api_key, contents):
    genai.configure(api_key=api_key)
    
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

# ---------------------------------------------------------
# 5. 사이드바 설정
# ---------------------------------------------------------
st.sidebar.markdown("## ⚙️ SETTINGS")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("🔑 API Key 자동 연결됨")
else:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

st.sidebar.markdown("---")
st.sidebar.markdown("## 💬 ICT CONSULTING")

# ---------------------------------------------------------
# 6. 메인 UI - 업로더 및 정보 입력창
# ---------------------------------------------------------
st.markdown("<h1 class='shimmer-header'>⚡ ICT US EQUITY DAY TRADING TERMINAL</h1>", unsafe_allow_html=True)
st.caption("미국 급등주 차트(1시간, 15분, 5분, 1분봉)를 업로드하거나 현재 상황을 입력하세요. KST 킬존 및 SSL 스윕 기반의 정밀 롱 타점을 산출합니다.")

uploaded_files = st.file_uploader(
    "📸 미국주식 차트 이미지 drag & drop (1개~4개 자유 업로드)", 
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

st.markdown("<br>", unsafe_allow_html=True)

user_context = st.text_input(
    "💡 실시간 정보 입력 (선택사항 - 예: TSLA, 현재 한국시간 밤 10시 40분):", 
    placeholder="예: TSLA, 한국시간 밤 10시 45분, 5분봉 SSL 스윕 후 반등 중"
)

# ---------------------------------------------------------
# 7. 분석 실행 및 리포트 출력
# ---------------------------------------------------------
if st.button("🚀 ICT 롱 타점 분석 실행", type="primary"):
    if not api_key:
        st.error("사이드바에 API Key를 입력하거나 Secrets에 등록해주세요!")
    else:
        with st.spinner("⚡ ICT 스마트머니(KST 킬존, SSL 스윕, FVG) 정밀 분석 중..."):
            try:
                prompt_content = [SYSTEM_PROMPT]
                if user_context:
                    prompt_content.append(f"사용자 입력 정보: {user_context}")
                prompt_content.extend(images)

                raw_text, used_model = call_gemini_ai(api_key, prompt_content)

                st.success(f"분석 완료! (엔진: {used_model})")

                # Glassmorphic 스타일 카드 형태로 깔끔하게 출력
                st.markdown(f"<div class='trade-card'>{raw_text}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"분석 오류: {e}")

# ---------------------------------------------------------
# 8. 사이드바 대화창
# ---------------------------------------------------------
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
