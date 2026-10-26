import logging

import streamlit as st

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.llm import generate_answer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Small Business AI Assistant",
    page_icon="💬",
)

st.title("Small Business AI Assistant")
st.caption("Ask a question and get an AI-generated response.")

question = st.text_input(
    "Your question",
    placeholder="Ask a business-related question...",
)

if st.button("Ask", type="primary", disabled=not question.strip()):
    try:
        with st.spinner("Generating answer..."):
            result = generate_answer(question.strip())

        logger.info(
            "LLM request completed | model=%s | latency_ms=%.2f",
            result["model"],
            result["latency_ms"],
        )

        st.subheader("Answer")
        st.write(result["answer"])

        col1, col2, col3 = st.columns(3)

        col1.metric("Retrieval", f'{result["retrieval_ms"]:.1f} ms')
        col2.metric("LLM", f'{result["latency_ms"]:.0f} ms')
        col3.metric("Products found", result["retrieved_count"])
    except Exception:
        logger.exception("Failed to generate an answer")
        st.error("The assistant couldn't generate a response. Please try again.")