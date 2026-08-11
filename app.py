import streamlit as st
import google.generativeai as genai
from PIL import Image

# ---------------------------------------------------------
# 1. 트레이딩뷰 다크모드 프로 터미널 커스텀 CSS (UI 업그레이드)
# ---------------------------------------------------------
st.set_page_config(
    page_title="ICT Pro Trading Terminal", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 메인 배경 및 폰트 설정 */
    .stApp {
        background-color: #131722;
        color: #d1d4dc;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
    
    /* 헤더 스타일링 */
    h1, h2, h3 {
        color: #f0f3fa !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* 사이드바 스타일링 */
    section[data-testid="stSidebar"] {
        background-color: #1e222d !important;
        border-right: 1px solid #2a2e39;
    }
    
    /* 버튼 커스텀 (트레이딩뷰 롱 녹색 Glow 효과) */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #089981 0%, #26a69a 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(38, 166, 154, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(38, 166, 154, 0.6);
    }
    
    /* 탭 디자인 커스텀 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e222d;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #2a2e39;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 6px;
        color: #787b86;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2a2e39 !important;
        color: #2962ff !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 로그인 및 보안 시스템
# ---------------------------------------------------------
MY_PASSWORD = "1234"  # 원하는 비밀번호로 변경 가능

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 ICT PRO TERMINAL LOGIN</h2>", unsafe_allow_html=True)
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
# 3. 4-Timeframe 초정밀 ICT 비전 시스템 프롬프트
# ---------------------------------------------------------
SYSTEM_PROMPT = """
[Role & Identity]
당신은 ICT(Inner Circle Trader) 및 SMC(Smart Money Concepts) 이론에 입각한 '미국 급등주/단타 롱(Long/매수) 전용 멀티 타임프레임(1시간/15분/5분/1분봉) 비전 분석 엔진'입니다.
사용자는 한국(KST) 거주 트레이더이며 오직 롱(Long) 포지션만 매매합니다. 숏(Short) 분석은 절대 배제하고, 상위 시간대의 세력 목표부터 하위 시간대의 스나이퍼 진입까지 시각적으로 교차 검증하여 승률 높은 타점만 산출하세요.

[Image Vision Analysis Guidelines - 차트 시각 판독 수칙]
업로드된 차트 이미지를 시각적으로 판독할 때 아래 5가지 요소를 명확히 찾으세요:
1. 차트상의 봉 단위 타임프레임(1시간/15분/5분/1분봉) 식별.
2. 주요 저점 밑으로 캔들 밑꼬리(Wick)가 내려갔다가 즉시 말아 올려 개미를 털었는지 여부 (SSL Sweep 포착).
3. 스윕 직후 강한 양봉이 터지며 직전 고점을 종가로 돌파했는지 여부 (MSS: 상승 구조 전환).
4. 상승 파동 도중 발생한 3개 캔들 간 비효율 빈 공간 (Bullish FVG: 1번 캔들 고점 ~ 3번 캔들 저점 사이) 범위 추출.
5. 5분봉 FVG와 1분봉 FVG가 중첩(Confluence)되는 최적의 매수 구간 정밀 계산.

[Timezone & Kill Zone Rules (KST Base)]
- 서머타임 기간 (3월~11월): 🔥 NY Open Kill Zone (22:30 ~ 24:00 KST) / 🌙 PM Kill Zone (02:30 ~ 04:00 KST)
- 서머타임 해제 기간 (11월~3월): 🔥 NY Open Kill Zone (23:30 ~ 01:00 KST) / 🌙 PM Kill Zone (03:30 ~ 05:00 KST)

[Output Format]
반드시 아래 양식으로만 답변하세요:

---------------------------------------------------
[⚡ ICT 4-Timeframe Long Trade Plan]

1. 🧭 시장 맥락 및 킬존 (KST)
   - 업로드 차트: [시각 판독된 타임프레임 및 종목명]
   - 킬존 판정: [NY Open 킬존 / PM 킬존 / 킬존 외 (주의 경고)]
   - HTF 1시간봉/15분봉 맥락: [매수 Bias 여부 및 지지선 위치]

2. 🔍 다중 시간대 ICT 구조 교차 검증 (Vision Analysis)
   - SSL 저점 스윕 (15분/5분): [개미 털기 꼬리 저점 가격 및 형성 위치]
   - MSS 상승 구조 전환 (5분/1분): [돌파된 직전 스윙 고점 가격]
   - Confluence 매수 갭: [5분봉 FVG와 1분봉 FVG가 중첩되는 핵심 지지 가격대]

3. 🎯 실전 롱 매매 타점 (Long Setup Execution)
   - 🟢 진입가 (Entry): [중첩 FVG 중단 또는 OTE 0.618~0.786 디스카운트 가격]
   - 🔴 손절가 (Stop Loss): [SSL 스윕 꼬리 끝 지점 바로 밑 - $0.05~$0.10 여유]
   - 🔵 1차 익절가 (TP1): [직전 스윙 고점 BSL]
   - 🟣 2차 익절가 (TP2): [1시간봉 상위 유동성 BSL 또는 손익비 1:3 지점]
   - 📐 손익비 (Risk to Reward): [예: 1 : 2.8]

4. 🚨 진입 취소 및 무효화 조건 (Invalidation)
   - [FVG 하단 종가 이탈 시, 킬존 시간 종료 시, 거래량 이탈 시 진입 취소]
---------------------------------------------------

[Strict Trading Rules]
- 숏(Short) 포지션 절대 추천 금지.
- 저점 스윕(SSL Sweep) 흔적이 없는 무지성 급등 차트는 "진입 불가(No Trade)"로 처리.
- 손익비(Risk to Reward)가 최소 1:2 미만인 자리는 진입 자제 권고.
"""

# ---------------------------------------------------------
# 4. 동적 AI 모델 탐색 및 호출 함수 (404 완벽 방지)
# ---------------------------------------------------------
def call_gemini_ai(api_key, contents):
    genai.configure(api_key=api_key)
    
    # 최신 규격 모델 1차 탐색 리스트
    primary_models = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]
    
    errors = []
    
    # 1. 최신 지정 모델 호출 시도
    for model_name in primary_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(contents)
            return response.text, model_name
        except Exception as e:
            errors.append(f"[{model_name}]: {e}")
            continue

    # 2. 지정 모델 모두 실패 시, 계정에서 지원하는 모델 목록을 동적으로 가져와 2차 시도
    try:
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        for model_name in available_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(contents)
                return response.text, model_name
            except Exception as e:
                errors.append(f"[{model_name}]: {e}")
                continue
    except Exception as list_err:
        errors.append(f"[list_models]: {list_err}")

    # 최종 실패 시 상세 원인 안내
    raise Exception(f"사용 가능한 Gemini 모델을 찾을 수 없습니다. (API Key 확인 필요)\n상세 에러:\n" + "\n".join(errors[:2]))

# ---------------------------------------------------------
# 5. 사이드바 API 키 자동 감지 (Secrets 지원)
# ---------------------------------------------------------
st.sidebar.markdown("## ⚙️ TERMINAL SETTINGS")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("🔑 API Key 자동 연결됨")
else:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Google AI Studio의 API 키를 입력하세요.")

st.sidebar.markdown("---")
st.sidebar.markdown("## 💬 LIVE AI CONSULTING")

# ---------------------------------------------------------
# 6. 메인 화면 - 4개 타임프레임 멀티 업로더 UI
# ---------------------------------------------------------
st.markdown("<h1 style='color: #2962ff !important;'>⚡ ICT MULTI-TIMEFRAME TERMINAL</h1>", unsafe_allow_html=True)
st.caption("1시간봉 / 15분봉 / 5분봉 / 1분봉 차트를 업로드하면 4중 분석으로 최고 승률의 롱 타점을 계산합니다.")

tab1, tab2, tab3, tab4 = st.tabs(["📊 1시간봉 (HTF)", "📈 15분봉 (MTF)", "📉 5분봉 (MTF)", "🎯 1분봉 (LTF)"])

img_1h, img_15m, img_5m, img_1m = None, None, None, None

with tab1:
    f_1h = st.file_uploader("1시간봉 차트 이미지", type=["png", "jpg", "jpeg"], key="1h")
    if f_1h: img_1h = Image.open(f_1h); st.image(img_1h, use_container_width=True)

with tab2:
    f_15m = st.file_uploader("15분봉 차트 이미지", type=["png", "jpg", "jpeg"], key="15m")
    if f_15m: img_15m = Image.open(f_15m); st.image(img_15m, use_container_width=True)

with tab3:
    f_5m = st.file_uploader("5분봉 차트 이미지", type=["png", "jpg", "jpeg"], key="5m")
    if f_5m: img_5m = Image.open(f_5m); st.image(img_5m, use_container_width=True)

with tab4:
    f_1m = st.file_uploader("1분봉 차트 이미지", type=["png", "jpg", "jpeg"], key="1m")
    if f_1m: img_1m = Image.open(f_1m); st.image(img_1m, use_container_width=True)

st.markdown("---")

uploaded_images = [img for img in [img_1h, img_15m, img_5m, img_1m] if img is not None]

if st.button("🚀 ICT 4-TIMEFRAME 롱 타점 정밀 분석 실행", type="primary"):
    if not api_key:
        st.error("👈 사이드바에 Gemini API Key를 입력하거나 Secrets에 등록해 주세요!")
    elif not uploaded_images:
        st.warning("최소 1개 이상의 차트 이미지를 업로드해 주세요!")
    else:
        with st.spinner("AI 비전 엔진이 4개 타임프레임을 교차 분석 중..."):
            try:
                contents = [SYSTEM_PROMPT] + uploaded_images
                result_text, used_model = call_gemini_ai(api_key, contents)
                st.success(f"분석 완료! (연결된 모델: {used_model})")
                st.markdown(result_text)
            except Exception as e:
                st.error(f"분석 오류: {e}")

# ---------------------------------------------------------
# 7. 실시간 사이드바 대화 (404 완벽 방지)
# ---------------------------------------------------------
if api_key:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.sidebar.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.sidebar.chat_input("타점 수정/질문 입력..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.sidebar.chat_message("user"):
            st.markdown(user_input)

        with st.sidebar.chat_message("assistant"):
            try:
                chat_prompt = f"{SYSTEM_PROMPT}\n\n사용자 질문: {user_input}"
                res_text, _ = call_gemini_ai(api_key, [chat_prompt])
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
            except Exception as e:
                st.error(f"대화 오류: {e}")
