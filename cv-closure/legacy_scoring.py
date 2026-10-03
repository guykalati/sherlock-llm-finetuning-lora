#!/usr/bin/env python3
"""Shared utilities for HW2 Sherlock SFT scripts.

The functions in this file deliberately stay small and dependency-light. The
cluster scripts should fail because of a real missing ML dependency, not because
basic JSONL parsing needed a package that is absent from the course image.
"""

from __future__ import annotations

import collections
import hashlib
import json
import math
import os
import random
import re
import string
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_path(path: str | Path) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def load_config(path: str | Path = "hw2_config.json") -> Dict[str, Any]:
    with project_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def ensure_dir(path: str | Path) -> Path:
    p = project_path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_jsonl(path: str | Path) -> List[Dict[str, Any]]:
    p = project_path(path)
    rows: List[Dict[str, Any]] = []
    if not p.exists():
        return rows
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {p}:{i}: {exc}") from exc
    return rows


def write_jsonl(path: str | Path, rows: Iterable[Dict[str, Any]]) -> None:
    p = project_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_text(path: str | Path, text: str) -> None:
    p = project_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def parse_notes(notes: str | None) -> Dict[str, str]:
    meta: Dict[str, str] = {}
    if not notes:
        return meta
    for part in str(notes).split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        meta[key.strip()] = value.strip()
    return meta


def make_notes(**kwargs: Any) -> str:
    return "; ".join(f"{k}={v}" for k, v in kwargs.items() if v is not None and v != "")


def message_by_role(row: Dict[str, Any], role: str) -> str:
    for msg in row.get("messages", []):
        if msg.get("role") == role:
            return str(msg.get("content", ""))
    return ""


def validate_messages(row: Dict[str, Any]) -> Tuple[bool, str]:
    messages = row.get("messages")
    if not isinstance(messages, list) or len(messages) < 3:
        return False, "messages must contain system, user, assistant"
    roles = [m.get("role") for m in messages]
    if roles[:3] != ["system", "user", "assistant"]:
        return False, f"unexpected first roles: {roles[:3]}"
    for msg in messages[:3]:
        if not isinstance(msg.get("content"), str) or not msg["content"].strip():
            return False, f"empty {msg.get('role')} content"
    return True, ""


def extract_book(row: Dict[str, Any]) -> str:
    system = message_by_role(row, "system")
    match = re.search(r"based on:\s*(.*?)(?:\.?$)", system, flags=re.I)
    if match:
        return match.group(1).strip().rstrip(".")
    if re.search(r"based on the text", system, flags=re.I):
        return "Not specified (provided unanswerable)"
    meta = parse_notes(row.get("notes"))
    return meta.get("book", "Not specified")


def extract_category(row: Dict[str, Any]) -> str:
    meta = parse_notes(row.get("notes"))
    return meta.get("category", "unknown")


def extract_source(row: Dict[str, Any]) -> str:
    meta = parse_notes(row.get("notes"))
    return meta.get("source", "unknown")


def extract_aliases(row: Dict[str, Any]) -> List[str]:
    aliases = []
    for key in ["alt_answers", "aliases", "alt_answers_nqa"]:
        value = row.get(key)
        if isinstance(value, list):
            aliases.extend(str(v) for v in value)
        elif isinstance(value, str):
            aliases.append(value)
    meta = parse_notes(row.get("notes"))
    for key in ["alt_answers", "aliases", "alt_answers_nqa"]:
        raw = meta.get(key)
        if not raw:
            continue
        raw = raw.strip()
        if raw.startswith("["):
            try:
                aliases.extend(str(v) for v in json.loads(raw))
                continue
            except json.JSONDecodeError:
                pass
        aliases.extend(x.strip().strip("\"'") for x in raw.split("|") if x.strip())
    answer = message_by_role(row, "assistant")
    if answer:
        aliases.append(answer)
    seen = set()
    unique = []
    for alias in aliases:
        key = normalize_answer(alias)
        if key and key not in seen:
            seen.add(key)
            unique.append(alias)
    return unique


def normalize_answer(text: str) -> str:
    """SQuAD-style answer normalization for exact match and token F1."""
    text = text.lower()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = " ".join(text.split())
    return text


def token_f1(prediction: str, ground_truth: str) -> float:
    pred_tokens = normalize_answer(prediction).split()
    truth_tokens = normalize_answer(ground_truth).split()
    if not pred_tokens and not truth_tokens:
        return 1.0
    if not pred_tokens or not truth_tokens:
        return 0.0
    common = collections.Counter(pred_tokens) & collections.Counter(truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(truth_tokens)
    return 2 * precision * recall / (precision + recall)


def score_prediction(prediction: str, answers: Sequence[str]) -> Dict[str, float]:
    normalized_prediction = normalize_answer(prediction)
    normalized_answers = [normalize_answer(a) for a in answers if normalize_answer(a)]
    accuracy = 1.0 if normalized_prediction in normalized_answers else 0.0
    f1 = max((token_f1(prediction, answer) for answer in answers), default=0.0)
    return {"accuracy": accuracy, "f1": f1}


def stable_hash(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def deterministic_sample(rows: Sequence[Dict[str, Any]], n: int, seed: int) -> List[Dict[str, Any]]:
    rows = list(rows)
    rng = random.Random(seed)
    if n >= len(rows):
        return rows
    return rng.sample(rows, n)


def counter_table(rows: Sequence[Dict[str, Any]], key_fn) -> List[Tuple[str, int]]:
    counter = collections.Counter(key_fn(row) for row in rows)
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def perplexity_from_losses(losses: Sequence[float]) -> float:
    loss = mean(losses)
    return math.exp(loss) if not math.isnan(loss) else float("nan")
