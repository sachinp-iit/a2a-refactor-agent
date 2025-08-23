# C# Auto-Refactor Agent (Multi-Agent + Approval Loop)

## Overview

The **C# Auto-Refactor Agent** is a **multi-agent system** designed using a **Blackboard pattern** to orchestrate automated code analysis and refactoring. It allows users to review and approve fixes interactively.

Key functionalities:

- Clone GitHub repositories and identify `.cs` files.  
- Perform static analysis using **Roslynator** to detect issues.  
- Store detected issues in **ChromaDB** for persistent querying and embedding-based search.  
- Multi-agent execution with **Agent-to-Agent (A2A) communication**.  
- Approval loop for each proposed fix — user decides whether to apply changes.  
- Optional commit back to the repository if fixes are applied.

This project is intended for **educational and non-commercial use** under a **CC BY-NC 4.0 license**.

---

## Features

- **Blackboard / Multi-Agent Architecture**
  - **Repo Manager Agent** — handles cloning and C# project discovery.  
  - **Roslynator Analyzer Agent** — performs static analysis and extracts issues.  
  - **Embedding Agent** — stores issue embeddings in ChromaDB.  
  - **Query Agent** — enables keyword-based issue search.  
  - **Refactor Agent** — proposes code fixes using GPT-4o-mini.  
  - **Approval Agent** — requests user approval before applying fixes.

- **Agent-to-Agent Communication (A2A)** — modular orchestration of agents.  
- **Persistent storage** — issues and embeddings stored in `chroma_db`.  
- **Interactive command-line interface** for workflow management.  

---

## Folder Structure

```
Multi-Agent-CSharp-Code-Refactor-with-Open-AI/
├── LICENSE
├── README.md
├── requirements.txt
├── install_dotnet_roslynator.sh
├── agents/
│   ├── approval_agent.py
│   ├── embedding_agent.py
│   ├── query_agent.py
│   ├── refactor_agent.py
│   ├── repo_manager.py
│   └── roslynator_agent.py
└── main.py
```

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/sachinp-iit/a2a-refactor-agent.git
cd a2a-refactor-agent
```

2. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

3. **Install .NET SDK and Roslynator CLI** (if not already installed)

---

## Usage

Run the main script:

```bash
python main.py
```

Follow the prompts:

1. Enter a GitHub repository URL.  
2. Review and approve each proposed fix.  
3. Optionally commit applied changes back to the repository.  

---

## Notes

- Requires **.NET SDK** and **Roslynator CLI** to analyze C# projects.  
- Persistent data (issues and embeddings) is stored in `chroma_db`.  
- Compatible with **Colab** and local Python environments.  

---
