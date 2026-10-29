import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from task2_rag.rag_pipeline import DATA_DIR, build_vectorstore, stream_answer

st.set_page_config(page_title="Document Chatbot", page_icon="💬")
st.title("💬 Document Q&A Chatbot")


@st.cache_resource(show_spinner="Sənədlər indekslənir...")
def get_store():
    return build_vectorstore()


with st.sidebar:
    st.header("Sənəd əlavə et")
    uploaded = st.file_uploader("PDF yüklə", type=["pdf"])
    if uploaded and st.button("İndeksə əlavə et"):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / uploaded.name).write_bytes(uploaded.getbuffer())
        get_store.clear()
        build_vectorstore(rebuild=True)
        st.success("Yeniləndi!")
    if st.button("Söhbəti təmizlə"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            with st.expander("Mənbələr"):
                st.write("\n".join(f"- {s}" for s in m["sources"]))

if question := st.chat_input("Sənəd haqqında sual ver..."):
    history = "\n".join(
        f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]
    )
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            gen, sources = stream_answer(question, get_store(), history)
            full = st.write_stream(gen)
        except Exception as e:
            st.error(f"Xəta: {e}. Bir az gözləyib yenidən cəhd et.")
            st.stop()
        with st.expander("Mənbələr"):
            st.write("\n".join(f"- {s}" for s in sources))

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append(
        {"role": "assistant", "content": full, "sources": sources}
    )