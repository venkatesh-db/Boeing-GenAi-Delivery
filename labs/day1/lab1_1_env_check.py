# %% [markdown]
# # Lab 1.1 — Environment check
# Run every cell. Each library should print a version,
# and the .env check should pass.

# %%
import importlib
import sys
from pathlib import Path

print("Python", sys.version.split()[0])
assert sys.version_info[:2] == (3, 11), "Use Python 3.11"

LIBS = ["numpy", "pandas", "sklearn", "matplotlib",
        "fastapi", "streamlit", "openai", "langchain",
        "langgraph", "faiss", "mcp"]
for name in LIBS:
    module = importlib.import_module(name)
    version = getattr(module, "__version__", "ok")
    print(f"{name:12s} {version}")

# %% Your key lives in .env, never in a notebook
HERE = Path(__file__) if "__file__" in globals() else None
ROOT = HERE.resolve().parents[2] if HERE else Path.cwd()
env_file = ROOT / ".env"
print(".env found:", env_file.exists())
print("Environment OK")
