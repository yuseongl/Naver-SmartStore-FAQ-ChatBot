import uuid

import requests
import streamlit as st

st.set_page_config(page_title="Cox Chatbot", layout="wide")
st.title("🧠 Cox Chatbot")

# 고유 세션 ID (브라우저 탭마다 고유)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 이전 대화 이력 저장용
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 기존 대화 렌더링
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
question = st.chat_input("질문을 입력하세요:")

if question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # 메시지 전송
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # 스트리밍 요청
        with requests.post(
            "http://localhost:8000/ask/stream",
            json={"session_id": st.session_state.session_id, "question": question},
            stream=True,
        ) as response:
            if response.status_code != 200:
                message_placeholder.error("⚠️ 질문 처리 중 오류 발생")
            else:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        decoded = chunk.decode("utf-8")
                        full_response += decoded
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

    # 대화 기록 저장
    st.session_state.chat_history.append(
        {"role": "assistant", "content": full_response}
    )

# 사이드바 - 로그
st.sidebar.title("📜 로그 기록")
if st.sidebar.button("로그 불러오기"):
    logs = requests.get("http://localhost:8000/logs")
    if logs.status_code == 200:
        logs = logs.json()
        for log in logs:
            st.sidebar.markdown(f"**Q:** {log['question']}")
            st.sidebar.markdown(f"**A:** {log['ai_response']}")
            st.sidebar.markdown("---")
    else:
        st.sidebar.error("로그 조회 실패")

# Streamlit 앱을 실행하려면 터미널에서 다음 명령어를 사용하세요:
# streamlit run streamlit_app.py
# 이 앱은 FastAPI 서버가 실행 중이어야 합니다.
# FastAPI 서버를 실행하려면 터미널에서 다음 명령어를 사용하세요:
# uvicorn main:app --reload
# 이 명령어는 main.py 파일에 정의된 FastAPI 앱을 실행합니다.
# FastAPI 서버가 실행 중이어야 Streamlit 앱이 정상적으로 작동합니다.
# 이 앱은 사용자가 질문을 입력하고 AI의 답변과 참고 문서를 보여줍니다.
# 또한, 사이드바에서 로그를 조회할 수 있는 기능을 제공합니다.
# 이 앱은 FastAPI 서버와 통신하여 질문을 처리하고 로그를 조회합니다.
# Streamlit 앱은 사용자가 질문을 입력하고 AI의 답변과 참고 문서를 보여줍니다.
