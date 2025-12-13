from typing import Any, Dict, List
import json
import os
import sys
import subprocess
import time
import uuid
from mcp.server.fastmcp import FastMCP
from elasticsearch import Elasticsearch
from extraction import process_all_pdfs

# Initialize FastMCP server
mcp = FastMCP("sme-elastic")

# Elasticsearch client configuration
# Assuming Elasticsearch is running locally on default port
ES_HOST = os.environ.get("ES_HOST", "http://localhost:9200")
es = Elasticsearch(ES_HOST)
INDEX_NAME = "sme-docs"

def check_elasticsearch_running():
    """Checks if Elasticsearch is reachable."""
    try:
        if es.ping():
            return True
        return False
    except Exception:
        return False

def flatten_docs(docs_dict: Dict[str, Any]) -> List[Dict[str, str]]:
    """Recursively flatten the nested docs structure."""
    documents = []
    for key, value in docs_dict.items():
        # Use the pre-generated deterministic doc_id if available, otherwise fallback to key
        doc_id = value.get("doc_id", key)
        
        doc = {
            "id": doc_id,
            "title": value.get("title", ""),
            "content": value.get("content", ""),
            "source": value.get("source", "unknown")
        }
        documents.append(doc)
        if "subsections" in value:
            documents.extend(flatten_docs(value["subsections"]))
    return documents

def _perform_indexing() -> str:
    if not check_elasticsearch_running():
        return (
        "Error: Elasticsearch is not running.\n\n"
        "Please start the Docker container by pulling the Elasticsearch image and running:\n\n"
        "docker run -d --name elasticsearch \\\n"
        "  -p 9200:9200 -p 9300:9300 \\\n"
        "  -e \"discovery.type=single-node\" \\\n"
        "  -e \"xpack.security.enabled=false\" \\\n"
        "  -e ES_JAVA_OPTS=\"-Xms1g -Xmx1g\" \\\n"
        "  docker.elastic.co/elasticsearch/elasticsearch:9.1.5"
    )


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
def index_documents() -> str:
    """
    Reads documents from data/docs.json and indexes them into Elasticsearch.
    Call this tool to initialize or update the knowledge base.
    """
    return _perform_indexing()



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
    if not check_elasticsearch_running():
        return "Error: Elasticsearch is not running. Please start the Docker container."

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
    if not check_elasticsearch_running():
        return "Error: Elasticsearch is not running. Please start the Docker container."

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
    
@mcp.tool()
def ingest_pdfs() -> str:
    """
    Takes all documents currently in input folder and creates output.json to process them
    add them to index to enable knowledge base powered querying.
    """
    try:
        process_all_pdfs()
        return "PDF extraction completed successfully."
    except Exception as e:
        return f"PDF extraction failed: {e}"


if __name__ == "__main__":
    print("MCP server started", file=sys.stderr)
    print("CWD:", os.getcwd(), file=sys.stderr)
    print("Script dir:", os.path.dirname(__file__), file=sys.stderr)

    if check_elasticsearch_running():
        print("Elasticsearch is running. Proceeding with auto-ingestion...", file=sys.stderr)
        
        # Auto-index on startup
        try:
            print("Running startup extraction...", file=sys.stderr)
            # process_all_pdfs()
            print("PDF extraction complete.", file=sys.stderr)
        except Exception as e:
            print(f"Warning: PDF extraction failed: {e}", file=sys.stderr)
        
        try:
            print("Running startup indexing...", file=sys.stderr)
            # result = _perform_indexing()
            # print(result, file=sys.stderr)
        except Exception as e:
            print(f"Warning: Initial indexing failed: {e}", file=sys.stderr)
    else:
        print("Warning: Elasticsearch is NOT running. Search tools will return errors.", file=sys.stderr)
        print("Please start it with: docker start elasticsearch", file=sys.stderr)
    
    mcp.run(transport='stdio')
