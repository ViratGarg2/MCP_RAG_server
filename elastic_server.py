from typing import Any, Dict, List
import json
import os
import sys
import subprocess
import time
from mcp.server.fastmcp import FastMCP
from elasticsearch import Elasticsearch

# Initialize FastMCP server
mcp = FastMCP("sme-elastic")

# Elasticsearch client configuration
# Assuming Elasticsearch is running locally on default port
ES_HOST = os.environ.get("ES_HOST", "http://localhost:9200")
es = Elasticsearch(ES_HOST)
INDEX_NAME = "sme-docs"

def ensure_elasticsearch_running():
    """Checks if Elasticsearch is running, starts it if not."""
    container_name = "elasticsearch"
    
    # Check if docker is available
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: Docker is not running or not installed. Cannot auto-start Elasticsearch.", file=sys.stderr)
        return

    # Check if container is running
    res = subprocess.run(["docker", "ps", "-q", "-f", f"name={container_name}"], capture_output=True, text=True)
    if res.stdout.strip():
        return # Already running

    # Check if container exists (stopped)
    res = subprocess.run(["docker", "ps", "-aq", "-f", f"name={container_name}"], capture_output=True, text=True)
    if res.stdout.strip():
        print(f"Starting existing {container_name} container...", file=sys.stderr)
        subprocess.run(["docker", "start", container_name], check=True)
    else:
        print(f"Creating and starting {container_name} container...", file=sys.stderr)
        subprocess.run([
            "docker",
            "run", "-d", "--name", container_name,
            "-p", "9200:9200", "-p", "9300:9300",
            "-e", "discovery.type=single-node",
            "-e", "xpack.security.enabled=false",
            "-e", "ES_JAVA_OPTS=-Xms1g -Xmx1g",
            "docker.elastic.co/elasticsearch/elasticsearch:8.11.0"
        ], check=True)
    
    # Wait for it to be ready
    print("Waiting for Elasticsearch to initialize...", file=sys.stderr)
    time.sleep(15)

def flatten_docs(docs_dict: Dict[str, Any]) -> List[Dict[str, str]]:
    """Recursively flatten the nested docs structure."""
    documents = []
    for key, value in docs_dict.items():
        doc = {
            "id": key,
            "title": value.get("title", ""),
            "content": value.get("content", "")
        }
        documents.append(doc)
        if "subsections" in value:
            documents.extend(flatten_docs(value["subsections"]))
    return documents

@mcp.tool()
def index_documents() -> str:
    """
    Reads documents from data/docs.json and indexes them into Elasticsearch.
    Call this tool to initialize or update the knowledge base.
    """
    file_path = os.path.join(os.path.dirname(__file__), "data", "docs.json")
    
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        docs = flatten_docs(data)
        
        # Create index if not exists
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(index=INDEX_NAME)
            
        # Index documents
        count = 0
        for doc in docs:
            # Using 'id' from the doc as the ES document ID to prevent duplicates
            es.index(index=INDEX_NAME, id=doc["id"], document=doc)
            count += 1
            
        return f"Successfully indexed {count} documents into '{INDEX_NAME}'."
    except Exception as e:
        return f"Error indexing documents: {str(e)}"

@mcp.tool()
def query_knowledge_base(query: str) -> str:
    """
    Query the knowledge base for relevant documents.
    Returns the top-2 documents' content and heading to be used as context.
    
    Args:
        query: The search query string.
    """
    try:
        if not es.indices.exists(index=INDEX_NAME):
            return "Error: Index does not exist. Please run 'index_documents' first."

        # Search query targeting title and content
        search_body = {
            "size": 2,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^2", "content"] # Boost title slightly
                }
            }
        }
        
        response = es.search(index=INDEX_NAME, body=search_body)
        hits = response['hits']['hits']
        
        if not hits:
            return "No relevant documents found."
            
        result_parts = []
        for hit in hits:
            source = hit['_source']
            title = source.get('title', 'No Title')
            content = source.get('content', 'No Content')
            result_parts.append(f"Heading: {title}\nContent: {content}")
            
        return "\n\n---\n\n".join(result_parts)
    except Exception as e:
        return f"Error querying knowledge base: {str(e)}"

if __name__ == "__main__":
    ensure_elasticsearch_running()
    mcp.run(transport='stdio')
