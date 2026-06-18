#!/usr/bin/env python3
"""
Smoke / latency benchmark for this repo's local TinyLlama stack.

Uses llm_provider.py (same as agent.py) — no Ollama or langchain_ollama required.

Usage (from agent/ with venv active):
    python benchmark.py
    python benchmark.py --tools-only
    python benchmark.py --prompts 3
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from llm_provider import MODEL_ID, create_llm, warmup_llm
from tool_generator import generate_tools

BASE_DIR = Path(__file__).parent
REGISTRY_PATH = str(BASE_DIR / "api_registry.yaml")

DEFAULT_PROMPTS = [
    "Reply with exactly one word: OK",
    'Return only JSON: {"status": "ok"}',
    "List three colors as a comma-separated line, nothing else.",
]


def bench_tools() -> int:
    print("\n── Registry & tools ──")
    tools = generate_tools(REGISTRY_PATH)
    print(f"   Tools generated: {len(tools)}")
    for t in tools:
        print(f"   • {t.name}")
    return len(tools)


def bench_llm(num_prompts: int, max_new_tokens: int) -> None:
    print("\n── TinyLlama load & warmup ──")
    print(f"   Model: {MODEL_ID}")
    t0 = time.perf_counter()
    warmup_llm()
    load_s = time.perf_counter() - t0
    print(f"   Load + warmup: {load_s:.1f}s")

    llm = create_llm(max_new_tokens=max_new_tokens)
    prompts = DEFAULT_PROMPTS[:num_prompts]

    print(f"\n── Generation ({len(prompts)} prompts, max_new_tokens={max_new_tokens}) ──")
    times: list[float] = []
    for i, prompt in enumerate(prompts, 1):
        t0 = time.perf_counter()
        out = llm.invoke(prompt).content
        elapsed = time.perf_counter() - t0
        times.append(elapsed)
        preview = out.replace("\n", " ")[:120]
        print(f"\n   [{i}] {elapsed:.2f}s")
        print(f"       prompt : {prompt[:80]}{'…' if len(prompt) > 80 else ''}")
        print(f"       output : {preview}{'…' if len(out) > 120 else ''}")

    if times:
        avg = sum(times) / len(times)
        print(f"\n   Average generation time: {avg:.2f}s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark local TinyLlama + registry tools (no Ollama)."
    )
    parser.add_argument(
        "--tools-only",
        action="store_true",
        help="Only load api_registry.yaml and list generated tools (no model load).",
    )
    parser.add_argument(
        "--prompts",
        type=int,
        default=len(DEFAULT_PROMPTS),
        metavar="N",
        help=f"Number of test prompts to run (1–{len(DEFAULT_PROMPTS)}, default: all).",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=64,
        help="Cap tokens per benchmark prompt (default: 64).",
    )
    args = parser.parse_args()

    n_tools = bench_tools()
    if args.tools_only:
        print("\n✅ Tools OK (skipped model load).")
        return

    n = max(1, min(args.prompts, len(DEFAULT_PROMPTS)))
    bench_llm(n, args.max_new_tokens)
    print(
        f"\n✅ Benchmark complete ({n_tools} tools, {n} prompt(s)).\n"
        "   Full chat test: python agent.py (API should be running in another terminal).\n"
    )


if __name__ == "__main__":
    main()
