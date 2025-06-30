# Multi-Agent A2A/MCP System

This project implements a robust, standards-compliant multi-agent system supporting both the [A2A protocol](https://github.com/modelcontextprotocol/a2a) and the [MCP protocol](https://github.com/modelcontextprotocol/mcp). It features:
- Triage-based agent routing (math, history, biology, psychology, ELA, Spanish, coffee, time)
- Secure guardrails
- Integration with external MCP servers (e.g., time, fetch)
- Modern GUI client (PySide6)

## Requirements
- Python 3.9+
- [OpenAI Python SDK](https://pypi.org/project/openai/) (latest)
- [httpx](https://www.python-httpx.org/)
- [fastapi](https://fastapi.tiangolo.com/)
- [uvicorn](https://www.uvicorn.org/)
- [PySide6](https://pypi.org/project/PySide6/)

Install dependencies:
```sh
pip install -r requirements.txt
```

## Environment Setup
Set your OpenAI API key:
```sh
export OPENAI_API_KEY=sk-...
```

## Running the Agent System

### 1. Start the A2A/MCP Agent Server
```sh
python -m uvicorn A2A.a2a_agent:app --host 0.0.0.0 --port 9000
```
- The A2A endpoint will be at `http://localhost:9000/a2a`
- The MCP server (if enabled) will run on port 8090 by default

### 2. Configure External MCP Servers (Optional)
To use external MCP servers (e.g., time, fetch), create `~/.vscode/mcp.json`:
```json
{
  "servers": [
    {"name": "time", "url": "http://localhost:8000/mcp/"},
    {"name": "fetch", "url": "http://localhost:8001/mcp/"},
    {"name": "server_chart", "url": "http://localhost:8002/mcp/"}
  ]
}
```

### 3. Run the GUI Client
```sh
python Agents/a2a_client_gui_qt.py
```
- Requires PySide6
- Supports both A2A and MCP tool modes

## Usage
- Use the GUI or send JSON-RPC requests to `/a2a` or `/mcp/` endpoints.
- The triage agent will classify and route questions to the appropriate specialist agent.
- Time, coffee, and other specialist agents use external APIs or MCP servers as configured.

## Extending the System
- Add new agents by defining them in `Agents/a2a_agent.py` and adding to `triage_agent.handoffs`.
- Add new MCP tools by registering them with the MCP server in the same file.
- Update the triage logic in `Agents/agents.py` to support new question types.

## Security
- Guardrails block PII, toxic content, and prompt injection attempts.
- The time agent and other external integrations only answer using their respective APIs/servers.

## License
MIT 