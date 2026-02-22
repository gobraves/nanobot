"""
FastAPI + Minimal Agent Loop integration demo.

Run:
  pip install fastapi uvicorn
  uvicorn case.examples.fastapi_agent_integration_demo:app --reload --port 8080

Test:
  curl -X POST http://127.0.0.1:8080/v1/chat \
    -H 'content-type: application/json' \
    -d '{"message":"what is weather today?"}'
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


# ---- Minimal protocol ----
@dataclass
class ToolCallRequest:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCallRequest] = field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class FakeLLMProvider:
    async def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None) -> LLMResponse:
        last = messages[-1]
        if last["role"] == "user" and "weather" in str(last["content"]).lower():
            return LLMResponse(
                content="I'll call weather tool.",
                tool_calls=[ToolCallRequest(id="call_1", name="get_weather", arguments={"city": "Hangzhou"})],
            )
        if last["role"] == "tool":
            data = json.loads(last["content"])
            return LLMResponse(content=f"{data['city']} is {data['temp_c']}°C, {data['condition']}.")
        return LLMResponse(content="Direct answer without tools.")


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, Any] = {}

    def register(self, name: str, fn):
        self.tools[name] = fn

    async def execute(self, name: str, args: dict[str, Any]) -> str:
        result = self.tools[name](**args)
        return json.dumps(result, ensure_ascii=False)


class MinimalAgentLoop:
    """HTTP-facing minimal loop: model -> tools -> model until final answer."""

    def __init__(self, provider: FakeLLMProvider, tools: ToolRegistry, max_iterations: int = 6):
        self.provider = provider
        self.tools = tools
        self.max_iterations = max_iterations

    async def run_once(self, user_text: str) -> dict[str, Any]:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_text},
        ]
        used_tools: list[str] = []

        for _ in range(self.max_iterations):
            resp = await self.provider.chat(messages, tools=[])
            if resp.has_tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": resp.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                            }
                            for tc in resp.tool_calls
                        ],
                    }
                )
                for tc in resp.tool_calls:
                    used_tools.append(tc.name)
                    tool_result = await self.tools.execute(tc.name, tc.arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": tc.name,
                            "content": tool_result,
                        }
                    )
                continue

            return {
                "answer": resp.content or "",
                "tools_used": used_tools,
                "iterations": len(used_tools) + 1,
            }

        return {
            "answer": "Stopped by max_iterations",
            "tools_used": used_tools,
            "iterations": self.max_iterations,
        }


def get_weather(city: str) -> dict[str, Any]:
    return {"city": city, "temp_c": 17, "condition": "cloudy"}


provider = FakeLLMProvider()
registry = ToolRegistry()
registry.register("get_weather", get_weather)
agent = MinimalAgentLoop(provider, registry)

app = FastAPI(title="Agent Loop Integration Demo")


class ChatRequest(BaseModel):
    message: str


@app.post("/v1/chat")
async def chat(req: ChatRequest):
    result = await agent.run_once(req.message)
    return {"ok": True, **result}
