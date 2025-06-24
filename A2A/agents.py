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

# --- OpenAI LLM for all agents (supports chat and text models) ---
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
        chat_models = ["gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        text_models = ["text-davinci-003"]
        if agent_name == "Math Tutor":
            system_prompt = (
                "You are a helpful math tutor. If the user asks for an explanation, show your work step by step. "
                "Otherwise, just provide the answer."
            )
        elif agent_name == "History Tutor":
            system_prompt = "You are a helpful and factual history tutor. Answer clearly and concisely."
        else:
            system_prompt = f"You are an expert assistant named {agent_name}."
        model = "gpt-4o"  # Default
        if model in chat_models:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=model,
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
        elif model in text_models:
            prompt = f"{system_prompt}\nQ: {input_data}\nA:"
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.completions.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=256,
                    temperature=0.2,
                )
            )
            text = response.choices[0].text
            if text is not None:
                return text.strip()
            else:
                return "[ERROR] No text returned from OpenAI Completion."
        else:
            return f"[ERROR] Model {model} is not supported."
    except Exception as e:
        return f"Error from OpenAI API: {e}"

# --- Classic routing logic for Triage Agent ---
def is_math_question(text):
    text = text.lower()
    math_keywords = ["add", "subtract", "multiply", "divide", "+", "-", "*", "/", "what is", "calculate", "^", "%", "math", "solve", "equals", "=", "sum", "difference", "product", "quotient"]
    return any(word in text for word in math_keywords)

def is_history_question(text):
    text = text.lower()
    history_keywords = ["who", "when", "where", "history", "president", "revolution", "war", "battle", "year", "event", "happened", "occurred", "leader", "empire", "ancient", "modern", "king", "queen", "dynasty"]
    return any(word in text for word in history_keywords)

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
        # Classic routing for Triage Agent
        if agent.name == "Triage Agent":
            if is_math_question(input_data):
                # Find Math Tutor agent in handoffs
                math_agent = next((a for a in agent.handoffs if a.name == "Math Tutor"), None)
                if math_agent:
                    math_result = await Runner.run(math_agent, input_data)
                    return Result(math_result.final_output)
                else:
                    return Result("[ERROR] Math Tutor agent not found.")
            elif is_history_question(input_data):
                history_agent = next((a for a in agent.handoffs if a.name == "History Tutor"), None)
                if history_agent:
                    history_result = await Runner.run(history_agent, input_data)
                    return Result(history_result.final_output)
                else:
                    return Result("[ERROR] History Tutor agent not found.")
            else:
                return Result("Sorry, I can only answer math or history questions.")
        # All other agents use OpenAI GPT
        answer = await gpt_openai_answer(agent.name, input_data)
        return Result(answer)

TIMEZONE_ABBREVIATIONS = {
    "edt": "America/New_York",
    "est": "America/New_York",
    "pst": "America/Los_Angeles",
    "pdt": "America/Los_Angeles",
    "cst": "America/Chicago",
    "cdt": "America/Chicago",
    "mst": "America/Denver",
    "mdt": "America/Denver",
    "gmt": "Etc/GMT",
    "utc": "Etc/UTC",
    "bst": "Europe/London",
    "cet": "Europe/Paris",
    "jst": "Asia/Tokyo",
    "hkt": "Asia/Hong_Kong",
    # Add more as needed
} 