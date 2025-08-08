# C# Auto-Refactor Agent (Multi-Agent + Approval Loop)

## Overview
This project is a **multi-agent C# Auto-Refactor Agent** that:

1. **Clones a GitHub repo** and extracts `.cs` files.  
2. **Runs Roslynator analysis** to detect issues.  
3. **Stores analysis in ChromaDB** for interactive exploration.  
4. **Supports multi-agent execution** with Agent-to-Agent (A2A) communication.  
5. **Approval loop** for each suggested fix — you decide whether to apply it.  
6. **Optional commit** back to the repo if any changes are applied.  

This is designed for **educational/training use only** under a **CC BY-NC 4.0 license**.

---

## Features
- **Multi-Agent Design**  
  - **Repo Manager Agent** — handles cloning and file extraction  
  - **Analyzer Agent** — runs Roslynator and stores results  
  - **Refactor Agent** — proposes fixes using GPT-4o-mini  
  - **Approval Agent** — asks you before applying each fix  
- **Agent-to-Agent (A2A) communication** for modular orchestration  
- **Non-commercial license** (CC BY-NC 4.0)  
- **Colab-compatible** execution  

---

## Folder Structure
```
a2a_refactor_agent/
│
├── LICENSE
├── README.md
├── requirements.txt
│
├── agents/
│   ├── repo_manager.py
│   ├── analyzer.py
│   ├── refactor.py
│   └── approval.py
│
└── main.py
```

---

## Installation
1. **Clone this repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/a2a_refactor_agent.git
   cd a2a_refactor_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage
Run the main entry point:
```bash
python main.py
```

You will be prompted to:
1. Enter a GitHub repository URL.  
2. Approve or skip each proposed fix.  
3. Optionally commit changes.

---

## License
This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License** — see the [LICENSE](LICENSE) file for details.

---

## Educational Use
This project is intended for:
- AI agent orchestration training  
- Multi-agent communication examples  
- Code analysis & refactoring demos  

**Commercial use is prohibited**.
