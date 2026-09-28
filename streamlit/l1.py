import streamlit as st

st.title("WinDiag AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


prompt = st.chat_input("Describe your Windows problem...")

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    response = f"You said: {prompt}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.rerun()