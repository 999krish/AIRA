<p align="center">
<img src="https://www.google.com/search?q=https://placehold.co/1200x400/010314/ffa600%3Ftext%3DAIRA%26font%3Dinter" alt="AIRA Banner"/>
</p>

<h1 align="center">AIRA: Your Personal PhD Research Team</h1>

<p align="center">
<strong>Can't get a research position? We built you one.</strong>
<br />
<br />
<a href="https://www.youtube.com/watch?v=FHkneqKVnS0"><strong>Watch the Demo »</strong></a>
<br />
<br />
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Python-3776AB%3Fstyle%3Dfor-the-badge%26logo%3Dpython%26logoColor%3Dwhite" alt="Python">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/VS_Code-007ACC%3Fstyle%3Dfor-the-badge%26logo%3Dvisual-studio-code%26logoColor%3Dwhite" alt="Visual Studio Code">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Azure-0078D4%3Fstyle%3Dfor-the-badge%26logo%3Dmicrosoft-azure%26logoColor%3Dwhite" alt="Azure">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Azure_AI-0078D4%3Fstyle%3Dfor-the-badge%26logo%3Dazure-cognitive-services%26logoColor%3Dwhite" alt="Azure AI">
</p>

🎯 Project Goal: Solving the Student Opportunity Gap
AIRA is a virtual research assistant developed for the [Name of Hackathon]. It demonstrates how a powerful, multi-agent AI system can replicate the capabilities of an interdisciplinary research team, making high-level scientific discovery accessible to everyone.

Many students have brilliant ideas but lack the guidance, resources, or portfolio to secure competitive research positions. AIRA provides a solution by giving every student on-demand access to a virtual, PhD-level research team, empowering them to:

🌱 Learn by Doing: Explore complex scientific ideas in a guided, powerful environment.

📄 Build a Portfolio: Go from hypothesis to a validated conclusion and a drafted paper, creating tangible projects to showcase their skills.

🔓 Break Barriers: Overcome the "portfolio paradox" where you need experience to get experience.

✨ Key Features
🤖 Multi-Agent System: A team of specialized AI agents (Biologist, Chemist, Principal Investigator) that collaborate, reason, and make decisions to automate a complex scientific workflow.

🔬 End-to-End Discovery Workflow: AIRA takes a high-level mission (e.g., "Design a therapeutic for COVID-19") and manages the entire process from hypothesis to a simulated experiment and a final scientific conclusion.

🌐 Interactive Virtual Lab: A user-friendly interface built with Streamlit that includes a 3D molecule viewer (Py3Dmol) to visualize the novel compounds designed by the AI agents.

🔗 Composable & Grounded Architecture: The system is built on a sophisticated architecture that is grounded in real-world scientific data from public databases (UniProt, AlphaFold) and ensures that all research is repeatable and verifiable.

📸 Screenshots & Demo
<details>
<summary><strong>Click to view application screenshots</strong></summary>





<em>The AI Research Team in Action: Agents collaborating to solve a research problem.</em>
<p align="center">
<img width="90%" alt="The AI Research Team in Action" src="https://github.com/user-attachments/assets/2304edab-6c23-475b-8ff2-b512cc8e68a5" />
</p>





<em>3D Molecule Visualization: An AI-designed compound shown in the interactive lab.</em>
<p align="center">
<img width="90%" alt="3D Molecule Visualization" src="https://github.com/user-attachments/assets/0ba293ff-84d4-44e7-adf0-fee4b4842bb3" />
</p>





<em>The Composable Architecture: A look at the system's robust, layered design.</em>
<p align="center">
<img width="70%" alt="The Composable Architecture" src="https://github.com/user-attachments/assets/a7b2fdc5-ddc2-4ae1-beaa-46d6b9f13f14" />
</p>





<em>Application Workflow and Login Screens.</em>
<p align="center">
<img width="60%" alt="Application Workflow 1" src="https://github.com/user-attachments/assets/c61f54fa-1dba-4322-aec1-516c9237c5d4" />
<img width="50%" alt="Login Screen" src="https://github.com/user-attachments/assets/f0f772c4-c51c-4099-9eb8-6539120fafc5" />
</p>





<em>Final Report Generation: The end-to-end process culminating in a research paper.</em>
<p align="center">
<img width="90%" alt="Final Report Generation" src="https://github.com/user-attachments/assets/82f8d195-f481-40f0-a773-abcc221ed759" />
</p>
</details>

🛠️ Setup & Installation
Follow these steps to run AIRA on your local machine.

1. Prerequisites

         Python 3.9+
      
         pip and venv

3. Clone the Repository

         git clone [your-github-repo-link]
         cd aira

5. Set up a Virtual Environment
# For Windows
      python -m venv venv
      venv\Scripts\activate

# For macOS/Linux
      python3 -m venv venv
      source venv/bin/activate

4. Install Dependencies
   
            pip install -r requirements.txt

6. Configure Your Secrets
Create a file at .streamlit/secrets.toml and add your Azure OpenAI credentials.

# .streamlit/secrets.toml

    # Azure OpenAI Credentials
    AZURE_ENDPOINT = "your-azure-endpoint-here"
    AZURE_API_KEY = "your-azure-api-key-here"
    API_VERSION = "your-api-version"
    DEPLOYMENT_NAME = "your-model-deployment-name"  

6. Run the Application
   
           streamlit run app.py

The application should now be running at http://localhost:8501.

🚀 Future Roadmap
Our vision for AIRA extends beyond this hackathon prototype.

Phase 2: The Student Platform (AIRA Multiplayer): Transform AIRA into a collaborative platform where student teams can work together on projects, guided by the AI agent mentors.

Phase 3: The Global Hub (The AIRA Hub): Leverage our composable architecture's Integration Layer to plug in AI research teams for any industry—Finance, Computer Science, Law, and more—making AIRA a universal platform for discovery.

👥 Team Members
  
      Krishna Vamsi R

      Philippa Burgess
      
      Aryan Jaiswal
      
      Charishma Regulavalasa
