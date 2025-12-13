from typing import Any, Dict, List
import json
import os
import sys
import subprocess
import time
import uuid
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
def add_text_to_index(title: str, content: str) -> str:
    """
    Adds a new text document to the knowledge base.
    If the content exceeds 1000 words, it will be chunked into smaller documents.
    Updates both the persistent JSON storage and the Elasticsearch index.
    
    Args:
        title: A descriptive title for the text.
        content: The actual text content to index.
    """
    # Helper to split into chunks
    words = content.split()
    CHUNK_SIZE = 1000
    
    chunks = []
    if len(words) <= CHUNK_SIZE:
        chunks.append((title, content))
    else:
        for i in range(0, len(words), CHUNK_SIZE):
            chunk_words = words[i:i + CHUNK_SIZE]
            chunk_content = " ".join(chunk_words)
            part_num = (i // CHUNK_SIZE) + 1
            total_parts = (len(words) + CHUNK_SIZE - 1) // CHUNK_SIZE
            chunk_title = f"{title} (Part {part_num}/{total_parts})"
            chunks.append((chunk_title, chunk_content))

    # Prepare data for storage and indexing
    new_entries = {}
    es_docs = []
    
    for chunk_title, chunk_content in chunks:
        doc_id = str(uuid.uuid4())
        new_entries[doc_id] = {
            "title": chunk_title,
            "content": chunk_content,
            "source": "user_input",
            "subsections": {}
        }
        es_docs.append({
            "id": doc_id,
            "title": chunk_title,
            "content": chunk_content
        })

    # Update docs.json
    file_path = os.path.join(os.path.dirname(__file__), "data", "docs.json")
    
    try:
        data = {}
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass 
        
        data.update(new_entries)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        return f"Error updating local storage: {str(e)}"

    # Index to Elasticsearch
    try:
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(index=INDEX_NAME)
            
        for doc in es_docs:
            es.index(index=INDEX_NAME, id=doc["id"], document=doc)
        
        if len(chunks) == 1:
            return f"Successfully added document '{title}' (ID: {es_docs[0]['id']}) to index and storage."
        else:
            return f"Successfully added document '{title}' split into {len(chunks)} parts to index and storage."
        
    except Exception as e:
        return f"Error indexing to Elasticsearch: {str(e)}"

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
