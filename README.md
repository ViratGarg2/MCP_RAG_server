# 🚀 SME Knowledge Base — MCP Server

This repository provides an **MCP (Model Context Protocol) server** that indexes documentation into **Elasticsearch** and exposes tools to query it from MCP-compatible clients such as **Claude Desktop**, **Cursor**, and **GitHub Copilot**.

---

## 📌 Features

- Index documentation (`docs.json`) into Elasticsearch
- Query the knowledge base using semantic search
- Integrates seamlessly with any MCP-enabled environment
- Lightweight, fast, and easy to extend

---

## 🛠 Prerequisites

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
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
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
| **`index_documents`** | Reads the processed data from `data/docs.json`, flattens the structure, and indexes it into Elasticsearch. **This must be called once to populate the database.** |
| **`query_knowledge_base`** | Accepts a search query string and returns the most relevant document sections (Heading and Content) from the knowledge base. |

---

## 📖 Example Workflow

1.  **Start Elasticsearch** (Docker).
2.  **Add PDF files** to the `input/` folder.
3.  **Run Extraction**: `uv run extraction.py`.
4.  **Start the MCP Server** (via Claude/Cursor).
5.  **Index Data**: Ask Claude to "Index the documents".
6.  **Query**: Ask questions like "Explain how indexing works."

---

## 📝 Troubleshooting

*   **Connection Refused:** Ensure the Docker container is running (`docker ps`) and port 9200 is accessible.
*   **Path Errors:** Double-check that the paths in your config JSON are absolute (start with `/`) and point to the correct locations.