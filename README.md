# SME Knowledge Base — MCP Server

This repository provides an **MCP (Model Context Protocol) server** that indexes documentation into **Elasticsearch** and exposes tools to query it from MCP-compatible clients such as **Claude Desktop**, **Cursor**, and **GitHub Copilot**.

---

## 📌 Features

- **Smart Indexing**: Uses deterministic IDs to prevent duplicate entries in Elasticsearch.
- **Semantic Search**: Query the knowledge base using Elasticsearch's matching capabilities.
- **Dynamic Updates**: Add new text content directly via MCP tools.
- **Robustness**: Gracefully handles database connection failures.

---

## Prerequisites

Before running the server, ensure the following are installed:

1. **Python 3.11+**
2. **Docker** (for running Elasticsearch)
3. **uv** (Python package and project manager)

---

## 📦 Setup

### 1. Start Elasticsearch
The server requires a running Elasticsearch instance. You can start one easily using Docker:

```bash
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e ES_JAVA_OPTS="-Xms1g -Xmx1g" \
  docker.elastic.co/elasticsearch/elasticsearch:9.1.5
```
*(Note: Ensure the version tag matches your requirements. Version 8.11.0 is used here as a stable default.)*

### 2. Install Dependencies
Navigate to the project directory and install the required Python packages:

```bash
uv sync
# OR
pip install -e .
```

### 3. Ingest Data
Place your PDF documents in the `input/` folder and run the extraction script to generate the `data/docs.json` index file:

```bash
uv run extraction.py
```

---

## 🧩 Configuration

To use this server with Claude Desktop, Cursor, or GitHub Copilot, you need to configure the MCP settings.

### 1. Locate Paths
You will need the absolute paths for both the `uv` executable and your cloned repository.

*   **Find `uv` path:**
    ```bash
    which uv
    ```
*   **Find Repository path:**
    ```bash
    pwd
    ```

### 2. Edit Configuration File
1.  Open **Claude Desktop**.
2.  Go to **Settings** > **Developer** > **Edit Config**.
3.  Add the following configuration to the `mcpServers` object in the JSON file:

```json
{
  "mcpServers": {
    "sme-knowledge-base": {
      "command": "/absolute/path/to/uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/my_server_sme",
        "elastic_server.py"
      ]
    }
  }
}
```
*Replace `/absolute/path/to/uv` and `/absolute/path/to/my_server_sme` with the actual paths identified in Step 1.*

---

## 🔧 Available Tools

The server exposes the following tools to the LLM:

| Tool Name | Description |
| :--- | :--- |
| **`ingest_pdfs`** | Scans the `input/` directory for new PDFs, extracts text, updates `docs.json`, and indexes everything into Elasticsearch. **Call this after adding new files.** |
| **`index_documents`** | Manually triggers the indexing process from `data/docs.json` to Elasticsearch. Useful if you've modified the JSON file directly. |
| **`add_text_to_index`** | Adds a new text document to the knowledge base. **Features:** <br>• Updates both persistent storage (`docs.json`) and Elasticsearch.<br>• Automatically chunks content > 1000 words.<br>• Generates unique IDs. |
| **`query_knowledge_base`** | Accepts a search query string and returns the top 2 most relevant document sections (Heading + Content). |

---

## 📖 Example Workflow

1.  **Start Elasticsearch**: Ensure your Docker container is running.
    ```bash
    docker start elasticsearch
    ```
2.  **Add Documents**: Drop any PDF files you want to index into the `input/` folder.
3.  **Start Server**: When you open Claude Desktop or Cursor, the server starts automatically.
    *   It will scan `input/`, extract text from new PDFs, and index them into Elasticsearch.
4.  **Interact**:
    *   "What does the document say about [topic]?" (Uses `query_knowledge_base`)
    *   "Add this meeting note to the knowledge base: [content]" (Uses `add_text_to_index`)

---

## Troubleshooting

*   **Connection Refused:** Ensure the Docker container is running (`docker ps`) and port 9200 is accessible.
*   **Path Errors:** Double-check that the paths in your config JSON are absolute (start with `/`) and point to the correct locations.