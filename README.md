# C# Auto-Refactor Agent (Multi-Agent + Approval Loop)

## Overview
This project is a **multi-agent C# Auto-Refactor system** designed using a **Blackboard pattern** for orchestrating multi-agent interactions. It allows automated code analysis and refactoring while keeping the user in the loop for approval.

Key functionalities:

- Clone GitHub repositories and extract `.cs` files.  
- Run static analysis using Roslynator to detect code issues.  
- Store analysis results in **ChromaDB** for persistent querying and refactoring.  
- Multi-agent execution with **Agent-to-Agent (A2A) communication**.  
- Approval loop for each proposed fix — user can approve or skip changes.  
- Optional commit back to the repository if fixes are applied.

This project is intended for **educational/training purposes** under a **CC BY-NC 4.0 license**.

---

## Features

- **Blackboard / Multi-Agent Architecture**
  - **Repo Manager Agent** — handles cloning and C# file discovery.  
  - **Roslynator Analyzer Agent** — runs static analysis and generates issue embeddings.  
  - **Embedding Agent** — stores issue embeddings in ChromaDB.  
  - **Query Agent** — allows keyword search across detected issues.  
  - **Refactor Agent** — proposes code fixes using GPT-4o-mini.  
  - **Approval Agent** — requests user approval before applying any fixes.  

- **Agent-to-Agent Communication (A2A)** for modular orchestration.  
- **Persistent storage** using ChromaDB for issues and embeddings.  
- **Interactive command-line interface** for flexible workflows.  

---

## Folder Structure

Multi-Agent-CSharp-Code-Refactor-with-Open-AI/
│
├── LICENSE
├── README.md
├── requirements.txt
├── install_dotnet_roslynator.sh
│
├── agents/
│ ├── approval_agent.py
│ ├── embedding_agent.py
│ ├── query_agent.py
│ ├── refactor_agent.py
│ ├── repo_manager.py
│ └── roslynator_agent.py
│
└── main.py


---

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/sachinp-iit/a2a-refactor-agent.git
cd a2a-refactor-agent

2. **Install Python dependencies**
```bash
pip install -r requirements.txt

**Usage**
Run the main script:
```bash
python main.py

**Follow the prompts to:**
1. Enter a GitHub repository URL.
2. Approve or skip each proposed fix.
3. Optionally commit changes back to the repo.

## Notes
Ensure .NET SDK and Roslynator CLI are installed on your system.
The system is compatible with Colab and local Python environments.
All embeddings and issue data are stored persistently in chroma_db.
