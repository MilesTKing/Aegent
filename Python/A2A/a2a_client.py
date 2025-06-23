import requests

A2A_URL = "http://localhost:9000/a2a"

def ask_agent(method, params, id_="1"):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": id_
    }
    response = requests.post(A2A_URL, json=payload)
    print("Status:", response.status_code)
    print("Response:", response.json())

# Example: Triage
ask_agent("triage", {"query": "Who was the first president of the United States?"}, id_="1")
ask_agent("triage", {"query": "What is 12 * 8?"}, id_="2")
ask_agent("triage", {"query": "Tell me about the French Revolution."}, id_="3")
