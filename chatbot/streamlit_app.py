import streamlit as st
from bedrock_client import BedrockChatbot

# 페이지 설정
st.set_page_config(
    page_title="Bedrock 챗봇",
    page_icon="🤖",
    layout="wide"
)

# 제목
st.title("🤖 엔트리 파이썬 RAG 챗봇")
st.markdown("**Knowledge Base**: 9R38KN62YH")

# 챗봇 초기화
@st.cache_resource
def init_chatbot():
    return BedrockChatbot()

chatbot = init_chatbot()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 챗봇 응답
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            response = chatbot.chat(prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# 사이드바
with st.sidebar:
    st.header("설정")
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("**모델**: Claude Sonnet 4 🚀")
    st.markdown("**Knowledge Base**: 9R38KN62YH")
    st.markdown("**기능**: RAG (검색 증강 생성)")
    st.markdown("**제공**: Amazon Bedrock")