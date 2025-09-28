import json
import re
import time
from typing import List, Dict, Any

# Third-party libraries
import py3Dmol
import requests
from openai import AzureOpenAI
import pandas as pd
import numpy as np
import streamlit as st
import concurrent.futures
import json
import uuid
import requests
import os
from datetime import datetime
from pathlib import Path
from openai import AzureOpenAI
import time
import re

# RDKit and Datamol
import rdkit
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
import datamol as dm

# Py3Dmol for 3D viewing
import py3Dmol

# Plotting and Data Handling
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Image Handling
from PIL import Image
import base64
from io import BytesIO
from typing import Iterable, List

# --------------------------------------------------------------------------
# --- 1. SECURE AZURE OPENAI CONFIGURATION ---
# --------------------------------------------------------------------------
# This function securely initializes and returns the Azure OpenAI client.
# It fetches credentials from Streamlit's secrets management, which is the
# recommended best practice. Avoid hardcoding keys in your code.
@st.cache_resource
def get_azure_openai_client():
    """
    Initializes and returns an AzureOpenAI client using credentials
    stored in Streamlit's secrets management.
    """
    try:
        client = AzureOpenAI(
            azure_endpoint=st.secrets["AZURE_ENDPOINT"],
            api_key=st.secrets["AZURE_API_KEY"],
            api_version=st.secrets["API_VERSION"],
        )
        return client
    except Exception as e:
        st.error(f"Failed to initialize Azure OpenAI client. Please check your .streamlit/secrets.toml file. Error: {e}")
        return None

# Centralized deployment name from secrets
DEPLOYMENT_NAME = st.secrets.get("DEPLOYMENT_NAME")

# --------------------------------------------------------------------------
# --- 2. HELPER FUNCTIONS ---
# --------------------------------------------------------------------------
def extract_json(text: str) -> dict:
    """
    Safely extracts a JSON object from a string that might contain other text.
    Handles potential JSON decoding errors.
    """
    try:
        # Use a regex to find the JSON block, which is more robust
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        st.warning("JSON object not found in the response.")
        return {}
    except json.JSONDecodeError:
        st.error("Failed to decode JSON from the API response.")
        return {}

# --------------------------------------------------------------------------
# --- 3. LOGIC FOR EACH TAB ---
# --------------------------------------------------------------------------

# --- Logic for Tab 1: Research Assistant ---

def run_agent(system_prompt: str, user_query: str, agent_task_prompt: str):
    """Generic function to run a single agent turn with the Azure OpenAI API."""
    client = get_azure_openai_client()
    if not client:
        return "Error: Azure OpenAI client is not available."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{agent_task_prompt}\n\nUser Query: '{user_query}'"}
    ]
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=800,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: An API error occurred: {e}"

def run_hierarchical_agent_system(user_query: str):
    """
    Manages the hierarchical agent workflow for the Research Assistant tab.
    A supervisor agent first delegates the task to the most relevant specialist.
    """
    supervisor_prompt = (
        "You are a supervisor agent managing a team of specialized AI assistants for drug discovery. "
        "Your team consists of: Bioinformatics, Pharmacokinetics, Pharmacodynamics, Clinical Trials, Toxicology, and Regulatory Affairs. "
        "Based on the user's query, your task is to identify and respond with ONLY the name of the single most relevant agent to handle the query (e.g., respond with 'Bioinformatics')."
    )
    supervisor_decision = run_agent("You are a supervisor agent.", user_query, supervisor_prompt)

    if supervisor_decision.startswith("Error:"):
        return {"error": supervisor_decision}

    agent_prompts = {
        "Bioinformatics": ("You are a bioinformatics assistant.", "Your expertise includes gene target identification, sequence analysis, and structural bioinformatics. Provide a detailed analysis based on the user's query."),
        "Pharmacokinetics": ("You are a pharmacokinetics (ADME) assistant.", "Your expertise includes modeling drug Absorption, Distribution, Metabolism, and Excretion. Analyze the query from an ADME perspective."),
        "Pharmacodynamics": ("You are a pharmacodynamics assistant.", "Your expertise includes receptor binding, dose-response relationships, and mechanism of action. Address the query based on these principles."),
        "Clinical Trials": ("You are a clinical trials assistant.", "Your expertise includes trial design, patient recruitment, statistical analysis, and regulatory phases. Frame your response in the context of clinical trials."),
        "Toxicology": ("You are a toxicology assistant.", "Your expertise includes evaluating toxicity profiles, identifying potential adverse effects, and risk assessment. Analyze the query for toxicological relevance."),
        "Regulatory Affairs": ("You are a regulatory affairs assistant.", "Your expertise includes navigating FDA/EMA guidelines, submission processes, and compliance. Provide insights on the regulatory aspects of the query."),
    }

    responses = {}
    # To improve efficiency, you could choose to run only the selected agent.
    # However, running all provides a multi-faceted view.
    for name, (system_prompt, task_prompt) in agent_prompts.items():
        responses[name] = run_agent(system_prompt, user_query, task_prompt)

    # Clean the supervisor's decision to ensure it matches a key
    cleaned_decision = supervisor_decision.replace('.', '').strip()
    if cleaned_decision not in agent_prompts:
        # Fallback if the supervisor's response is not a valid agent name
        cleaned_decision = next(iter(agent_prompts))


    return {
        "supervisor_decision": cleaned_decision,
        "all_responses": responses
    }

# --- Logic for Tab 2: Nanobody Design Lab ---

class Agent:
    """A simple class to define an LLM agent's persona."""
    def __init__(self, title: str, expertise: str, goal: str, role: str) -> None:
        self.title = title
        self.expertise = expertise
        self.goal = goal
        self.role = role

    @property
    def prompt(self) -> str:
        return (
            f"You are a {self.title}. "
            f"Your expertise is in {self.expertise}. "
            f"Your goal is to {self.goal}. "
            f"Your role is to {self.role}."
        )

    def __str__(self) -> str:
        return self.title

# Define the team of agents for the collaborative discussion
principal_investigator = Agent(
    title="Principal Investigator",
    expertise="applying artificial intelligence to biomedical research",
    goal="perform research in your area of expertise that maximizes the scientific impact of the work",
    role="lead a team of experts to solve an important problem in artificial intelligence for biomedicine, make key decisions about the project direction based on team member input, and manage the project timeline and resources",
)

team_members = [
    Agent(
        title="Immunologist",
        expertise="antibody engineering and immune response characterization",
        goal="guide the development of antibodies/nanobodies that elicit a strong and broad immune response",
        role="advise on immunogenicity, cross-reactivity with other variants, and potential for therapeutic application",
    ),
    Agent(
        title="Machine Learning Specialist",
        expertise="developing algorithms for protein-ligand interactions and optimization",
        goal="create and apply machine learning models to predict antibody efficacy and optimize binding affinity",
        role="lead the development of AI tools for predicting interactions and refining antibody designs",
    ),
    Agent(
        title="Computational Biologist",
        expertise="protein structure prediction and molecular dynamics simulations",
        goal="develop predictive models to identify potential antibody/nanobody candidates and simulate interactions",
        role="provide insights into structural dynamics and validate computational predictions",
    ),
]

def initialize_team_discussion(agenda: str) -> List[Dict[str, str]]:
    """Kicks off the simulated team meeting with the Principal Investigator's opening statement."""
    client = get_azure_openai_client()
    if not client:
        return [{"agent": "Error", "message": "Azure OpenAI client is not available."}]

    prompt_text = f"As the Principal Investigator, you are starting a team meeting. The research agenda is: '{agenda}'. Please provide your opening statement to the team. Outline the project's direction, key challenges, and your initial goals."
    messages = [{"role": "system", "content": principal_investigator.prompt}, {"role": "user", "content": prompt_text}]

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME, messages=messages, max_tokens=800, temperature=0.7
        )
        opening_statement = response.choices[0].message.content.strip()
    except Exception as e:
        opening_statement = f"Error generating Principal Investigator response: {e}"

    return [{"agent": "Principal Investigator", "message": opening_statement}]


def advance_team_discussion(discussion_history: List[Dict[str, str]], agenda: str, num_rounds: int) -> Dict[str, Any]:
    """Advances the simulated team discussion by one turn for the next agent in line."""
    client = get_azure_openai_client()
    if not client:
        return {"discussion_history": discussion_history, "is_complete": True}

    full_agent_roster = [principal_investigator] + team_members
    current_turn_number = len(discussion_history)
    total_turns_per_round = len(full_agent_roster)
    total_turns = num_rounds * total_turns_per_round

    if current_turn_number >= total_turns:
        return {"discussion_history": discussion_history, "is_complete": True}

    next_agent_index = current_turn_number % total_turns_per_round
    next_agent = full_agent_roster[next_agent_index]
    current_round = (current_turn_number // total_turns_per_round) + 1
    last_message = discussion_history[-1]["message"]
    last_speaker = discussion_history[-1]["agent"]

    prompt_text = (
        f"The research agenda is: '{agenda}'.\n\n"
        f"This is a multi-turn team discussion. Here is the most recent contribution:\n"
        f"'{last_speaker} said: {last_message}'\n\n"
        f"Now, as the {next_agent.title}, it is your turn to speak. Please provide your input for Round {current_round} of {num_rounds}. Build upon the previous points and offer your unique perspective."
    )
    messages = [{"role": "system", "content": next_agent.prompt}, {"role": "user", "content": prompt_text}]

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME, messages=messages, max_tokens=800, temperature=0.7
        )
        agent_response = response.choices[0].message.content.strip()
    except Exception as e:
        agent_response = f"Error generating response for {next_agent.title}: {e}"

    discussion_history.append({"agent": next_agent.title, "message": agent_response})
    is_complete = len(discussion_history) >= total_turns

    return {"discussion_history": discussion_history, "is_complete": is_complete}

# Pre-defined nanobody sequences for the designer
NANOBODY_SEQUENCES = {
    "H11-D4": "QVQLQESGGGLVQAGGSLRLSCAASGFTFSSYAMAWFRQAPGKEREFVSAISWSGGSTYYADSVKGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAAADANLSTVVFYYYYMDVWGKGTQVTVSS",
    "Nb21": "QVQLQESGGGLVQAGGSLRLSCAASGRIFSSYAMGWFRQAPGKEREFVAAISWSGGSTYYADSVKGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAADDLSTVVFYYYYMDVWGKGTQVTVSS",
    "Ty1": "QVQLQESGGGLVQAGGSLRLSCAASGFTFSDYAMAWFRQAPGKEREFVSAISWSGGSTYYADSVKGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAAADNLSTVVFYYYYMDVWGKGTQVTVSS",
    "VHH-72": "QVQLQESGGGLVQAGGSLRLSCAASGFTFSSYDMAWFRQAPGKEREFVSAISWSGGSTYYADSVKGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAAADSLSTVVFYYYYMDVWGKGTQVTVSS",
}

def run_nanobody_designer(nanobody_name: str, design_goal: str) -> Dict[str, Any]:
    """Generates new nanobody sequences using a specialized AI agent."""
    client = get_azure_openai_client()
    if not client:
        return {"error": "Azure OpenAI client is not available."}

    if nanobody_name not in NANOBODY_SEQUENCES:
        return {"error": "Selected base nanobody not found."}

    wildtype_sequence = NANOBODY_SEQUENCES[nanobody_name]
    system_prompt = (
        "You are a specialist in protein and nanobody design with expertise in computational biology and machine learning. "
        "Your task is to generate novel, plausible nanobody amino acid sequences by introducing mutations into a provided wildtype sequence. "
        "Focus on modifications that are likely to achieve the user's specified design goal. "
        "Return a single JSON object with one key: `candidates`, which should be a list of strings, where each string is a new nanobody sequence."
    )
    user_prompt = (
        f"The wildtype nanobody is {nanobody_name} with the sequence: '{wildtype_sequence}'.\n\n"
        f"The design goal is: '{design_goal}'.\n\n"
        "Please generate the JSON object with the list of new candidate sequences."
    )
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=1500,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = extract_json(content)
        data['wildtype'] = wildtype_sequence
        return data
    except Exception as e:
        return {"error": f"Azure API Error during design generation: {e}"}

def run_nanobody_analysis(sequences: List[str], wildtype_sequence: str) -> pd.DataFrame:
    """Analyzes generated sequences using another AI agent to predict key biophysical metrics."""
    client = get_azure_openai_client()
    if not client:
        return pd.DataFrame([{"error": "Azure OpenAI client is not available."}])

    sequences_str = "\n".join(sequences)
    system_prompt = (
        "You are a specialist in predicting biophysical properties of proteins from their amino acid sequence. "
        "Your task is to predict three key metrics for a list of new nanobody sequences: "
        "1. `esm_llr`: A log-likelihood ratio score from a protein language model, indicating biological plausibility. Higher is better. "
        "2. `plddt`: A score from 0-100 indicating confidence in the predicted structure of the binding interface (interface pLDDT). Higher is better. "
        "3. `dG_separated`: A score predicting binding energy to the target (Delta G). Lower (more negative) is better. "
        "Return a single JSON object with one key: `analysis`, which is a list of objects. Each object must contain the `sequence`, `esm_llr`, `plddt`, and `dG_separated`."
    )
    user_prompt = f"Please analyze the following sequences and provide the predicted metrics in the specified JSON format:\n{sequences_str}"
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=2000,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        data = extract_json(content)
        df = pd.DataFrame(data.get("analysis", []))

        # Add wildtype for comparison with plausible placeholder scores
        wildtype_data = {
            "name": "wildtype",
            "sequence": wildtype_sequence,
            "esm_llr": 0,  # LLR is a ratio vs wildtype, so it's 0 by definition
            "plddt": np.random.uniform(85, 95), # Placeholder
            "dG_separated": np.random.uniform(-30, -25) # Placeholder
        }
        df['name'] = [f"designed_{i+1}" for i in range(len(df))]

        # Combine and reorder columns for clarity
        final_df = pd.concat([pd.DataFrame([wildtype_data]), df], ignore_index=True)
        return final_df[['name', 'sequence', 'esm_llr', 'plddt', 'dG_separated']]
    except Exception as e:
        return pd.DataFrame([{"error": f"Azure API Error during analysis: {e}"}])

# --- Logic for Tab 5: Molecule Structure Prediction ---

def fetch_protein_data(disease: str) -> Dict:
    """Fetches protein data (UniProt IDs) associated with a given disease using an AI agent."""
    client = get_azure_openai_client()
    if not client:
        return {"error": "Azure OpenAI client is not available."}

    system_prompt = (
        "You are a biomedical research assistant. Your task is to identify key proteins associated with a given disease. "
        "For each protein, you must provide its standard UniProt ID. "
        "Return a single JSON object with one key: `proteins`, which should be a list of strings (the UniProt IDs)."
    )
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Disease: {disease}"}]

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=800,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return extract_json(content)
    except Exception as e:
        return {"error": f"Azure API Error: {e}"}

def generate_3d_protein_structure(uniprot_id: str):
    """Generates an interactive 3D protein structure viewer from a UniProt ID using the AlphaFold database."""
    try:
        # Fetch PDB data from AlphaFold's public database
        alphafold_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
        res = requests.get(alphafold_url)
        if res.status_code == 404:
            return {"error": f"No 3D structure available from AlphaFold for UniProt ID {uniprot_id}."}
        res.raise_for_status() # Raise an exception for other HTTP errors
        pdb_content = res.text

        # Create an interactive 3D viewer using py3Dmol
        viewer = py3Dmol.view(width=800, height=400)
        viewer.addModel(pdb_content, "pdb")
        viewer.setStyle({"cartoon": {"color": "spectrum"}})
        viewer.zoomTo()
        return viewer
    except Exception as e:
        return {"error": f"An error occurred while fetching the 3D structure for {uniprot_id}: {e}"}

# --------------------------------------------------------------------------
# --- 4. LOGIC FOR NEW TAB: AI Research Report ---
# --------------------------------------------------------------------------
def get_web_research_summary(query: str) -> str:
    """
    Simulates fetching additional web research by using the LLM to summarize
    the current state of knowledge on a topic.
    """
    client = get_azure_openai_client()
    if not client:
        return "Error: Azure OpenAI client is not available."

    system_prompt = "You are a web research assistant. Your goal is to provide a concise summary of the most important, recent findings and key concepts related to the user's query. Focus on information that would be relevant for a scientific report."
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": query}]
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during web research simulation: {e}"

def run_outline_agent(research_question: str, additional_research: str) -> Dict:
    """
    Calls the Outline Agent to generate a structured JSON outline for the report.
    """
    client = get_azure_openai_client()
    if not client:
        return {"error": "Azure OpenAI client is not available."}

    prompt = f"""
    Create a detailed outline for an interdisciplinary research report on: {research_question}. Return a JSON object with 'sections' as 
    a list of section titles, 'subsections' with key points, and 'descriptions' with the purpose of each subsection. Ensure the outline integrates expertise from microbiology, 
    neuroscience, immunology, biochemistry or other scientific fields that relate to the research question detailed, specifying analytical approaches (e.g., 16S rRNA sequencing, neuroimaging), cross-disciplinary integration points (e.g., gut-brain 
    axis mechanisms), and mechanistic pathways (e.g., neuroinflammation, metabolite production).
    Example: {{'sections': ['Introduction', 'Methods'], 'subsections': {{'Introduction': ['Background', 'Objectives'], 'Methods': ['Design', 'Analysis']}}, 
    'descriptions': {{'Introduction': {{'Background': 'Contextualizes the gut microbiome\'s role in neurodegeneration'}}}}. Ensure all sections and subsections are relevant to 
    the research question and avoid generic placeholders.

    The outline should be precise and specific to the research question, with no placeholder content.
    The outline should be comprehensive enough to guide an interdisciplinary research effort.
    Include the following sections at minimum: Introduction, Literature Review, Methods, Results, Discussion, and Conclusion.
    Structure your response as a valid JSON object.
    
    The example should only be used to illustrate the format and should be tailored to the research question.

    The outline should also use the additional web research to help inform the outline:
    {additional_research}
    """
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=2000,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return extract_json(content)
    except Exception as e:
        return {"error": f"Error with Outline Agent: {e}"}

def run_research_agent(research_question: str, outline: str) -> str:
    """
    Calls the Research Agent to gather information with CLICKABLE citations.
    """
    client = get_azure_openai_client()
    if not client:
        return "Error: Azure OpenAI client is not available."

    prompt = f"""
    You respond in markdown. Conduct comprehensive interdisciplinary research on: {research_question}.
    For each subsection in the provided outline, gather key facts, definitions, and recent findings (2020–2025) from reliable scientific sources (e.g., PubMed, Nature, Google Scholar).
    
    CRITICAL REQUIREMENT: For each piece of information, you MUST provide an in-text citation formatted as a clickable markdown link: `[Author, Year](URL)`. 
    The URL must be a direct, public link to the source (e.g., a PubMed, DOI, or arXiv link). Ensure every URL is valid.
    
    Return a structured summary organized by the outline's subsections.
    The output MUST include a final 'References' section at the end, listing the full citation and the clickable URL for every source used.
    
    Here's the outline for your reference:
    {outline}

    - Ensure all citation URLs are real and lead to the source article.
    - Prioritize peer-reviewed research published in the last 5 years.
    - Be thorough and detailed in your research for each subsection.
    """
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=4000, # Increased tokens for detailed research
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error with Research Agent: {e}"

def run_writer_agent(section: str, section_outline: str, research_data: str) -> str:
    """
    Calls the Writer Agent to generate VERBOSE content for a specific section.
    """
    client = get_azure_openai_client()
    if not client:
        return "Error: Azure OpenAI client is not available."

    prompt = f"""
    You respond in markdown. Your task is to act as a scientific writer and generate a VERBOSE, DETAILED, and COMPREHENSIVE section for a research report on '{section}'.
    
    CRITICAL REQUIREMENT: Use the supplied research data to produce **at least 300-500 words of scientifically accurate, multi-paragraph content for EACH subsection.** Do NOT write short summaries; your primary goal is depth, detail, and providing a full explanation.
    
    You MUST preserve the clickable in-text citations provided in the research data, which are in the format `[Author, Year](URL)`. Do not convert them to plain text.
    Integrate interdisciplinary perspectives, emphasizing connections. Format with headings and subheadings.
    
    Your output should ONLY be the content for the requested '{section}'. Do not add titles, or content for other sections.

    Here's the outline for your section:
    {section_outline}

    Here's the research data, including clickable citations, for you to use:
    {research_data}
    """
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=4000, # Increased tokens for verbose writing
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error with Writer Agent for section '{section}': {e}"

def run_editor_agent(research_question: str, draft_report: str) -> str:
    """
    Calls the Editor Agent to review and polish the complete draft report.
    """
    client = get_azure_openai_client()
    if not client:
        return "Error: Azure OpenAI client is not available."

    prompt = f"""
    You respond in markdown. Review and edit the complete research report for: {research_question}. 
    Ensure logical flow, consistency, clarity, grammar, and scientific accuracy. 
    Strengthen the integration between sections (e.g., link Literature Review findings to Results). 
    Strengthen the Conclusion with a clear summary of key findings and actionable recommendations for future research.
    
    CRITICAL REQUIREMENT: Verify that all clickable in-text citations `[Author, Year](URL)` are preserved and correctly formatted.
    
    Return the polished report in markdown format.

    Here's the draft report:
    {draft_report}
    """
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=4000, # Increased tokens for editing the full report
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error with Editor Agent: {e}"

