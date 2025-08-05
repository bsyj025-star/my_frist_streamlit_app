import os
import streamlit as st
from openai import OpenAI
from datetime import datetime

# Streamlit 앱 페이지 설정
st.set_page_config(
    page_title="학생 심리 상담 챗봇",
    layout="wide",
    page_icon="🌱"
)

# CSS 스타일 추가
st.markdown("""
<style>
.chat-message.user {
    background-color: #f0f2f6;
    border-color: #bbb;
}
.chat-message.assistant {
    background-color: #e8f0fe;
    border-color: #4c9ced;
}
.sidebar .sidebar-content {
    background-color: #f8f9fa;
}
</style>
""", unsafe_allow_html=True)

# 메인 컨텐츠
st.title("🌱 마음의 정원 챗봇")
st.write("안녕하세요! 저는 당신의 이야기를 들어줄 마음의 정원 챗봇이에요. 편하게 이야기해주세요.")

# API 키 설정
@st.cache_data(show_spinner=False)
def load_api_key():
    return os.getenv("UPSTAGE_API_KEY")

api_key = load_api_key()

if not api_key:
    with st.sidebar:
        st.error("Upstage API 키가 설정되지 않았습니다")
        api_key_input = st.text_input("Upstage API Key", type="password", key="api_key")
        if api_key_input:
            os.environ["UPSTAGE_API_KEY"] = api_key_input
            api_key = api_key_input
        else:
            st.info("API 키를 입력해주세요. 환경 변수에 설정하거나 위 입력란에 입력해주세요.")
            st.stop()

# Upstage API 클라이언트 초기화
client = OpenAI(
    api_key=api_key,
    base_url="https://api.upstage.ai/v1"
)

# 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "너는 학생의 고민을 진심으로 듣고 공감해주는 친절하고 따뜻한 심리 상담가야. 편안한 분위기로 대화를 이끌어줘."},
        {"role": "assistant", "content": "안녕! 힘든 일이 있었구나. 괜찮아, 여기엔 뭐든지 편하게 말해도 돼. 내가 옆에 있을게."}
    ]

# 대화 기록 표시
st.markdown("### 🗣 대화 기록")
chat_placeholder = st.empty()
with chat_placeholder.container():
    for i, msg in enumerate(st.session_state.chat_history):
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            st.markdown(f"<small style='color:gray;'>{datetime.fromtimestamp(i/2).strftime('%H:%M')}</small>", unsafe_allow_html=True)

# 사용자 입력 처리
prompt = st.chat_input("여기에 당신의 이야기를 입력해주세요.", key="input")
if prompt:
    # 사용자 메시지 추가
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
        st.markdown(f"<small style='color:gray;'>{datetime.now().strftime('%H:%M')}</small>", unsafe_allow_html=True)

    # 챗봇 응답 생성
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            # 시스템 메시지 제외한 대화 기록 전달
            conversation = [msg for msg in st.session_state.chat_history if msg["role"] != "system"]

            for chunk in client.chat.completions.create(
                model="solar-pro2",
                messages=conversation,
                stream=True,
            ):
                delta = chunk.choices[0].delta.get('content', '')
                full_response += delta
                response_placeholder.markdown(full_response + "▌")

            # 최종 응답 표시
            response_placeholder.markdown(full_response)
            st.markdown(f"<small style='color:gray;'>{datetime.now().strftime('%H:%M')}</small>", unsafe_allow_html=True)

            # 대화 기록 저장
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.session_state.chat_history.append({"role": "assistant", "content": "미안, 지금은 답변하기가 어렵네. 잠시 후 다시 시도해볼래?"})

# 사이드바
with st.sidebar:
    st.header("정보")
    st.markdown("""
    **마음의 정원 챗봇**
    - **개발 목적**: 학생들의 심리적 고민을 돕기 위해
    - **사용 모델**: Upstage.ai의 SOLAR-PRO2
    - **특징**: 따뜻하고 공감하는 대화 스타일

    ---

    ### 🛠 설정
    """)

    # 대화 내보내기 기능
    if st.button("대화 내보내기"):
        export_text = "\n".join([f"[{msg['role'].upper()}] {msg['content']}" for msg in st.session_state.chat_history if msg["role"] != "system"])
        st.download_button(
            "대화 내용 다운로드",
            export_text,
            file_name=f"상담기록_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

    # 대화 초기화 버튼
    if st.button("대화 초기화", key="reset"):
        st.session_state.chat_history = [
            {"role": "system", "content": "너는 학생의 고민을 진심으로 듣고 공감해주는 친절하고 따뜻한 심리 상담가야. 편안한 분위기로 대화를 이끌어줘."},
            {"role": "assistant", "content": "안녕! 다시 시작한 우리의 대화. 무엇을 이야기해볼까요?"}
        ]
        st.experimental_rerun()

    # 현재 API 키 표시 (마스킹 처리)
    st.markdown("---")
    st.markdown("**API 키 상태**: 설정됨 (마지막 4자리: `****" + api_key[-4:] + "`")")
