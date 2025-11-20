import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Import retriever from vector (this will initialize/load the Chroma DB)
from vector import retriever

st.set_page_config(page_title="Agriculture Disease Assistant", layout="centered")

@st.cache_resource
def get_model():
    # Initialize the Ollama model once and reuse it
    return OllamaLLM(model="deepseek-r1:8b")

@st.cache_data
def retrieve_observations(query, k=5):
    # Try common retriever methods with fallbacks
    try:
        docs = retriever.get_relevant_documents(query)
    except Exception:
        try:
            docs = retriever.invoke(query)
        except Exception:
            try:
                docs = retriever.get_relevant_results(query)
            except Exception:
                docs = []
    # Normalize to list of strings
    results = []
    for d in docs:
        try:
            # LangChain Document
            results.append(d.page_content)
        except Exception:
            results.append(str(d))
    return results[:k]

model = get_model()

template = """
You are an expert in agriculture and crop disease detection.

Here are some relevant observations and records: {observations}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

st.title("Agriculture Disease Assistant")
st.markdown("Ask questions about crop diseases, symptoms, and treatments. The system will retrieve matching records and provide an answer using a local LLM.")

with st.form(key="query_form"):
    question = st.text_input("Enter your question:")
    submitted = st.form_submit_button("Ask")

if submitted and question:
    with st.spinner("Retrieving observations..."):
        observations = retrieve_observations(question)

    if not observations:
        st.warning("No matching observations found in the vector DB.")
    else:
        st.subheader("Top observations")
        for i, obs in enumerate(observations, start=1):
            st.markdown(f"**{i}.** {obs}")

    with st.spinner("Generating answer from the LLM..."):
        try:
            result = chain.invoke({"observations": "\n\n".join(observations), "question": question})
            st.subheader("Answer")
            st.write(result)
        except Exception as e:
            st.error(f"Model invocation failed: {e}")
            st.info("You can still view observations shown above.")

st.markdown("---")
st.caption("Requires Ollama running locally with the model `deepseek-r1:8b` and embeddings model available when building the vector DB.")
