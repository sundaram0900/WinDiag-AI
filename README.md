# WinDiag AI

WinDiag AI is an AI-powered Windows troubleshooting and diagnostic assistant built with Python, LangChain, LangGraph, Hugging Face, Chroma, and Streamlit.

It combines Windows knowledge retrieval with live system diagnostics so the AI can both explain Windows problems and inspect the computer when required.

---

## Features

- AI-powered Windows troubleshooting
- RAG-based Windows knowledge base
- Semantic search using Chroma
- Document reranking
- Conversational query rewriting
- Query routing
- LangChain agent with tool calling
- Live CPU, RAM, disk, process, system and network diagnostics
- Internet speed testing
- Conversation memory
- Structured diagnostic responses
- Streamlit web interface
- Read-only diagnostic tools

---

## Architecture

```text
User
 ↓
Streamlit
 ↓
Query Router
 ↓
KNOWLEDGE / DIAGNOSTIC / BOTH
 ↓
LangChain Agent
 ↓
 ┌─────────────────────┐
 │                     │
 ▼                     ▼
Windows Knowledge    System Tools
 │                     │
 ▼                     ▼
Query Rewriting     CPU / RAM / Disk
 │                  Processes / Network
 ▼                     │
Chroma                  │
 │                     │
 ▼                     │
Qwen Reranker           │
 │                     │
 └──────────┬──────────┘
            ▼
        AI Response

```
## Tech Stack
| Component      | Technology                  |
| -------------- | --------------------------- |
| Language       | Python 3.12                 |
| LLM            | Qwen/Qwen3-4B-Instruct-2507 |
| Embeddings     | Qwen/Qwen3-Embedding-0.6B   |
| Reranker       | Qwen/Qwen3-Reranker-0.6B    |
| Agent          | LangChain + LangGraph       |
| Vector DB      | Chroma                      |
| Diagnostics    | psutil + Windows APIs       |
| UI             | Streamlit                   |
| Internet Speed | Ookla Speedtest CLI         |

## Models

## LLM
```
Qwen/Qwen3-4B-Instruct-2507
```
Used for:

* Agent reasoning

* Query routing

* Query rewriting

* Troubleshooting responses

* Structured responses

The LLM is accessed through Hugging Face.

## Embedding Model

```
Qwen/Qwen3-Embedding-0.6B
```

Used to convert Windows documentation and queries into vectors for semantic search.

## Reranker
```
Qwen/Qwen3-Reranker-0.6B
```

Used to rerank the documents retrieved from Chroma based on their relevance to the user's query.

The embedding and reranker models are downloaded automatically to the local Hugging Face cache when first required.

## Project Structure
```commandline
WinDiag AI/
│
├── agent/
│   ├── agent_core.py
│   ├── diagnostic_agent.py
│   ├── router.py
│   ├── response_schema.py
│   ├── response_formatter.py
│   └── approval.py
│
├── tools/
│   ├── cpu.py
│   ├── memory.py
│   ├── disk.py
│   ├── process.py
│   ├── system.py
│   ├── get_network_info.py
│   └── windows_knowledge.py
│
├── rag/
├── retrieval/
├── ingestion/
├── evaluation/
│
├── streamlit/
│   ├── app.py
│   └── dashboard_utils.py
│
├── vector_store/
│
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements
Windows 10/11\
Python 3.12\
Internet connection\
Hugging Face account and token

# Installation

Clone/download the project and open PowerShell in the project directory.

## 1. Create virtual environment
python -m venv .venv
## 2. Activate it
```
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:
```commandline
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

```

Then activate again:
```commandline
.\.venv\Scripts\Activate.ps1

```
## 3. Install dependencies
```commandline
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Verify installation
```commandline
python -c "import streamlit, langchain, langchain_huggingface, langchain_chroma, langgraph, chromadb, sentence_transformers, transformers, psutil; print('ALL IMPORTS OK')"

```

## Expected:
```commandline
ALL IMPORTS OK

```
## Hugging Face Configuration

Create a .env file in the project root:
```commandline
HF_TOKEN=your_huggingface_token_here

```

Use your own Hugging Face token.

Do not share  ```.env``` or upload it to GitHub.

Use ```.env.example``` as the template.

## Run the Application

Start Streamlit with:
```commandline
python -m streamlit run streamlit/app.py --server.fileWatcherType none

```

Then open:

```http://localhost:8501```

The ```--server.fileWatcherType none``` option avoids a Streamlit/PyTorch file-watcher issue that can occur with the local ML dependencies.

## Internet Speed Test

The Internet speed diagnostic uses the official Ookla Speedtest CLI.

Install it with:

```winget install Ookla.Speedtest.CLI```

After installation, open a new terminal and verify:

```speedtest --version```

The rest of WinDiag AI does not depend on the speed-test tool.

## Diagnostic Tools

WinDiag AI currently provides read-only tools for:

* CPU usage
* RAM usage
* System drive storage
* Top CPU processes
* Windows system information
* Network information
* Internet speed
* Windows troubleshooting knowledge

The tools only collect information. They do not modify the computer.

## Important Diagnostic Rules

The application distinguishes between observations and conclusions.

For example:

```RAM usage = 90%```

does not automatically prove:

```RAM is the confirmed cause of the slowdown.```

Similarly:

```Wi-Fi link speed = 1201 Mbps```

does not mean:

```Internet speed = 1201 Mbps```

The system attempts to avoid presenting measurements as confirmed causes without sufficient evidence.

## Error Handling

The application handles common runtime problems such as:

* Hugging Face/API errors
* Model loading failures
* Invalid router responses
* Invalid structured-response JSON
* Missing or inaccessible diagnostic information
* Streamlit/PyTorch file-watcher issues
* Missing dependencies

If the Hugging Face service temporarily returns an error such as ```500```, ```502```, ```503```, ```504```, or ```quota-related errors```, the application displays an appropriate error instead of crashing the UI.

The router and structured response components also validate model-generated JSON before using it.

## Common Errors
```ModuleNotFoundError```

Make sure the virtual environment is active and run:

```pip install -r requirements.txt```
## Hugging Face authentication error

Check that ```.env``` exists and contains:

```HF_TOKEN=your_token_here```
## Streamlit PyTorch watcher error

Run:

```python -m streamlit run streamlit/app.py --server.fileWatcherType none```
## Port already in use

Run Streamlit on another port:

```python -m streamlit run streamlit/app.py --server.port 8502 --server.fileWatcherType none```

Then open:

```http://localhost:8502```
## Models downloading for the first time

The embedding and reranker models are downloaded automatically on first use. The first run may therefore take longer.

## Important Files
```agent/agent_core.py```

Creates the LangChain agent, loads the model, registers tools, and manages conversation state.

```agent/router.py```

Classifies queries into:
```
KNOWLEDGE
DIAGNOSTIC
BOTH
```
```agent/diagnostic_agent.py```

Main backend entry point used by the CLI and Streamlit application.

```tools/```

Contains the Windows diagnostic and knowledge tools.

```retrieval/```

Contains retrieval and reranking logic.

```vector_store/```

Contains the pre-built Chroma vector database.

```streamlit/app.py```

Main Streamlit application.

## Important Note About ```vector_store```

The project already contains the Chroma vector store.

Do not delete or rebuild it during normal use.

The ingestion scripts are mainly for rebuilding/updating the knowledge base during development.

## Local Execution

WinDiag AI is designed to run locally when actual Windows diagnostics are required.

For example:
```
ur's Windows PC
        ↓
WinDiag AI
        ↓
Diagnostic Tools
        ↓
ur's CPU / RAM / Disk / Network
```

If the application is instead deployed to a cloud server, the diagnostic tools would inspect the cloud server rather than the user's personal computer.

## Example Queries

## Diagnostics
```
What is my CPU usage right now?
How much RAM am I using?
Which processes are using the most CPU?
What Windows version am I running?
What is my Internet speed right now?
```
## Windows Knowledge
```
How do I troubleshoot Wi-Fi problems in Windows?
How do I fix Windows Update problems?
```
## Combined Diagnosis
```
My laptop is very slow. Check my computer and tell me what I should do.
My Wi-Fi is slow. What should I check?
```

## Limitations
* Diagnostic measurements are point-in-time observations.
* A measurement does not automatically prove causation.
* Internet speed can vary between tests.
* Local embedding and reranker models require additional disk space and are downloaded on first use.
* The LLM requires an Internet connection through Hugging Face.
* The current diagnostic tools are read-only.

## Quick Start
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Create ```.env:```

```HF_TOKEN=your_huggingface_token_here```

Run:

```
python -m streamlit run streamlit/app.py --server.fileWatcherType none
```

Open:

```http://localhost:8501```

And the rest of the files in folder structure are only for testing , ClI , Bug fixing purpose only no need to touch them. 