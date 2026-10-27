# Small Business AI Assistant

An LLM-powered product assistant designed to help small businesses answer customer questions using a product catalogue and an MCP-based stock-checking tool.

**Live Demo:** https://agentic-ai-lab-voice-assistant.streamlit.app/  
**Source Code:** https://github.com/Divyanshu0Raj/agentic-ai-lab/tree/main/01-small-business-voice-agent

---

## Overview

The Small Business AI Assistant combines a language model with structured product data to produce concise, context-grounded answers. Customers can ask questions about products, descriptions, categories, and budgets. For stock-related questions, the application can invoke a dedicated Model Context Protocol (MCP) tool to retrieve product availability and pricing from the catalogue.

The project explores practical building blocks for agentic AI applications: LLM integration, retrieval, tool calling, configuration management, and latency measurement.

## Features

- **LLM-powered answers** — generates concise responses using the Groq API.
- **Product catalogue retrieval** — matches questions against product names, categories, and descriptions.
- **Budget-aware filtering** — supports price limits such as “under ₹1,500.”
- **MCP stock-checking tool** — checks a product's availability and price through a FastMCP tool.
- **Grounded responses** — supplies retrieved records to the model and instructs it not to invent product prices or stock information.
- **Latency visibility** — displays retrieval time, LLM response time, and the number of retrieved products.
- **Streamlit interface** — offers a simple web UI for asking product-related questions.
- **Environment-based configuration** — keeps the Groq API key outside the application source code.

## Try the Demo

Open the [live application](https://agentic-ai-lab-voice-assistant.streamlit.app/) and enter a product-related question.

Example questions:

- `What audio products are available?`
- `Show me products under ₹1,500`
- `Is SoundBeat Wireless Earbuds in stock?`
- `What is the price of product P002?`

The sample catalogue is stored in `data/products.json`. Results depend on the product records included in that file.

## How It Works

1. **Receive a question:** The user enters a question in the Streamlit interface.
2. **Identify the query type:** The application checks whether the question asks about stock or availability.
3. **Retrieve relevant data:**
   - For general product questions, a lightweight keyword and budget filter searches the local JSON catalogue.
   - For stock questions, the application resolves a product ID and calls the `get_product_stock` MCP tool.
4. **Build grounded context:** The relevant product records or stock result are passed to the language model with instructions to avoid unsupported claims.
5. **Generate the answer:** Groq runs the configured model and returns a natural-language response.
6. **Display timing information:** The UI shows retrieval latency, LLM latency, and the number of returned products.

## Architecture

```text
                     Customer Question
                            |
                            v
                     Streamlit UI
                            |
                            v
                   Question Processing
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          Product Query          Stock Query
                 |                     |
                 v                     v
        products.json          FastMCP Client
                 |                     |
                 |                     v
                 |             get_product_stock
                 |                     |
                 |                     v
                 |          Product Stock Lookup
                 |                     |
                 +----------+----------+
                            |
                            v
                    Context + Question
                            |
                            v
                       Groq LLM
                            |
                            v
                    Generated Answer
                            |
                            v
                 Answer + Latency Metrics
```

## Technology Stack

| Technology | Purpose in this project |
|---|---|
| **Python** | Application logic, product retrieval, configuration, and tool implementation. |
| **Streamlit** | Web interface for entering questions and displaying answers and timing metrics. |
| **Groq API / Groq Python SDK** | Sends prompts to the configured language model and receives generated answers. |
| **FastMCP** | Defines the `get_product_stock` tool and makes it callable through an MCP client. |
| **Model Context Protocol (MCP)** | Provides a structured interface for invoking the stock-checking tool. |
| **JSON** | Stores the sample product catalogue and structured product attributes. |
| **python-dotenv** | Loads local environment variables from a `.env` file. |
| **pytest** | Included as a dependency for testing as the project develops. |

## Project Structure

```text
01-small-business-voice-agent/
├── data/
│   └── products.json       # Sample product catalogue
├── src/
│   ├── __init__.py
│   ├── config.py           # Loads Groq configuration
│   ├── llm.py              # Retrieval, MCP calls, prompts, and LLM requests
│   ├── main.py             # Streamlit application entry point
│   ├── mcp_server.py       # FastMCP server and stock tool registration
│   └── tools.py            # Product stock-checking logic
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
└── README.md
```

## Run Locally

### 1. Clone the repository

Run these commands from your terminal:

```bash
git clone https://github.com/Divyanshu0Raj/agentic-ai-lab.git
cd agentic-ai-lab/01-small-business-voice-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Linux / macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example configuration:

```bash
cp .env.example .env
```

Open `.env` and set your Groq API key and model:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Use a valid model ID available to your Groq account. Do not commit your real API key or share it publicly.

### 5. Start the application

Run Streamlit from the `01-small-business-voice-agent` directory:

```bash
streamlit run src/main.py
```

Streamlit will print a local URL in the terminal. Open that URL in your browser.

## Product Catalogue

The sample dataset is in `data/products.json`. Each record contains:

| Field | Description |
|---|---|
| `id` | Unique product identifier, such as `P001`. |
| `name` | Product name. |
| `category` | Product category. |
| `price_inr` | Price in Indian rupees. |
| `in_stock` | Stock availability as a Boolean value. |
| `description` | Short product description. |

You can extend the catalogue by adding records that follow the same schema.

## MCP Tool

The project exposes a tool named `get_product_stock` through FastMCP.

**Input:** `product_id`, for example `P001`.

**Output:** A structured result containing whether the product was found and, when available, its ID, name, stock status, and price.

The LLM pipeline calls this tool for stock-related questions and uses the tool result as the source of truth for stock status and pricing. This separates deterministic product lookup from natural-language response generation.

## Performance Metrics

The application displays:

- **Retrieval:** time spent finding matching products for general product questions.
- **LLM:** time spent waiting for the model response.
- **Products found:** number of product records returned for the query.

For stock-related requests, the application also measures MCP-call latency internally. Observed latency varies with network conditions, model availability, and deployment resources; this README does not assume a fixed response-time benchmark.

## Security

- Store API keys in environment variables, not in source code.
- Keep `.env` out of version control.
- Use `.env.example` to document required configuration without exposing secrets.
- Do not treat model-generated text as the source of truth for stock or pricing; use the structured catalogue/tool result.

## Current Scope

This version is a **text-based product assistant** with an MCP stock-checking tool. The repository's broader direction includes voice interaction and other agentic capabilities, but microphone capture, speech-to-text, and text-to-speech should be described as implemented only once they are present in the application code.

The current retrieval approach is a lightweight keyword and budget filter over a JSON file, not a vector database or embedding-based semantic search system.

## Future Improvements

- Add microphone input and speech-to-text.
- Add text-to-speech for spoken responses.
- Expand the MCP toolset with validated product search and other safe business operations.
- Improve retrieval with ranking, synonyms, and more robust query parsing.
- Add automated tests for retrieval, stock lookup, and response handling.
- Persist structured logs and track latency across requests.
- Replace the sample JSON catalogue with a database or inventory API.

## Learning Outcomes

This project provides hands-on practice with:

- Integrating a hosted LLM into a Python application.
- Building a small retrieval-and-generation pipeline.
- Exposing application functionality as an MCP tool.
- Passing structured context to an LLM to reduce unsupported answers.
- Managing secrets with environment variables.
- Measuring latency across application components.
- Deploying a Python application using Streamlit.

## Author

**Divyanshu Singh Nathawat**

- GitHub: [@Divyanshu0Raj](https://github.com/Divyanshu0Raj)
- Project: [Agentic AI Lab](https://github.com/Divyanshu0Raj/agentic-ai-lab)

---

If you find this project useful, consider starring the repository.
