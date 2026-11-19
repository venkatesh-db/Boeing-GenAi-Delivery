# %% [markdown]
# # Lab 5.1 — Tool calling: let the LLM choose a tool, validate it, run it
# OpenAI models return native tool calls. Some local models (e.g. llama3) don't support tools,
# so we fall back to asking for JSON. Either way the tool name is checked against the allowlist
# and the arguments are validated before anything runs.

# %%
import json
import sys
from pathlib import Path

import openai
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd().parents[1]
sys.path.insert(0, str(ROOT))
from aeroguard import llm, security  # noqa: E402
from aeroguard.agent.tools import TOOLS  # noqa: E402
from aeroguard.config import get_settings  # noqa: E402

specs = [convert_to_openai_tool(t) for t in TOOLS.values()]
print(json.dumps(specs[0], indent=1)[:400])


def choose_tool(question: str) -> tuple[str, dict, str]:
    messages = [{"role": "system", "content": "Pick the single best tool for the question."},
                {"role": "user", "content": question}]
    try:
        with llm.friendly_errors():
            resp = llm.client().chat.completions.create(model=get_settings().chat_model, messages=messages,
                                                        tools=specs)
        call = resp.choices[0].message.tool_calls[0]
        return call.function.name, json.loads(call.function.arguments), "native tool call"
    except (openai.BadRequestError, TypeError, IndexError) as err:
        if isinstance(err, openai.BadRequestError) and "does not support tools" not in str(err):
            raise
    menu = "\n".join(
        f"- {s['function']['name']}: {s['function']['description']} arguments: "
        + json.dumps({k: v.get("type", "string") for k, v in s["function"]["parameters"]["properties"].items()})
        for s in specs)
    convo = [{"role": "system", "content": f"Tools:\n{menu}\nReply ONLY with JSON like "
              '{"tool": "predict_failure", "arguments": {"engine_id": "N123AB-E1"}}'},
             {"role": "user", "content": question}]
    for _ in range(2):  # one retry with the error message, as on Day 3
        text = llm.chat(convo, json_mode=True, temperature=0)
        data = json.loads(text)
        name, args = data.get("tool", ""), data.get("arguments", {})
        try:
            if name in TOOLS:
                TOOLS[name].args_schema.model_validate(args)
                return name, args, "JSON fallback"
            error = f"unknown tool {name!r}"
        except ValidationError as err:
            error = str(err)
        convo += [{"role": "assistant", "content": text},
                  {"role": "user", "content": f"Invalid: {error}. Arguments must be an object with named fields."}]
    return name, args, "JSON fallback (still invalid)"


def run_tool(name: str, args: dict):
    security.check_tool(name)                       # 1. allowlist
    tool = TOOLS[name]
    validated = tool.args_schema.model_validate(args)  # 2. validate arguments
    return tool.invoke(validated.model_dump(exclude_none=True))  # 3. run


# %%
for question in ["What is the failure risk for engine N123AB-E2?",
                 "Which airworthiness directives are still open on N123AB?",
                 "Find the manual procedure for high engine vibration."]:
    name, args, how = choose_tool(question)
    print(f"\n{question}\n  -> {name}({args})  [{how}]")
    try:
        print("  result:", str(run_tool(name, args))[:200])
    except (ValidationError, security.PermissionDenied) as err:
        print("  refused:", str(err).splitlines()[0])

# %% The allowlist in action: a tool that is not allowed is refused before it runs
try:
    run_tool("close_work_order", {"id": "WO-1"})
except Exception as err:
    print("\nBlocked:", err)
