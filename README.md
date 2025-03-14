# Query-Generator-Chatbot

This project is a web-based chatbot that translates natural language into Cypher queries using an open-source Hugging Face LLM and interacts with a Neo4j database.

## Features
- Converts natural language into Cypher queries
- Runs locally using FastAPI and Ollama
- Interfaces with Neo4j for querying relationships between genes and diseases
- Basic frontend for user interaction

## Project Structure
├── app.py         # Main FastAPI backend handling requests
├── model.py       # LLM model integration with Ollama
├── frontend.py    # Frontend for the chatbot interface
├── dataset/       # Contains the dataset used for training/testing
├── requirements.txt  # List of dependencies
├── README.md      # Project documentation

### Installation
Clone the repository and install dependencies:
