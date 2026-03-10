import streamlit as st
import requests
from dotenv import load_dotenv
from docx import Document
from PyPDF2 import PdfReader
import io

load_dotenv()

st.set_page_config(page_title="Meeting Insights Analyzer", layout="wide")

st.title("📝 AI Meeting Insights Analyzer")
st.markdown("Upload documents or paste text to extract summary, action items, risks, and priority tasks")

API_URL = "http://localhost:8000"

def extract_text_from_docx(file):
    doc = Document(io.BytesIO(file.read()))
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(io.BytesIO(file.read()))
    return "\n".join([page.extract_text() for page in pdf_reader.pages])

# File upload section
uploaded_file = st.file_uploader("Upload a document (PDF or DOCX)", type=["pdf", "docx"])

text_input = ""
if uploaded_file:
    try:
        if uploaded_file.type == "application/pdf":
            text_input = extract_text_from_pdf(uploaded_file)
            st.success(f"✅ Extracted text from PDF ({len(text_input)} characters)")
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text_input = extract_text_from_docx(uploaded_file)
            st.success(f"✅ Extracted text from DOCX ({len(text_input)} characters)")
    except Exception as e:
        st.error(f"❌ Error extracting text: {str(e)}")

# Text input section
st.markdown("### Or paste your text directly:")
text_input = st.text_area(
    "Enter meeting notes or text:",
    value=text_input,
    height=250,
    placeholder="Paste your meeting notes, document text, or upload a file above..."
)

# Show text stats
if text_input.strip():
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Characters", len(text_input))
    with col2:
        st.metric("Words", len(text_input.split()))

if st.button("🚀 Analyze", type="primary"):
    if not text_input.strip():
        st.error("Please provide text to analyze")
    else:
        with st.spinner("Analyzing..."):
            try:
                response = requests.post(
                    f"{API_URL}/analyze",
                    json={"text": text_input}
                )
                response.raise_for_status()
                data = response.json()
                
                st.success("✅ Analysis complete!")
                
                # Token usage
                st.markdown("### 📊 Token Usage")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Input Tokens", data.get("input_tokens", 0))
                with col2:
                    st.metric("Output Tokens", data.get("output_tokens", 0))
                with col3:
                    st.metric("Total", data.get("input_tokens", 0) + data.get("output_tokens", 0))
                
                st.markdown("---")
                
                # Summary
                st.subheader("📄 Summary")
                st.write(data.get("summary", "No summary available"))
                
                st.markdown("---")
                
                # Three columns for action items, risks, priority tasks
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("✅ Action Items")
                    action_items = data.get("action_items", [])
                    if action_items:
                        for item in action_items:
                            st.markdown(f"- {item}")
                    else:
                        st.info("No action items found")
                
                with col2:
                    st.subheader("⚠️ Risks")
                    risks = data.get("risks", [])
                    if risks:
                        for risk in risks:
                            st.markdown(f"- {risk}")
                    else:
                        st.info("No risks identified")
                
                with col3:
                    st.subheader("🎯 Priority Tasks")
                    priority_tasks = data.get("priority_tasks", [])
                    if priority_tasks:
                        for task in priority_tasks:
                            st.markdown(f"- {task}")
                    else:
                        st.info("No priority tasks found")
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 400:
                    error_detail = e.response.json().get("detail", "Invalid request")
                    st.error(f"❌ {error_detail}")
                else:
                    st.error(f"❌ Error: {e.response.json().get('detail', str(e))}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the API server is running on port 8000")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
