import asyncio
from typing import Any, Callable, List, Optional
import os

class GuardrailFunctionOutput:
    def __init__(self, output_info: str, tripwire_triggered: bool):
        self.output_info = output_info
        self.tripwire_triggered = tripwire_triggered

class InputGuardrail:
    def __init__(self, guardrail_function: Callable):
        self.guardrail_function = guardrail_function

class Agent:
    def __init__(self, name: str, instructions: str, handoff_description: Optional[str] = None, handoffs: Optional[List['Agent']] = None, input_guardrails: Optional[List['InputGuardrail']] = None):
        self.name = name
        self.instructions = instructions
        self.handoff_description = handoff_description
        self.handoffs = handoffs or []
        self.input_guardrails = input_guardrails or []

# --- OpenAI LLM for all agents (new SDK interface) ---
async def gpt_openai_answer(agent_name, input_data):
    try:
        import openai
    except ImportError:
        return "OpenAI package not installed. Please run 'pip install openai'."
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OpenAI API key not set. Please set the OPENAI_API_KEY environment variable."
    try:
        client = openai.OpenAI(api_key=api_key)
        if agent_name == "Math Tutor":
            system_prompt = "You are a helpful math tutor. Solve the user's math problem. Show your work step by step, then give the final answer."
        elif agent_name == "History Tutor":
            system_prompt = "You are a helpful and factual history tutor. Answer clearly and concisely."
        elif agent_name == "Triage Agent":
            system_prompt = (
                "You are a triage agent. If the user's question is about math, say 'This is a math question.' "
                "If it's about history, say 'This is a history question.' "
                "If it's about anything else, say 'Sorry, I can only answer math or history questions.' "
                "Do not answer questions outside of math or history."
                "If you use the time server mcp tool, tell the user."
            )
        else:
            system_prompt = f"You are an expert assistant named {agent_name}."
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_data}
                ],
                max_tokens=256,
                temperature=0.2,
            )
        )
        content = response.choices[0].message.content
        if content is not None:
            return content.strip()
        else:
            return "[ERROR] No content returned from OpenAI ChatCompletion."
    except Exception as e:
        return f"Error from OpenAI API: {e}"

class Runner:
    @staticmethod
    async def run(agent: Agent, input_data: str):
        class Result:
            def __init__(self, final_output: str):
                self.final_output = final_output
        # Run guardrails first
        for guardrail in agent.input_guardrails:
            guardrail_result = await guardrail.guardrail_function(None, agent, input_data)
            if guardrail_result.tripwire_triggered:
                return Result(f"[SECURITY BLOCKED] {guardrail_result.output_info}")
        # All agents use OpenAI GPT
        answer = await gpt_openai_answer(agent.name, input_data)
        return Result(answer) 