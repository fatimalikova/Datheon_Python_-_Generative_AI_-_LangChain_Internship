# Python + Generative AI & LangChain Internship (Datheon)

Hands-on projects built during the Datheon Python + Generative AI & LangChain internship, using Python, Google Gemini and LangChain.

**Completed tasks:** all 4 tasks.

| Task | Project | Run command |
|------|---------|-------------|
| 1 | Structured LLM prompt pipeline and JSON extractor (invoice and resume) | `python -m task1_json_extractor.main --type invoice --file task1_json_extractor/samples/invoice.txt` |
| 2 | Document Q&A assistant with RAG and vector embeddings | `python -m task2_rag.main` |
| 3 | Multi-tool autonomous AI agent | `python -m task3_agent.agent` |
| 4 | Interactive full-stack AI chatbot with Streamlit | `streamlit run task4_streamlit/app.py` |

## Project structure

```
.
├── outputs/                  # saved results of Task 1
├── task1_json_extractor/     # prompts, Pydantic schemas, extraction script, sample documents
├── task2_rag/                # RAG pipeline (loader, splitter, ChromaDB, answer chain) and data/ folder
├── task3_agent/              # agent loop, tools and data/ folder
├── task4_streamlit/          # Streamlit chat UI (app.py)
├── config.py                 # loads settings from .env
├── requirements.txt
└── .env.example
```

## Setup

Requirements: Python 3.10 or newer and a free Gemini API key from https://aistudio.google.com

1. Clone the repository and open the project folder.
2. Create and activate a virtual environment (Windows):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   On Linux or macOS use `source venv/bin/activate`.
3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root (copy `.env.example`) and add your key:
   ```
   GOOGLE_API_KEY=your_key_here
   GEMINI_MODEL=gemini-3.1-flash-lite
   EMBED_MODEL=gemini-embedding-001
   ```

Run every command from the project root folder. The `.env` file is listed in `.gitignore` and is never uploaded.

## Task 1: Structured LLM Prompt Pipeline and JSON Extractor

Extracts structured data from unstructured text (invoices and resumes) and guarantees a valid JSON result.

How it works:
- `prompts.py` contains a parameterized prompt template with a few-shot example for each document type.
- `schemas.py` defines the expected output with Pydantic models (`Invoice`, `Resume`).
- `main.py` calls the Gemini API with JSON output enabled, validates the response with Pydantic, and retries with the validation error if the output is invalid. It also waits and retries when the API is temporarily overloaded.

Run:
```
python -m task1_json_extractor.main --type invoice --file task1_json_extractor/samples/invoice.txt
python -m task1_json_extractor.main --type resume --file task1_json_extractor/samples/resume.txt
```
Add `--out outputs/result.json` to save the result to a file. Saved examples are in `outputs/`.

Example output (invoice):
```json
{
  "invoice_number": "INV-2026-044",
  "date": "2026-10-12",
  "vendor": "BlueSky Software LLC",
  "customer": "Nova Trading",
  "items": [
    {"description": "Website maintenance", "quantity": 3.0, "unit_price": 120.0, "total": 360.0},
    {"description": "Hosting (annual)", "quantity": 1.0, "unit_price": 200.0, "total": 200.0}
  ],
  "subtotal": 560.0,
  "tax": 100.8,
  "total_amount": 660.8,
  "currency": "AZN"
}
```

## Task 2: Document Q&A Assistant with RAG and Vector Embeddings

Answers questions strictly from your own documents and shows where the answer came from.

How it works:
1. PDF and TXT files from `task2_rag/data/` are loaded with LangChain document loaders.
2. Text is split with `RecursiveCharacterTextSplitter` (chunk size 1000, overlap 150).
3. Chunks are embedded with Gemini embeddings and stored in a local ChromaDB database (`task2_rag/chroma_db/`, created on the first run).
4. For each question the 4 most relevant chunks are retrieved and passed to the model with an instruction to answer only from that context.
5. The answer is printed together with the source file name and page number.

Run:
```
python -m task2_rag.main
```
After adding or changing files in `task2_rag/data/`, rebuild the index:
```
python -m task2_rag.main --rebuild
```

If the answer is not in the documents, the assistant says so instead of guessing:
```
Sual: What is the capital of France?

Cavab: I could not find this in the documents.
```

Notes:
- PDFs must contain selectable text. Scanned PDFs (page images without text) return no content and would need OCR.
- Page numbers are shown for PDF files. Plain TXT files have no pages.
- The console prompts (`Sual`, `Cavab`, `Mənbələr`) are in Azerbaijani; the documents and answers can be in any language the model supports.

## Task 3: Multi-Tool Autonomous AI Agent

A console agent that decides by itself which tool to call, reads the result, and continues until it can give a final answer.

Tools:
- `web_search`: real-time web search with DuckDuckGo
- `calculator`: safe math evaluator (parses the expression instead of using `eval`)
- `read_file`: reads text files from `task3_agent/data/` (path traversal is blocked)

The console prints each step of the reasoning chain: thought, action, observation, final answer.

Run:
```
python -m task3_agent.agent
```

Example questions:
```
Read notes.txt and divide the budget by the team size
Read notes.txt, divide the budget by the team size, then search the web for the latest LangChain version
```

Example run:
```
Sual: Read notes.txt and divide the budget by the team size
[Step 1] Action: read_file({'filename': 'notes.txt'})
[Step 1] Observation: Project budget: 4500 AZN
Team size: 5 developers
Deadline: 2026-12-20
[Step 2] Action: calculator({'expression': '4500 / 5'})
[Step 2] Observation: 900.0

Final Answer:
900 AZN per developer.
```

Notes:
- Web search results come from DuckDuckGo and can be noisy or incomplete, so answers about the "latest version" of a fast-moving library may not be exact.
- The agent stops after a maximum of 8 steps.

## Task 4: Interactive Full-Stack AI Chatbot with Streamlit

Wraps the Task 2 RAG pipeline in a web chat interface.

Features:
- Streaming token output (`st.write_stream`)
- Chat history stored in `st.session_state`; the last 6 messages are passed to the model as conversation context
- Source file and page number shown under every answer
- Sidebar: upload a PDF (the documents are re-indexed) and clear the conversation

Run:
```
streamlit run task4_streamlit/app.py
```
Then open http://localhost:8501. On the first launch Streamlit asks for an email; leave it blank and press Enter.

Note: refreshing the browser page resets the conversation, because session state lives per browser session.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `404 NOT_FOUND ... model is no longer available` | Set another model in `.env`. List the models available to your key with the `google-genai` client (`client.models.list()`). |
| `503 UNAVAILABLE ... high demand` | Temporary. The scripts retry automatically. Try a `lite` model or wait a few minutes. |
| `403 PERMISSION_DENIED ... API has not been used` | Enable the Generative Language API for your Google project, or create a new key in AI Studio. |
| `GOOGLE_API_KEY not found` | Create the `.env` file in the project root. |
| Task 2 or Task 4 ignores new documents | Run `python -m task2_rag.main --rebuild`, or upload the PDF in the Streamlit sidebar. |

## Tech stack

Python 3, Google Gemini (`google-genai`, `langchain-google-genai`), LangChain, ChromaDB, Pydantic, Streamlit, DuckDuckGo Search (`ddgs`), pypdf
