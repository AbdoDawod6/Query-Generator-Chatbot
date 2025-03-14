import ollama
from neo4j import GraphDatabase

# Neo4j Connection Details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "123456789"

# Connect to Neo4j
def connect_to_neo4j():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        return driver
    except Exception as e:
        print(f"❌ Error connecting to Neo4j: {e}")
        return None

# Function to generate a valid Cypher query
def generate_cypher_query(user_question):
    full_prompt = f"""
    You are a Neo4j Cypher query expert. Generate a precise Cypher query based on the user question. **Strictly follow these rules**:

    1️⃣ **ONLY return the Cypher query** (no explanations, no comments).
    2️⃣ **Start the response with `MATCH`**.
    3️⃣ **Ensure the query is syntactically correct for Neo4j**.
    4️⃣ **Do not include any additional text, headers, or formatting**.

    ### **Schema**
    - `(:Gene)-[:ASSOCIATED_WITH]->(:Disease)`
    - `(:Gene)-[:REGULATES]->(:Protein)`
    - `(:Disease)-[:HAS_SYMPTOM]->(:Symptom)`
    - `(:Gene)-[:INTERACTS_WITH]->(:Gene)`

    ### **Examples**
    **Q:** Find genes related to Lung Cancer.  
    **A:** MATCH (g:Gene)-[:ASSOCIATED_WITH]->(d:Disease {{name: "Lung Cancer"}}) RETURN g.name;

    **Q:** Find all relationships for the gene "APOE".  
    **A:** MATCH (g:Gene {{name: "APOE"}})-[r]->(n) RETURN type(r), labels(n), n.name;

    **Q:** Find diseases related to the gene "TP53".  
    **A:** MATCH (g:Gene {{name: "TP53"}})-[:ASSOCIATED_WITH]->(d:Disease) RETURN d.name;

    ### **User Question:**
    {user_question}
    """

    print("\n[🔹 Sending prompt to Ollama LLM...]")
    try:
        response = ollama.chat(
            model="deepseek-coder:1.3b",
            messages=[{"role": "system", "content": "Generate a Cypher query."},
                      {"role": "user", "content": full_prompt}]
        )

        cypher_response = response['message']['content']

        # Extract only the valid Cypher query
        cypher_start = cypher_response.find("MATCH")
        cypher_end = cypher_response.find(";") + 1  # Ensure full query is captured

        if cypher_start != -1 and cypher_end != -1:
            cypher_query = cypher_response[cypher_start:cypher_end].strip()
        else:
            print("❌ No valid query generated.")
            return None

        print(f"\n[✅ Generated Cypher Query]\n{cypher_query}")
        return cypher_query

    except Exception as e:
        print(f"❌ Error generating Cypher query: {e}")
        return None

# Function to run Cypher query in Neo4j
def run_cypher_query(cypher_query):
    driver = connect_to_neo4j()
    if not driver:
        return {"error": "Failed to connect to Neo4j."}

    try:
        with driver.session() as session:
            result = session.run(cypher_query)
            records = [record.data() for record in result]
            return {"query": cypher_query, "results": records}

    except Exception as e:
        return {"error": str(e)}

    finally:
        driver.close()

# Main execution
if __name__ == "__main__":
    user_question = input("\nEnter your question: ")
    cypher_query = generate_cypher_query(user_question)

    if cypher_query:
        print("\n[🔹 Sending query to Neo4j...]")
        query_results = run_cypher_query(cypher_query)
        print("\n[🔹 Neo4j Query Results]")
        print(query_results)
