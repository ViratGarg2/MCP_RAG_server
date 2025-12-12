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
2. **Elasticsearch (single-node instance)**  
   If not already available, pull and run via Docker:

   ```bash
   docker run -d --name elasticsearch \
     -p 9200:9200 -p 9300:9300 \
     -e "discovery.type=single-node" \
     -e "xpack.security.enabled=false" \
     -e ES_JAVA_OPTS="-Xms1g -Xmx1g" \
     docker.elastic.co/elasticsearch/elasticsearch:9.1.5
uv package manager (recommended)
Install uv:
pip install uv
Verify installation:
which uv
📦 Setup
Clone the repository and install dependencies:
pip install -e .
This installs the project in editable mode.
▶️ Running the MCP Server
You can run the server in two ways:
1. Using the MCP CLI (recommended)
mcp run src/elastic_server.py
2. Using Python directly
python src/elastic_server.py
🔧 Available MCP Tools
1. index_documents
Reads data/docs.json
Flattens nested structures
Indexes all documents into Elasticsearch
Run this once after installation to populate the database.
2. query_knowledge_base
Accepts a natural-language query
Returns the top 2 matching document sections, including heading + content
🧩 Adding This Server to Claude / Cursor / Copilot
After running Elasticsearch and installing uv:
Find the absolute path of uv:
which uv
Find the absolute path of your cloned repository.
Open your MCP configuration:
Claude Desktop
Settings → Developer Settings → MCP Servers
Click Edit Config
Cursor / Copilot Chat
Open your MCP JSON configuration file.
Add this block to the config:
{
  "mcpServers": {
    "sme-knowledge-base": {
      "command": "ABSOLUTE_PATH_TO_UV",
      "args": [
        "run",
        "--directory",
        "ABSOLUTE_PATH_TO_CLONED_REPO",
        "elastic_server.py"
      ]
    }
  }
}
Replace:
"ABSOLUTE_PATH_TO_UV" with the output of which uv
"ABSOLUTE_PATH_TO_CLONED_REPO" with your repo directory path
Restart your IDE/assistant after saving the config.
📖 Example Workflow
Start Elasticsearch
add pdf files to be given as input to my_server_sme/input folder,which would be indexed whenever required by claude
Start the MCP server
From Claude/Cursor, run:
index_documents
Query the knowledge base:
query_knowledge_base: "Explain how indexing works."
📝 Notes
Ensure Elasticsearch is running before starting the server
Run index_documents only when docs change
Existing structure is designed for easy extension