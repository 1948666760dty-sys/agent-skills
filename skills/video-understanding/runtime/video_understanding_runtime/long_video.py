from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

_ASCII_OR_CJK = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.+\-/]*|[\u4e00-\u9fff]+")


def sampling_profile(duration_seconds: float) -> dict[str, Any]:
    """Return an adaptive profile for overview coverage and long-video memory."""
    minutes = max(0.0, duration_seconds) / 60.0
    if minutes <= 5:
        tier = "short"
        baseline = 6.0
        max_frames = 240
        chapter = 120.0
        memory = 90.0
        overlap = 15.0
        frame_skip = 0
    elif minutes <= 30:
        tier = "standard"
        baseline = 12.0
        max_frames = 360
        chapter = 240.0
        memory = 120.0
        overlap = 20.0
        frame_skip = 0
    elif minutes <= 90:
        tier = "long"
        baseline = 20.0
        max_frames = 480
        chapter = 360.0
        memory = 180.0
        overlap = 30.0
        frame_skip = 0
    elif minutes <= 180:
        tier = "very_long"
        baseline = 30.0
        max_frames = 600
        chapter = 600.0
        memory = 300.0
        overlap = 45.0
        frame_skip = 1
    else:
        tier = "ultra_long"
        baseline = 45.0
        max_frames = 720
        chapter = 900.0
        memory = 420.0
        overlap = 60.0
        frame_skip = 2

    return {
        "tier": tier,
        "baseline_step_seconds": baseline,
        "max_overview_frames": max_frames,
        "chapter_window_seconds": chapter,
        "memory_window_seconds": memory,
        "memory_overlap_seconds": overlap,
        "scene_frame_skip": frame_skip,
        "agentic_rewatch": True,
    }


def build_chapters(
    transcript: list[dict[str, Any]],
    duration_seconds: float,
) -> list[dict[str, Any]]:
    profile = sampling_profile(duration_seconds)
    window = float(profile["chapter_window_seconds"])
    duration = max(duration_seconds, transcript[-1]["end"] if transcript else 0.0)
    if duration <= 0:
        return []

    chapters: list[dict[str, Any]] = []
    start = 0.0
    chapter_id = 1
    while start < duration:
        end = min(duration, start + window)
        rows = [
            row for row in transcript
            if float(row.get("end", 0.0)) >= start and float(row.get("start", 0.0)) < end
        ]
        joined = " ".join(str(row.get("text", "")).strip() for row in rows if row.get("text"))
        preview = joined[:360]
        chapters.append(
            {
                "chapter_id": chapter_id,
                "start_seconds": round(start, 3),
                "end_seconds": round(end, 3),
                "segment_count": len(rows),
                "characters": len(joined),
                "preview": preview,
                "title": None,
                "summary": None,
                "status": "structural_window",
            }
        )
        chapter_id += 1
        start = end
    return chapters


def build_evidence_chunks(
    transcript: list[dict[str, Any]],
    duration_seconds: float,
) -> list[dict[str, Any]]:
    """Build overlapping transcript windows for cheap retrieval before rewatch."""
    profile = sampling_profile(duration_seconds)
    window = float(profile["memory_window_seconds"])
    overlap = float(profile["memory_overlap_seconds"])
    step = max(30.0, window - overlap)
    duration = max(duration_seconds, transcript[-1]["end"] if transcript else 0.0)
    if duration <= 0:
        return []

    chunks: list[dict[str, Any]] = []
    start = 0.0
    chunk_id = 1
    while start < duration:
        end = min(duration, start + window)
        rows = [
            row for row in transcript
            if float(row.get("end", 0.0)) >= start and float(row.get("start", 0.0)) < end
        ]
        text = "\n".join(str(row.get("text", "")).strip() for row in rows if row.get("text"))
        if text:
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "start_seconds": round(start, 3),
                    "end_seconds": round(end, 3),
                    "text": text,
                    "characters": len(text),
                    "segment_count": len(rows),
                }
            )
            chunk_id += 1
        if end >= duration:
            break
        start += step
    return chunks


def _tokens(text: str) -> list[str]:
    result: list[str] = []
    for item in _ASCII_OR_CJK.findall(text.lower()):
        if not item:
            continue
        if "\u4e00" <= item[0] <= "\u9fff":
            chars = list(item)
            result.extend(chars)
            result.extend("".join(chars[i : i + 2]) for i in range(len(chars) - 1))
        else:
            result.append(item)
    return result


def search_evidence(
    chunks: list[dict[str, Any]],
    query: str,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Small local BM25-like lexical retriever. No external embedding API required."""
    limit = max(1, min(int(limit), 20))
    query_tokens = _tokens(query)
    if not chunks or not query_tokens:
        return []

    tokenized = [_tokens(str(chunk.get("text", ""))) for chunk in chunks]
    doc_freq: Counter[str] = Counter()
    for tokens in tokenized:
        doc_freq.update(set(tokens))

    total_docs = len(chunks)
    scored: list[tuple[float, dict[str, Any]]] = []
    q_lower = query.strip().lower()
    for chunk, tokens in zip(chunks, tokenized):
        counts = Counter(tokens)
        length_norm = max(1.0, math.sqrt(len(tokens) or 1))
        score = 0.0
        for token in query_tokens:
            tf = counts.get(token, 0)
            if not tf:
                continue
            idf = math.log((total_docs + 1.0) / (doc_freq[token] + 0.5)) + 1.0
            score += (1.0 + math.log(tf)) * idf
        text_lower = str(chunk.get("text", "")).lower()
        if q_lower and len(q_lower) >= 2 and q_lower in text_lower:
            score += 8.0
        score /= length_norm
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [
        {
            "score": round(score, 5),
            "chunk_id": chunk.get("chunk_id"),
            "start_seconds": chunk.get("start_seconds"),
            "end_seconds": chunk.get("end_seconds"),
            "text": chunk.get("text"),
            "characters": chunk.get("characters"),
        }
        for score, chunk in scored[:limit]
    ]
