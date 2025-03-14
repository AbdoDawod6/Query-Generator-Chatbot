from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
import ollama
import re

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the GSoC Chatbot API! Visit /docs for Swagger UI."}

# Neo4j Database Credentials
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "123456789"

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Request Model for API
class QueryRequest(BaseModel):
    question: str

# Define Schema for Neo4j Data
SCHEMA = """
(:Gene)-[:ASSOCIATED_WITH]->(:Disease)
(:Gene)-[:INTERACTS_WITH]->(:Gene)
(:Disease)-[:HAS_SYMPTOM]->(:Symptom)
"""

# Example Queries for LLM
EXAMPLES = """
1. Find all genes related to Lung Cancer:
   MATCH (g:Gene)-[:ASSOCIATED_WITH]->(d:Disease {name: "Lung Cancer"}) RETURN g.name;

2. Find all diseases associated with a specific gene:
   MATCH (g:Gene {name: "APOE"})-[:ASSOCIATED_WITH]->(d:Disease) RETURN d.name;
"""

@app.post("/generate-cypher/")
def generate_cypher(request: QueryRequest):
    """ Generate Cypher Query from Natural Language """
    
    prompt = f"""
    Convert the following question into a valid Cypher MATCH query. Only return the query itself.
    
    ### Schema ###
    {SCHEMA}
    
    ### Example Queries ###
    {EXAMPLES}
    
    Question: {request.question}
    """

    print("[🔹 Sending prompt to Ollama LLM...]")
    try:
        response = ollama.chat(
            model="deepseek-coder:1.3b",
            messages=[
                {"role": "system", "content": "Generate a valid Cypher MATCH query. Only return the query itself."},
                {"role": "user", "content": prompt}
            ]
        )
        raw_cypher_query = response["message"]["content"].strip()

        # Extract Cypher query without explanations
        cypher_query = extract_cypher_query(raw_cypher_query)
        if not cypher_query:
            print("[❌ Ollama generated an invalid Cypher Query!]")
            raise HTTPException(status_code=400, detail="Failed to generate a valid Cypher query.")

        print(f"[✅ Extracted Cypher Query]: {cypher_query}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

    return run_cypher_query(cypher_query)


def extract_cypher_query(text):
    """ Extracts the actual Cypher query from LLM response """
    match = re.search(r"MATCH\s+\(.*", text, re.IGNORECASE)
    if match:
        return match.group(0).strip()  # Return only the Cypher query
    return None  # No valid query found


def run_cypher_query(query: str):
    """ Executes Cypher query in Neo4j and returns results """
    try:
        with driver.session() as session:
            result = session.run(query)
            data = [record.data() for record in result]
            print("[🔹 Neo4j Query Results]", data)
            return {"query": query, "results": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neo4j Error: {str(e)}")

# Run FastAPI with: uvicorn app:app --reload
