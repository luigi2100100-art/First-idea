import streamlit as st
from docx import Document
import openai
import json
import os
import chromadb
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Project Blueprint: Compliance & Conversion SaaS",
    page_icon="🛡️",
    layout="wide"
)

# --- REGULATORY DISCLAIMER BANNER ---
st.markdown(
    """
    > **Disclaimer:** Project Blueprint provides automated pre-publication risk analysis and copy optimization suggestions. 
    > It does not constitute formal legal counsel. Always review final marketing deliverables with qualified regulatory counsel.
    """
)

st.title("🛡️ Project Blueprint")
st.subheader("Pre-Compliance & Conversion Optimization Engine for Wellness Brands")

# --- SIDEBAR: MILESTONE TRACKER & API CONFIG ---
st.sidebar.header("Engineering Milestones")
st.sidebar.text("✅ Milestone 1: UI & Document Ingestion")
st.sidebar.text("✅ Milestone 2: LLM Compliance & Scoring")
st.sidebar.text("✅ Milestone 3: ChromaDB RAG Knowledge Base")
st.sidebar.success("✅ **Milestone 4:** Docx Audit Log & Export (Active)")

st.sidebar.markdown("---")
st.sidebar.header("🔑 API Configuration")
api_key_input = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Enter your OpenAI API key to power the compliance and conversion audit engine."
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Current Environment:** GitHub Codespace / Python 3.x")

# --- CHROMADB RAG INITIALIZATION ---
DB_PATH = "./chroma_db"
REGULATIONS_DIR = "./data/regulations"

@st.cache_resource
def initialize_vector_db():
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(name="regulatory_knowledge_base")
    
    if os.path.exists(REGULATIONS_DIR):
        files = os.listdir(REGULATIONS_DIR)
        for filename in files:
            file_path = os.path.join(REGULATIONS_DIR, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if content.strip():
                        collection.upsert(
                            documents=[content],
                            metadatas=[{"source": filename}],
                            ids=[filename]
                        )
    return collection

rag_collection = initialize_vector_db()

# --- MAIN INTERFACE: INPUT SELECTION ---
st.markdown("---")
st.subheader("Step 1: Input Marketing Deliverable")

input_method = st.radio(
    "Choose ingestion method (Bypasses Codespaces mobile file-upload network errors):",
    ["📋 Paste Marketing Copy Directly", "📄 Upload .docx File"]
)

extracted_text = ""

if input_method == "📋 Paste Marketing Copy Directly":
    extracted_text = st.text_area(
        "Paste your sales page, email sequence, or ad copy here:",
        placeholder="Example: Discover how our new Vitamin D supplement instantly cures joint pain...",
        height=200
    )
else:
    uploaded_file = st.file_uploader(
        "Upload your compliance target document (.docx format)",
        type=["docx"]
    )
    if uploaded_file is not None:
        try:
            doc = Document(uploaded_file)
            full_text = [p.text for p in doc.paragraphs if p.text.strip()]
            extracted_text = "\n".join(full_text)
            st.success(f"Successfully loaded: **{uploaded_file.name}**")
        except Exception as e:
            st.error(f"Error reading docx file: {e}")

def retrieve_rag_context(query_text, collection, n_results=2):
    try:
        results = collection.query(query_texts=[query_text], n_results=n_results)
        documents = results.get("documents", [[]])[0]
        return "\n\n".join(documents)
    except Exception:
        return "No specific local regulatory precedents retrieved."

def run_compliance_audit(document_text, rag_context, api_key):
    client = openai.OpenAI(api_key=api_key)
    
    system_prompt = f"""
    You are an expert Senior Regulatory Compliance Officer and Direct-Response Copywriting Auditor specializing in FDA DSHEA rules, FTC deceptive advertising guidelines, and Meta/TikTok/Google Ads supplement policies.
    
    Use the following retrieved regulatory knowledge base (RAG Context) from official warning letters and platform policies to ground your analysis:
    ---
    {rag_context}
    ---
    
    Analyze the provided marketing text and return a valid JSON object strictly matching this schema:
    {{
      "conversion_scores": {{
        "overall_score": 7,
        "hook_strength": "Detailed critique of the hook...",
        "value_proposition": "Critique of value prop...",
        "credibility_proof": "Critique of clinical proof or testimonials...",
        "offer_clarity": "Critique of offer clarity...",
        "call_to_action": "Critique of CTA...",
        "benchmarks_feedback": "Actionable recommendations based on top wellness brand benchmarks..."
      }},
      "internal_mismatches": [
        "Description of any contradiction between fine-print disclaimers and aggressive headline claims..."
      ],
      "line_by_line_audits": [
        {{
          "original_text": "Exact problematic sentence or phrase from the text",
          "rule_violated": "Specific FDA/FTC/Ad platform rule violated",
          "violation_type": "Explicit or Implied",
          "explanation": "Why this triggers regulatory scrutiny or ad bans",
          "safe_rewrite": "Compliant rewrite preserving core persuasion and brand voice"
        }}
      ]
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": document_text}
        ],
        temperature=0.1
    )
    
    return json.loads(response.choices[0].message.content)

# --- MILESTONE 4: DOCX GENERATION HELPERS ---
def generate_edited_deliverable(original_text, audits):
    doc = Document()
    doc.add_heading("Project Blueprint: Compliant Edited Deliverable", level=1)
    doc.add_paragraph("This document contains your marketing copy with all AI-recommended regulatory safe rewrites applied.")
    doc.add_paragraph("---")
    
    # Perform string replacements for safe rewrites
    modified_text = original_text
    for item in audits:
        orig = item.get("original_text", "")
        rewrite = item.get("safe_rewrite", "")
        if orig and rewrite:
            modified_text = modified_text.replace(orig, rewrite)
            
    for paragraph in modified_text.split("\n"):
        if paragraph.strip():
            doc.add_paragraph(paragraph)
            
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def generate_audit_log_report(audit_results, original_text_len):
    doc = Document()
    doc.add_heading("Project Blueprint: Regulatory Audit & Compliance Log", level=1)
    doc.add_paragraph("Generated by Project Blueprint AI Compliance Engine")
    doc.add_paragraph(f"Analyzed Character Count: {original_text_len:,}")
    
    scores = audit_results.get("conversion_scores", {})
    doc.add_heading("1. Conversion & Compliance Summary", level=2)
    doc.add_paragraph(f"Overall Conversion Score: {scores.get('overall_score', 0)} / 10")
    doc.add_paragraph(f"Benchmark Feedback: {scores.get('benchmarks_feedback', '')}")
    
    doc.add_heading("2. Internal Context Mismatches", level=2)
    mismatches = audit_results.get("internal_mismatches", [])
    if mismatches:
        for idx, m in enumerate(mismatches, 1):
            doc.add_paragraph(f"Mismatch {idx}: {m}", style='List Bullet')
    else:
        doc.add_paragraph("No internal context mismatches detected.")
        
    doc.add_heading("3. Line-by-Line Regulatory Breakdown", level=2)
    audits = audit_results.get("line_by_line_audits", [])
    for idx, item in enumerate(audits, 1):
        doc.add_heading(f"Flagged Claim #{idx}", level=3)
        doc.add_paragraph(f"Original Text: \"{item.get('original_text', '')}\"")
        doc.add_paragraph(f"Rule Violated: {item.get('rule_violated', '')} ({item.get('violation_type', '')})")
        doc.add_paragraph(f"Explanation: {item.get('explanation', '')}")
        doc.add_paragraph(f"Safe Rewrite: {item.get('safe_rewrite', '')}")
        doc.add_paragraph("-" * 40)
        
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- PROCESSING PIPELINE ---
if extracted_text.strip():
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Characters", f"{len(extracted_text):,}")
    with col2:
        st.metric("Total Paragraphs", f"{len(extracted_text.split(chr(10))):,}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Content Preview", 
        "📚 RAG Knowledge Base", 
        "⚙️ AI Compliance Audit",
        "📥 Milestone 4: Export Deliverables"
    ])
    
    with tab1:
        st.text_area("Loaded Document Text", value=extracted_text, height=350)
        
    with tab2:
        st.subheader("Local Regulatory Vector Database (ChromaDB)")
        st.info(f"Connected to local vector store at `{DB_PATH}`. Indexed directory: `{REGULATIONS_DIR}`")
        
        if os.path.exists(REGULATIONS_DIR):
            indexed_files = os.listdir(REGULATIONS_DIR)
            st.write(f"**Currently Indexed Knowledge Files ({len(indexed_files)}):**")
            for file in indexed_files:
                st.text(f"• {file}")
        
        st.markdown("---")
        st.markdown("### ➕ Add New Regulation File")
        new_rule_title = st.text_input("Document Name (e.g., ftc_weight_loss_guidelines.txt)")
        new_rule_content = st.text_area("Paste Warning Letter Excerpt or Platform Policy Text")
        
        if st.button("Save & Index into ChromaDB"):
            if new_rule_title and new_rule_content:
                os.makedirs(REGULATIONS_DIR, exist_ok=True)
                save_path = os.path.join(REGULATIONS_DIR, new_rule_title)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(new_rule_content)
                st.cache_resource.clear()
                st.success(f"Successfully added and indexed **{new_rule_title}** into ChromaDB!")
                st.rerun()
            else:
                st.warning("Please provide both a document name and content.")

    with tab3:
        st.subheader("RAG-Powered Compliance & Conversion Engine")
        
        if not api_key_input:
            st.warning("⚠️ Please enter your **OpenAI API Key** in the left sidebar to run the compliance audit.")
        else:
            if st.button("🚀 Run RAG Compliance & Conversion Scan", type="primary"):
                with st.spinner("Retrieving local regulatory precedents and querying AI compliance engine..."):
                    try:
                        rag_context = retrieve_rag_context(extracted_text, rag_collection)
                        audit_results = run_compliance_audit(extracted_text, rag_context, api_key_input)
                        
                        st.session_state['audit_results'] = audit_results
                        st.session_state['extracted_text'] = extracted_text
                        
                        st.success("RAG Compliance audit completed successfully! Navigate to Tab 4 to download your deliverables.")
                        
                        scores = audit_results.get("conversion_scores", {})
                        st.markdown("### 📊 Conversion Potential & Market Intelligence")
                        col_score, col_bench = st.columns([1, 2])
                        with col_score:
                            st.metric("Overall Conversion Score", f"{scores.get('overall_score', 0)} / 10")
                        with col_bench:
                            st.info(f"**Benchmark Recommendations:** {scores.get('benchmarks_feedback', '')}")
                            
                        with st.expander("🔍 View Direct-Response Pillar Breakdown"):
                            st.write(f"**Hook Strength:** {scores.get('hook_strength', '')}")
                            st.write(f"**Value Proposition:** {scores.get('value_proposition', '')}")
                            st.write(f"**Credibility & Proof:** {scores.get('credibility_proof', '')}")
                            st.write(f"**Offer Clarity:** {scores.get('offer_clarity', '')}")
                            st.write(f"**Call to Action:** {scores.get('call_to_action', '')}")

                        st.markdown("---")
                        st.markdown("### ⚠️ Internal Context Mismatches Detected")
                        mismatches = audit_results.get("internal_mismatches", [])
                        if mismatches:
                            for idx, mismatch in enumerate(mismatches, 1):
                                st.error(f"**Mismatch {idx}:** {mismatch}")
                        else:
                            st.success("No internal context contradictions detected.")

                        st.markdown("---")
                        st.markdown("### 🔍 Line-by-Line Regulatory Decoding")
                        audits = audit_results.get("line_by_line_audits", [])
                        if audits:
                            for i, item in enumerate(audits, 1):
                                with st.container():
                                    st.markdown(f"#### Item {i}: Flagged Claim")
                                    st.markdown(f"> *\"{item.get('original_text', '')}\"*")
                                    cols = st.columns(2)
                                    with cols[0]:
                                        st.markdown(f"**Violation Rule:** {item.get('rule_violated', '')}")
                                        st.markdown(f"**Type:** `{item.get('violation_type', '')}`")
                                    with cols[1]:
                                        st.markdown(f"**Why it's problematic:** {item.get('explanation', '')}")
                                    st.markdown(f"✅ **Safe Compliant Rewrite:** `{item.get('safe_rewrite', '')}`")
                                    st.markdown("---")
                        else:
                            st.info("No compliance violations flagged.")
                            
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                        
            elif 'audit_results' in st.session_state:
                st.info("Previous audit results loaded from session state. Check Tab 4 for exports.")

    with tab4:
        st.subheader("📥 Milestone 4: Export Final Deliverables")
        
        if 'audit_results' in st.session_state and 'extracted_text' in st.session_state:
            audit_data = st.session_state['audit_results']
            orig_text = st.session_state['extracted_text']
            audits_list = audit_data.get("line_by_line_audits", [])
            
            st.success("Audit results are ready for export!")
            
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                st.markdown("### 📄 Compliant Edited Deliverable")
                st.markdown("Download your original copy with all risky claims automatically replaced by FDA/FTC-compliant safe rewrites.")
                edited_bio = generate_edited_deliverable(orig_text, audits_list)
                st.download_button(
                    label="📥 Download Edited Deliverable (.docx)",
                    data=edited_bio,
                    file_name="Project_Blueprint_Compliant_Deliverable.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            with col_dl2:
                st.markdown("### 📊 Detailed Audit Log Report")
                st.markdown("Download the full executive compliance report including scores, internal mismatches, and line-by-line violation breakdowns.")
                audit_bio = generate_audit_log_report(audit_data, len(orig_text))
                st.download_button(
                    label="📥 Download Audit Log Report (.docx)",
                    data=audit_bio,
                    file_name="Project_Blueprint_Audit_Log.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.warning("⚠️ Please run a compliance audit in **Tab 3** first before exporting deliverables.")
                        
else:
    if input_method == "📋 Paste Marketing Copy Directly":
        st.info("👆 Please paste your marketing copy above to initialize the workflow.")
    else:
        st.info("👆 Please paste your text or switch ingestion methods above.")
