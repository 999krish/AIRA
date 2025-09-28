AIRA: Your Personal PhD Research Team
Can't get a research position? We built you one.
AIRA is a virtual research assistant developed for the [Name of Hackathon]. It demonstrates how a powerful, multi-agent AI system can replicate the capabilities of an interdisciplinary research team, making high-level scientific discovery accessible to everyone.

🎯 Project Goal
The primary goal of AIRA is to solve the Student Opportunity Gap. Many students have brilliant ideas but lack the guidance, resources, or portfolio to secure competitive research positions. AIRA provides a solution by giving every student on-demand access to a virtual, PhD-level research team.

With AIRA, students can:

Learn by Doing: Explore complex scientific ideas in a guided, powerful environment.

Build a Portfolio: Go from hypothesis to a validated conclusion and a drafted paper, creating tangible projects to showcase their skills.

Break Barriers: Overcome the "portfolio paradox" where you need experience to get experience.

✨ Key Features
Multi-Agent System: A team of specialized AI agents (Biologist, Chemist, Principal Investigator) that collaborate, reason, and make decisions to automate a complex scientific workflow.

End-to-End Discovery Workflow: AIRA takes a high-level mission (e.g., "Design a therapeutic for COVID-19") and manages the entire process from hypothesis to a simulated experiment and a final scientific conclusion.

Interactive Virtual Lab: A user-friendly interface built with Streamlit that includes a 3D molecule viewer (Py3Dmol) to visualize the novel compounds designed by the AI agents.

Composable & Grounded Architecture: The system is built on a sophisticated architecture that is grounded in real-world scientific data from public databases (UniProt, AlphaFold) and ensures that all research is repeatable and verifiable.

📸 Screenshots
<img width="1807" height="725" alt="image" src="https://github.com/user-attachments/assets/2304edab-6c23-475b-8ff2-b512cc8e68a5" />

The AI Research Team in Action

<img width="1747" height="751" alt="image" src="https://github.com/user-attachments/assets/0ba293ff-84d4-44e7-adf0-fee4b4842bb3" />


3D Molecule Visualization

<img width="1100" height="832" alt="image" src="https://github.com/user-attachments/assets/a7b2fdc5-ddc2-4ae1-beaa-46d6b9f13f14" />


The Composable Architecture
<img width="1072" height="527" alt="image" src="https://github.com/user-attachments/assets/c61f54fa-1dba-4322-aec1-516c9237c5d4" />


<img width="952" height="720" alt="image" src="https://github.com/user-attachments/assets/f0f772c4-c51c-4099-9eb8-6539120fafc5" />


Team Members:
Krishna Vamsi R
Philippa Burgess
Aryan Jaiswal
Charishma Regulavalasa




🛠️ Setup & Installation
Follow these steps to run AIRA on your local machine.

1. Prerequisites
Python 3.9+

pip and venv

2. Clone the Repository
git clone [your-github-repo-link]
cd aira

3. Set up a Virtual Environment
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

4. Install Dependencies
pip install -r requirements.txt

5. Configure Your Secrets
Create a file at .streamlit/secrets.toml and add your Azure OpenAI credentials.

# .streamlit/secrets.toml

# Azure OpenAI Credentials

AZURE_ENDPOINT = "your-azure-endpoint-here"

AZURE_API_KEY = "your-azure-api-key-here"

API_VERSION = "your-api-version"

DEPLOYMENT_NAME = "your-model-deployment-name"


6. Run the Application
streamlit run app.py

The application should now be running on http://localhost:8501.

DEMO : https://www.youtube.com/watch?v=FHkneqKVnS0
🚀 Future Roadmap
Our vision for AIRA extends beyond this hackathon prototype.

Phase 2: The Student Platform (AIRA Multiplayer): Transform AIRA into a collaborative platform where student teams can work together on projects, guided by the AI agent mentors.

Phase 3: The Global Hub (The AIRA Hub): Leverage our composable architecture's Integration Layer to plug in AI research teams for any industry—Finance, Computer Science, Law, and more—making AIRA a universal platform for discovery.

<img width="1934" height="822" alt="image" src="https://github.com/user-attachments/assets/82f8d195-f481-40f0-a773-abcc221ed759" />

