import streamlit as st
from io import BytesIO
from pathlib import Path
from PIL import Image
import base64
import numpy as np
import json

# Plotting and Data Handling
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Import logic from our backend files
import lab
import local_auth # Using the local auth and email module

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="AIRA - For Life Sciences",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def show_logo():
    try:
        logo_path = "images/logo.png" # Make sure you have this image in the correct path
        logo = Image.open(logo_path)
        buffer = BytesIO()
        logo.save(buffer, format="PNG")
        logo_base64 = base64.b64encode(buffer.getvalue()).decode()
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="height: 50px; margin-right: 15px;">
                <h1 style="font-size: 2.5em; font-weight: bold; color: #FFFFFF; margin: 0;">AIRA - For Life Sciences</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.error("Logo file not found. Please ensure 'images/logo.png' exists.")

# Custom CSS for a professional, dark-themed lab interface
st.markdown("""
<style>
    /* General App Styling */
    .stApp {
        background-color: #010314;
        color: white;
    }
    /* Tab Navigation Styling */
    .stRadio [role="radiogroup"] {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2rem;
        background-color: #070B2F;
        padding: 0.5rem;
        border-radius: 15px;
    }
    .stRadio [role="radio"] {
        background: transparent;
        border: 2px solid #12ABDB;
        border-radius: 10px;
        padding: 8px 24px;
        color: #12ABDB;
        cursor: pointer;
        transition: all 0.3s ease-in-out;
    }
    .stRadio [role="radio"] > label {
        color: #12ABDB;
    }
    .stRadio [role="radio"]:has(input:checked) {
        background: #12ABDB;
        color: #010314;
        font-weight: 700;
        box-shadow: 0px 0px 15px #12ABDB;
    }
    .stRadio [role="radio"]:has(input:checked) > label {
        color: #010314;
    }
    /* Text Input & Text Area Styling */
    .stTextInput input, .stTextArea textarea {
        background: #070B2F;
        border: 2px solid #12ABDB;
        color: #FFFFFF;
        border-radius: 10px;
    }
    /* Button Styling */
    .stButton>button {
        border: 2px solid #12ABDB;
        background-color: #070B2F;
        color: #12ABDB;
        border-radius: 10px;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #12ABDB;
        color: #010314;
        box-shadow: 0px 0px 15px #12ABDB;
    }
    /* Headers and Dividers */
    h1, h2, h3 {
        color: #12ABDB;
    }
    hr {
        background-color: #12ABDB;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATE INITIALIZATION ---
def init_session_state():
    if "user_email" not in st.session_state:
        st.session_state.user_email = None

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "1. Research Assistant"
    
    # State for Analysis Hub
    if 'hub_target_protein_data' not in st.session_state:
        st.session_state.hub_target_protein_data = None
    if 'hub_design_goal' not in st.session_state:
        st.session_state.hub_design_goal = ""
    if 'hub_design_results' not in st.session_state:
        st.session_state.hub_design_results = None
    if 'hub_uploaded_data' not in st.session_state:
        st.session_state.hub_uploaded_data = None

    # State for AI Research Report Tab
    if 'report_generation_stage' not in st.session_state:
        st.session_state.report_generation_stage = 'start'
    if 'research_question' not in st.session_state:
        st.session_state.research_question = ''
    if 'report_outline' not in st.session_state:
        st.session_state.report_outline = None
    if 'research_data' not in st.session_state:
        st.session_state.research_data = None
    if 'draft_report' not in st.session_state:
        st.session_state.draft_report = None
    if 'final_report' not in st.session_state:
        st.session_state.final_report = None

# --- 3. AUTHENTICATION UI ---
def render_auth_ui():
    st.title("Welcome to AIRA")
    st.write("Please sign in or create an account to continue.")

    choice = st.selectbox("Choose an option", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Sign Up":
        if st.button("Create Account"):
            if email and password:
                user_id, error = local_auth.sign_up_user_local(email, password)
                if error:
                    st.error(error)
                else:
                    st.success("Account created successfully! Please log in.")
                    subject = "Welcome to AIRA!"
                    body = f"Hello {email},\n\nYour account for the AIRA Research Assistant has been created.\n\nBest regards,\nThe AIRA Team"
                    local_auth.send_email_notification(email, subject, body)
            else:
                st.warning("Please provide both an email and a password.")
    else: # Login
        if st.button("Login"):
            user_id, error = local_auth.login_user_local(email, password)
            if error:
                st.error(error)
            else:
                st.session_state.user_email = user_id
                st.rerun()

# --- MAIN APP EXECUTION ---
init_session_state()

if st.session_state.user_email is None:
    render_auth_ui()
else:
    # --- USER IS LOGGED IN, RENDER THE MAIN APP ---
    with st.sidebar:
        st.subheader(f"Welcome, {st.session_state.user_email}")
        if st.button("Logout"):
            st.session_state.user_email = None
            st.rerun()

    show_logo()

    # --- NAVIGATION ---
    tab_names = [
        "1. Research Assistant",
        "2. Analysis & Simulation Hub",
        "3. AI Research Report",
    ]

    selected_tab = st.radio(
        "Navigation",
        tab_names,
        index=tab_names.index(st.session_state.active_tab),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.active_tab = selected_tab
    st.divider()

    # ==========================================================================
    # --- TAB 1: RESEARCH ASSISTANT ---
    # ==========================================================================
    if selected_tab == "1. Research Assistant":
        st.header("Step 1: Ask Your Research Question")
        st.markdown("Start your project by consulting with a team of specialized AI agents. Enter a high-level query to get multi-faceted insights.")
        user_query = st.text_area("Enter your research query:", height=150, key="query_tab1")

        if st.button("Run Query", key="button_tab1"):
            if user_query:
                with st.spinner("Querying AI agents..."):
                    results = lab.run_hierarchical_agent_system(user_query)
                    if results.get("error"):
                        st.error(results["error"])
                    else:
                        decision = results["supervisor_decision"]
                        all_responses = results["all_responses"]
                        st.subheader(f"Primary Analysis by the {decision} Agent")
                        st.info(f"{all_responses.get(decision, 'No response generated.')}")
                        with st.expander("View responses from all other specialized agents"):
                            for agent, response in all_responses.items():
                                if agent != decision:
                                    st.markdown(f"**{agent}:** {response}")
            else:
                st.warning("Please enter a query.")

    # ==========================================================================
    # --- TAB 2: ANALYSIS & SIMULATION HUB ---
    # ==========================================================================
    elif selected_tab == "2. Analysis & Simulation Hub":
        st.header("Step 2: Analyze, Simulate, and Validate")
        st.markdown("Use the modules below to identify molecular targets, design novel therapeutics, or upload your own data for analysis.")

        with st.expander("🔬 Module 1: Disease Target Identification", expanded=True):
            disease_name = st.text_input("Enter a disease name (e.g., Alzheimer's disease):")
            if st.button("Find Protein Targets"):
                if disease_name:
                    with st.spinner(f"Searching for targets related to '{disease_name}'..."):
                        st.session_state.hub_target_protein_data = lab.fetch_protein_data(disease_name)
                else:
                    st.warning("Please enter a disease name.")
            
            if st.session_state.hub_target_protein_data:
                data = st.session_state.hub_target_protein_data
                if data.get("error"):
                    st.error(data["error"])
                elif proteins := data.get("proteins"):
                    st.success(f"Found {len(proteins)} protein target(s).")
                    for uniprot_id in proteins:
                        st.subheader(f"Structure for UniProt ID: {uniprot_id}")
                        viewer = lab.generate_3d_protein_structure(uniprot_id)
                        st.components.v1.html(viewer._make_html(), height=500)
                        if st.button(f"Use {uniprot_id} for therapeutic design", key=f"design_{uniprot_id}"):
                            st.session_state.hub_design_goal = f"Generate nanobody variants with high binding affinity to protein {uniprot_id}."
                            st.success(f"Goal set! Go to Module 2 to design your therapeutic.")
                            st.rerun()

        with st.expander("🤖 Module 2: AI Therapeutic Designer"):
            if st.session_state.hub_design_goal:
                st.info(f"🎯 Pre-filled Goal: {st.session_state.hub_design_goal}")
            with st.form(key="designer_form"):
                nanobody_name = st.selectbox("Select Base Nanobody", options=list(lab.NANOBODY_SEQUENCES.keys()))
                design_goal_input = st.text_input("Enter or Refine Design Goal", value=st.session_state.hub_design_goal)
                if st.form_submit_button('Generate and Analyze Candidates'):
                    if design_goal_input:
                        with st.spinner("AI Designer is generating and analyzing sequences..."):
                            design_data = lab.run_nanobody_designer(nanobody_name, design_goal_input)
                            if "candidates" in design_data:
                                candidates = design_data.get("candidates", [])
                                wildtype_seq = design_data.get("wildtype")
                                analysis_df = lab.run_nanobody_analysis(candidates, wildtype_seq)
                                st.session_state.hub_design_results = analysis_df
                    else:
                        st.warning("Please enter a design goal.")
            
            if st.session_state.hub_design_results is not None:
                st.subheader("Design Campaign Results")
                st.dataframe(st.session_state.hub_design_results)

        with st.expander("📊 Module 3: Custom Data Validation"):
            uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.session_state.hub_uploaded_data = df
                    st.success("File uploaded successfully!")
                    st.dataframe(df.head())
                except Exception as e:
                    st.error(f"Error reading file: {e}")
            if st.session_state.hub_uploaded_data is not None:
                st.subheader("Create a Correlation Plot")
                df = st.session_state.hub_uploaded_data
                columns = df.columns.tolist()
                col1, col2 = st.columns(2)
                x_axis = col1.selectbox("Select X-axis", columns, index=0)
                y_axis = col2.selectbox("Select Y-axis", columns, index=min(1, len(columns)-1))
                if st.button("Generate Plot"):
                    fig, ax = plt.subplots()
                    sns.regplot(data=df, x=x_axis, y=y_axis, ax=ax, scatter_kws={'alpha':0.6})
                    st.pyplot(fig)

    # ==========================================================================
    # --- TAB 3: AI RESEARCH REPORT ---
    # ==========================================================================
    elif selected_tab == "3. AI Research Report":
        st.header("Step 3: Generate Your Full Research Report")
        st.markdown("Automate the creation of a scientific report, from outline to final draft, complete with verifiable citations.")
        
        def reset_report_workflow():
            st.session_state.report_generation_stage = 'start'
            st.session_state.research_question = ''
            st.session_state.report_outline = None
            st.session_state.research_data = None
            st.session_state.draft_report = None
            st.session_state.final_report = None
            st.rerun()

        def format_outline_as_text(outline_json):
            if not isinstance(outline_json, dict): return "Outline is not in the correct format."
            sections = outline_json.get('sections', [])
            subsections = outline_json.get('subsections', {})
            descriptions = outline_json.get('descriptions', {})
            markdown_output = []
            for i, section_title in enumerate(sections):
                markdown_output.append(f"### {i+1}. {section_title}")
                section_subsections = subsections.get(section_title, [])
                section_descriptions = descriptions.get(section_title, {})
                if not section_subsections:
                    markdown_output.append("> *No subsections defined.*")
                for sub_title in section_subsections:
                    markdown_output.append(f"- **{sub_title}**")
                    description_text = section_descriptions.get(sub_title, "No description provided.")
                    markdown_output.append(f"  > *{description_text}*")
                markdown_output.append("")
            return "\n".join(markdown_output)

        if st.session_state.report_generation_stage == 'start':
            st.subheader("Step 3.1: Define Your Research Question")
            research_q = st.text_area("Enter your research question here:", height=100, key="report_q_input", value=st.session_state.research_question)
            if st.button("Generate Report Outline"):
                if research_q:
                    st.session_state.research_question = research_q
                    with st.spinner("Generating a detailed report outline..."):
                        web_research = lab.get_web_research_summary(st.session_state.research_question)
                        outline = lab.run_outline_agent(st.session_state.research_question, web_research)
                        if "error" in outline:
                            st.error(outline["error"])
                        else:
                            st.session_state.report_outline = outline
                            st.session_state.report_generation_stage = 'outline_generated'
                            st.rerun()
                else:
                    st.warning("Please enter a research question.")

        if st.session_state.report_generation_stage in ['outline_generated', 'research_gathered', 'writing_complete', 'editing_complete']:
            st.subheader("Report Outline")
            if st.session_state.report_outline:
                st.markdown(format_outline_as_text(st.session_state.report_outline))
                if st.session_state.report_generation_stage == 'outline_generated':
                    if st.button("Step 3.2: Gather Research Data"):
                        with st.spinner("Research Agent is gathering cited information... This may take a minute."):
                            research = lab.run_research_agent(st.session_state.research_question, json.dumps(st.session_state.report_outline))
                            if research.startswith("Error"):
                                st.error(research)
                            else:
                                st.session_state.research_data = research
                                st.session_state.report_generation_stage = 'research_gathered'
                                st.rerun()
        
        if st.session_state.report_generation_stage in ['research_gathered', 'writing_complete', 'editing_complete']:
            st.subheader("Collected Research Data")
            if st.session_state.research_data:
                with st.expander("View Collected Research", expanded=False):
                    st.markdown(st.session_state.research_data)
                if st.session_state.report_generation_stage == 'research_gathered':
                    if st.button("Step 3.3: Write Full Draft Report"):
                        outline = st.session_state.report_outline
                        sections = outline.get('sections', [])
                        full_draft = ""
                        writer_progress = st.progress(0, text="Writer Agent is starting...")
                        for i, section_title in enumerate(sections):
                            writer_progress.progress((i) / len(sections), text=f"Writing section: {section_title}...")
                            section_outline_details = { "subsections": outline.get('subsections', {}).get(section_title, []), "descriptions": outline.get('descriptions', {}).get(section_title, {}) }
                            section_content = lab.run_writer_agent(section_title, json.dumps(section_outline_details), st.session_state.research_data)
                            if section_content.startswith("Error"):
                                st.error(section_content)
                                full_draft = None
                                break
                            full_draft += f"\n\n## {section_title}\n\n{section_content}"
                        writer_progress.progress(1.0, text="Draft writing complete!")
                        if full_draft:
                            st.session_state.draft_report = full_draft
                            st.session_state.report_generation_stage = 'writing_complete'
                            st.rerun()

        if st.session_state.report_generation_stage in ['writing_complete', 'editing_complete']:
            st.subheader("Generated Draft Report")
            if st.session_state.draft_report:
                with st.expander("View Full Draft", expanded=False):
                    st.markdown(st.session_state.draft_report)
                if st.session_state.report_generation_stage == 'writing_complete':
                    if st.button("Step 3.4: Edit and Finalize Report"):
                        with st.spinner("Editor Agent is reviewing and polishing the final report..."):
                            final_version = lab.run_editor_agent(st.session_state.research_question, st.session_state.draft_report)
                            if final_version.startswith("Error"):
                                st.error(final_version)
                            else:
                                st.session_state.final_report = final_version
                                st.session_state.report_generation_stage = 'editing_complete'
                                st.rerun()

        if st.session_state.report_generation_stage == 'editing_complete':
            st.subheader("Final Polished Report")
            st.success("Your research report has been generated successfully!")
            if st.session_state.final_report:
                st.markdown(st.session_state.final_report)
                
                st.download_button(
                    label="⬇️ Download Report as Markdown",
                    data=st.session_state.final_report.encode('utf-8'),
                    file_name=f"research_report_{st.session_state.research_question[:20].replace(' ', '_')}.md",
                    mime='text/markdown',
                )
                if st.button("Email Final Report to Myself"):
                    subject = f"Your AIRA Research Report: {st.session_state.research_question}"
                    body = st.session_state.final_report
                    success, msg = local_auth.send_email_notification(st.session_state.user_email, subject, body)
                    if success:
                        st.success(msg)

        if st.session_state.report_generation_stage != 'start':
            st.divider()
            if st.button("Start a New Report"):
                reset_report_workflow()

