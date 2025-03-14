import gradio as gr
import requests

def ask_question(question):
    url = "http://127.0.0.1:8000/generate-cypher/"
    headers = {"Content-Type": "application/json"}
    payload = {"question": question}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["query"]
    else:
        return f"Error: {response.status_code} - {response.text}"

gr.Interface(
    fn=ask_question,
    inputs="text",
    outputs="text",
    title="Cypher Query Generator",
).launch()
