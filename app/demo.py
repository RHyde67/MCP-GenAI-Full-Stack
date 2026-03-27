import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

import streamlit as st
from mcp_client import call
import asyncio
import os
import requests
from config.settings import settings

def safe_call(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Already inside a running event loop → use create_task + wait
        future = asyncio.ensure_future(coro)
        return asyncio.get_event_loop().run_until_complete(future)
    else:
        # Normal case
        return asyncio.run(coro)
    
# ---------------------------------------------------------
# App Screens Setup
# ---------------------------------------------------------
@st.dialog(" Current Documents")
def show_documents_dialog(docs):
    st.write("## Documents in VDB")
    for d in docs:
        st.write(f"- {d}")


# ---------------------------------------------------------
# STREAMLIT PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(page_title="RAG Demo", layout="wide")
st.title("📘 RAG Demo Application")


# ---------------------------------------------------------
# SIDEBAR: MODE + ACTIONS
# ---------------------------------------------------------
st.sidebar.header("Query Mode")
mode = st.sidebar.radio(
    "Choose how to run queries:",
    ("Simple RAG (rag_answer)", "Context Chat (rag_chat_stateful)")
)

st.sidebar.divider()
# ------------------------------------------
# LLM MODE TOGGLE (Local / Remote)
# ------------------------------------------
st.sidebar.subheader("LLM Selection")

llm_choice = st.sidebar.radio(
    "Choose LLM:",
    ("Local (Ollama)", "Remote Server"),
    index=0 if settings.LLM_MODE == "local" else 1
)

# Update mode when user switches
if llm_choice.startswith("Local"):
    settings.update_llm_mode("local")
else:
    settings.update_llm_mode("remote")

st.sidebar.write(f"✅ Active LLM: **{settings.LLM_MODE.upper()}**")
st.sidebar.write(f"📡 Endpoint: `{settings.LLM_BASE_URL}`")

st.sidebar.header("Document Controls")

if st.sidebar.button(" List Documents"):
    docs = safe_call(call("vdb_list_documents"))
    show_documents_dialog(docs.data["documents"])

if st.sidebar.button(" Add Document"):
    st.session_state["show_add_modal"] = True

if st.sidebar.button(" Update Document"):
    st.session_state["show_update_modal"] = True

if st.sidebar.button("🗑 Delete Document"):
    st.session_state["show_delete_modal"] = True

st.sidebar.divider()

if st.sidebar.button(" Clear Chat History"):
    safe_call(call("reset_chat_memory"))
    st.sidebar.success("Chat history cleared.")


# ---------------------------------------------------------
# MAIN QUERY AREA
# ---------------------------------------------------------
st.subheader("Enter your query")
query = st.text_area("Query:", height=120)

if st.button("Run Query"):
    if mode == "Simple RAG (rag_answer)":
        response = safe_call(call("rag_answer", {"query": query}))

        st.write("###  Response")
        st.write(response.data["answer"])

        st.write("###  Citations")
        for c in response.data["chunks_used"]:
            st.write("- ", c[:200], "...")

    else:
        response = safe_call(call("rag_chat_stateful", {"user_message": query}))

        st.write("###  Response")
        st.write(response.data["reply"])

        st.write("###  Citations")
        for c in response.data["chunks_used"]:
            st.write("- ", c[:200], "...")


# ---------------------------------------------------------
# MODAL: ADD DOCUMENT (with overwrite warning)
# ---------------------------------------------------------
if st.sidebar.button(" Add Document", key="open_add_doc"):
    st.session_state["show_add_modal"] = True
    st.session_state.pop("confirm_overwrite", None)  # reset overwrite state

if st.session_state.get("show_add_modal", False):
    st.write("##  Add Document")

    uploaded = st.file_uploader(
        "Select .docx file",
        type=["docx"],
        key="add_doc_uploader"
    )

    if uploaded:

        # Load current documents to check if filename already exists
        docs_result = safe_call(call("vdb_list_documents"))
        existing_docs = docs_result.data["documents"]

        filename = uploaded.name

        # Does document already exist?
        if filename in existing_docs and "confirm_overwrite" not in st.session_state:
            st.warning(
                f"⚠️ A document named **'{filename}'** already exists.\n\n"
                "Do you want to overwrite it or update it?\n"
                "- ✅ Yes: Overwrite the document\n"
                "- ❌ No: Cancel and use the Update Document tool instead"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Overwrite"):
                    st.session_state["confirm_overwrite"] = True
            with col2:
                if st.button("❌ No, Cancel"):
                    st.session_state["show_add_modal"] = False
                    st.session_state.pop("confirm_overwrite", None)
            st.stop()

        # Either file does not exist OR user confirmed overwrite
        if st.button("Add Document", key="confirm_add_doc"):

            import os
            save_dir = os.path.abspath("uploads")
            os.makedirs(save_dir, exist_ok=True)
            dest_path = os.path.join(save_dir, filename)

            uploaded.seek(0)
            with open(dest_path, "wb") as f:
                f.write(uploaded.read())




# ---------------------------------------------------------
# MODAL: UPDATE DOCUMENT
# ---------------------------------------------------------
if st.session_state.get("show_update_modal"):

    st.write("## 📝 Update Document")

    # ✅ Correct list_documents call
    docs_result = safe_call(call("vdb_list_documents"))
    docs = docs_result.data["documents"]

    filename = st.selectbox("Select existing document to replace:", docs)

    uploaded = st.file_uploader(
        "Select new .docx file",
        type=["docx"],
        key="update_doc_uploader"
    )

    if uploaded and filename and st.button("Update Document", key="confirm_update_doc"):

        import os

        # ✅ Save replacement file
        save_dir = os.path.abspath("uploads")
        os.makedirs(save_dir, exist_ok=True)
        dest_path = os.path.join(save_dir, filename)

        uploaded.seek(0)
        with open(dest_path, "wb") as f:
            f.write(uploaded.read())

        # ✅ Call MCP tool to update VDB
        resp = safe_call(call("vdb_update_document", {"path": dest_path}))
        
        # ✅ Extract useful fields (if any)
        old_chunks = resp.data.get("old_chunks_removed", 0)
        new_chunks = resp.data.get("new_chunks_added", 0)

        st.success(
            f"✅ Document '{filename}' updated successfully "
            f"({old_chunks} old chunks replaced with {new_chunks} new chunks)."
        )


        # ✅ Close modal AFTER success
        st.session_state["show_update_modal"] = False


# ---------------------------------------------------------
# MODAL: DELETE DOCUMENT
# ---------------------------------------------------------
if st.session_state.get("show_delete_modal"):

    st.write("## 🗑 Delete Document")

    # ✅ Load documents correctly
    docs_result = safe_call(call("vdb_list_documents"))
    docs = docs_result.data["documents"]

    filename = st.selectbox("Select a document to delete:", docs)

    if st.button("Confirm Delete"):
        # ✅ Perform deletion
        resp = safe_call(call("vdb_delete_document", {"filename": filename}))

        removed = resp.data.get("chunks_removed", "unknown")

        st.success(f"✅ Deleted '{filename}' ({removed} chunks removed)")

        # ✅ Now it is safe to close the modal
        st.session_state["show_delete_modal"] = False