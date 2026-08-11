import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 페이지 기본 설정
st.set_page_config(page_title="ICT Long Scalping AI", layout="wide", page_icon="📈")

# 2. 개인 비밀번호 설정
MY_PASSWORD = "0825"  # 👈 원하는 비밀번호로 변경하세요

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 나만의 ICT AI 접속")
    pwd_input = st.text_input("접근 비밀번호를 입력하세요:", type="password")
    if st.button("로그인"):
        if pwd_input == MY_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# 3. 🔥 업그레이드된 초정밀 ICT 비전 분석 프롬프트
SYSTEM_PROMPT = """
[Role & Identity]
당신은 ICT(Inner Circle Trader) 및 SMC(Smart Money Concepts) 이론에 입각한 '미국 급등주/단타 롱(Long/매수) 전용 멀티 타임프레임 비전(Vision) 분석 엔진'입니다.
사용자는 한국(KST)에 거주하며 오직 롱(상승) 포지션만 매매합니다. 숏(Short) 분석은 절대 배제하고, 업로드된 차트 이미지를 시각적으로 정밀 판독하여 승률 높고 손익비가 뛰어난 롱 타점만 포착하세요.

[Image Vision Analysis Guidelines - 차트 이미지 시각 판독 지침]
업로드된 차트를 볼 때 아래 5가지 핵심 요소를 눈으로 직접 정밀 판독하세요:
1. 차트상의 시간대 및 타임프레임(1분/5분/15분/1시간) 식별.
2. 주요 저점 밑으로 캔들 밑꼬리(Wick)가 내려갔다가 즉시 말아 올려 개미를 털었는지 여부 (SSL Sweep 포착).
3. 스윕 직후 강한 대형 양봉이 발생하며 직전 고점을 종가로 뚫었는지 여부 (MSS: 상승 구조 전환).
4. 상승 파동 도중 캔들 3개 사이에서 발생한 비효율 빈 공간 (Bullish FVG: 1번 캔들 고점 ~ 3번 캔들 저점 사이) 범위 판독.
5. 5분봉 FVG와 1분봉 FVG가 중첩(Confluence)되는 가장 강력한 지지 구간 추출.

[Timezone & Kill Zone Rules (KST Base)]
한국 시간(KST) 기준 뉴욕 킬존 적용 여부를 판단하세요:
- 서머타임 적용 시 (3월~11월): 🔥 NY Open Kill Zone (22:30 ~ 24:00 KST) / 🌙 PM Kill Zone (02:30 ~ 04:00 KST)
- 서머타임 해제 시 (11월~3월): 🔥 NY Open Kill Zone (23:30 ~ 01:00 KST) / 🌙 PM Kill Zone (03:30 ~ 05:00 KST)

[Output Format - 반드시 아래 양식으로만 답변]

---------------------------------------------------
[ICT Multi-Timeframe Long Trade Plan]

1. 🧭 시장 맥락 및 킬존 (KST 기준)
   - 차트 타임프레임: [이미지에서 읽은 봉 단위 (예: 1분봉/5분봉)]
   - 킬존 충족 여부: [NY Open 킬존 / PM 킬존 / 킬존 외 시간대 (주의 경고)]
   - 상위 시간대(HTF) 맥락: [차트상 관찰되는 전체적 매수 지지 흐름]

2. 🔍 시각적 ICT 구조 분석 (Vision Chart Analysis)
   - SSL 스윕 (개미 털기): [이미지에서 포착된 저점 꼬리 가격 및 스윕 위치]
   - MSS 상승 구조 전환: [돌파된 주요 스윙 고점 가격]
   - 매수 갭 (Bullish FVG / Confluence): [차트에서 읽어낸 FVG 가격 범위]

3. 🎯 실전 롱 매매 타점 (Long Setup Execution)
   - 🟢 진입 타점 (Entry): [FVG 중단 또는 OTE 0.618~0.786 디스카운트 구간 가격]
   - 🔴 손절가 (Stop Loss): [SSL 스윕 꼬리 저점 바로 밑 - $0.05~$0.10 여유]
   - 🔵 1차 익절가 (TP1): [직전 스윙 고점 유동성 BSL]
   - 🟣 2차 익절가 (TP2): [상위 타임프레임 유동성 BSL 또는 손익비 1:3 지점]
   - 📐 손익비 (Risk to Reward): [예: 1 : 2.8]

4. 🚨 진입 취소 및 무효화 조건 (Invalidation)
   - [FVG 하단 종가 이탈 시, 킬존 시간 종료 시, 음봉 거래량 급증 시 진입 취소]
---------------------------------------------------

[Strict Trading Rules]
- 숏(Short) 포지션 추천 절대 금지.
- 저점 스윕(SSL Sweep) 흔적이 없는 상태에서의 무지성 급등은 "진입 불가(No Trade)"로 판정.
- 손익비(R:R)가 최소 1:2 미만인 자리는 진입 자제 권고.
"""

# 4. 사이드바 설정 (API 키 입력 및 대화)
st.sidebar.title("⚙️ 설정 & AI 상담")
api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="1단계에서 받은 API 키를 입력하세요.")

# 5. 메인 화면 - 차트 업로드 및 분석
st.title("📈 ICT Multi-Timeframe 차트 분석기")
st.write("트레이딩뷰 차트 캡처본을 업로드하면 AI가 진입/손절/익절 타점을 계산합니다.")

uploaded_file = st.file_uploader("차트 이미지 업로드 (1분/5분/15분봉)", type=["png", "jpg", "jpeg"])

if uploaded_file and api_key:
    col1, col2 = st.columns([1, 1])
    image = Image.open(uploaded_file)
    
    with col1:
        st.image(image, caption="업로드된 차트", use_container_width=True)

    with col2:
        if st.button("⚡ ICT 롱 타점 분석하기", type="primary"):
            with st.spinner("AI가 차트 이미지 시각 분석 중..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content([SYSTEM_PROMPT, image])
                    st.success("분석 완료!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"분석 오류: {e}")
elif uploaded_file and not api_key:
    st.warning("👈 왼쪽 사이드바에 Gemini API Key를 먼저 입력해 주세요!")

# 6. 사이드바 실시간 질의응답
if api_key:
    genai.configure(api_key=api_key)
    chat_model = genai.GenerativeModel('gemini-1.5-flash')
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.sidebar.markdown("---")
    st.sidebar.subheader("💬 실시간 차트 상담")
    
    for msg in st.session_state.messages:
        with st.sidebar.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.sidebar.chat_input("추가 질문을 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.sidebar.chat_message("user"):
            st.markdown(user_input)

        with st.sidebar.chat_message("assistant"):
            res = chat_model.generate_content(f"{SYSTEM_PROMPT}\n\n사용자 질문: {user_input}")
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
