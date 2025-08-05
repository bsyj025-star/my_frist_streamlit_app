import os
import streamlit as st
from openai import OpenAI

# Streamlit 앱 페이지 설정
st.set_page_config(page_title="학생 심리 상담 챗봇", layout="wide")
st.title("🌱 마음의 정원 챗봇")
st.write("안녕하세요! 저는 당신의 이야기를 들어줄 마음의 정원 챗봇이에요. 편하게 이야기해주세요.")

# 보안을 위해 환경 변수에서 API 키를 불러옵니다.
api_key = os.getenv("")

if not api_key:
    # API 키가 설정되지 않았을 경우 사용자에게 입력하도록 안내
    st.error("Upstage API 키를 환경 변수에 설정하거나, 사이드바에 입력해주세요.")
    with st.sidebar:
        api_key_input = st.text_input("Upstage API Key", type="password")
        if api_key_input:
            api_key = api_key_input
            
        else:
            st.info("API 키를 입력해주세요.")
            st.stop() # 키가 없으면 앱 실행 중단

# Upstage API 클라이언트 초기화
client = OpenAI(
    api_key=api_key,
    base_url="https://api.upstage.ai/v1"
)

# 세션 상태(session_state)에 대화 기록이 없으면 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "너는 학생의 고민을 진심으로 듣고 공감해주는 친절하고 따뜻한 심리 상담가야. 편안한 분위기로 대화를 이끌어줘."},
        {"role": "assistant", "content": "안녕! 힘든 일이 있었구나. 괜찮아, 여기선 뭐든지 편하게 이야기해도 돼. 내가 옆에 있어줄게."}
    ]

# 대화 기록을 화면에 표시
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("여기에 당신의 이야기를 입력해주세요."):
    # 사용자의 메시지를 대화 기록에 추가하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 챗봇 응답 생성 및 표시
    with st.chat_message("assistant"):
        # 메시지 히스토리에서 "system" 역할 메시지를 제외하고 전달
        response_messages = [msg for msg in st.session_state.messages if msg["role"] != "system"]
        
        try:
            stream = client.chat.completions.create(
                model="solar-pro2",
                messages=response_messages,
                stream=True,
            )
            # 스트리밍 응답을 위한 컨테이너 생성
            response = st.write_stream(stream)
            
            # 전체 응답을 대화 기록에 추가
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.session_state.messages.append({"role": "assistant", "content": "미안, 지금은 답변하기가 어렵네. 잠시 후 다시 시도해볼래?"})

# 사이드바에 추가 정보 표시
with st.sidebar:
    st.header("정보")
    st.markdown("""
    **마음의 정원 챗봇**
    - **개발 목적**: 학생들의 심리적 고민을 돕기 위해
    - **사용 모델**: Upstage.ai의 SOLAR-PRO2
    - **특징**: 따뜻하고 공감하는 대화 스타일
    
    ---
    
    ### 주의사항
    이 챗봇은 전문 심리 상담가를 대체할 수 없습니다. 
    만약 심각한 어려움이 있다면, 반드시 전문가의 도움을 받으세요.
    
    """)
    st.text_area("대화 내용", value='\n'.join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]), height=300)