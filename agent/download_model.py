#!/usr/bin/env python3
"""Download TinyLlama with a visible progress bar (run before agent.py)."""

from llm_provider import MODEL_ID, _ensure_model_cached

if __name__ == "__main__":
    path = _ensure_model_cached()
    print(f"\n✅ Model cached at:\n   {path}\n")
    print("You can now run: python agent.py")
