from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

RE_TAG_RESPONSE = re.compile(r"<response>(.*?)</response>", flags=re.DOTALL | re.IGNORECASE)
RE_TAG_SKILL = re.compile(r"<skill>.*?</skill>", flags=re.S | re.IGNORECASE)
RE_JSON_CODE_BLOCK = re.compile(r"```json\s*(\{.*?\})\s*```", flags=re.S)
RE_JSON_BRACE = re.compile(r"(\{.*\})", flags=re.S)


def extract_tag_content(text: str, tag: str = "response") -> Optional[str]:
    if not text:
        return None
    if tag == "response":
        match = RE_TAG_RESPONSE.search(text)
    else:
        match = re.search(rf"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else text.strip()


def _tag_at(text: str, start: int) -> Optional[tuple[str, bool, int]]:
    if start >= len(text) or text[start] != "<":
        return None
    end = text.find(">", start + 1)
    if end < 0:
        return None
    body = text[start + 1 : end].strip()
    closing = body.startswith("/")
    if closing:
        body = body[1:].lstrip()
    name_chars = []
    for char in body:
        if char.isalnum() or char in {"_", "-"}:
            name_chars.append(char)
        else:
            break
    if not name_chars:
        return None
    return "".join(name_chars).casefold(), closing, end + 1


def _has_incomplete_internal_tag(text: str) -> bool:
    lowered = text.casefold()
    for name in ("think", "assessment", "client_state", "skill", "strategy"):
        for marker in (f"<{name}", f"</{name}"):
            cursor = 0
            while True:
                position = lowered.find(marker, cursor)
                if position < 0:
                    break
                boundary = position + len(marker)
                if boundary < len(lowered) and (lowered[boundary].isalnum() or lowered[boundary] in {"_", "-"}):
                    cursor = boundary
                    continue
                if lowered.find(">", boundary) < 0:
                    return True
                cursor = boundary
    return False


def _find_tag(text: str, name: str, *, closing: Optional[bool] = None, start: int = 0):
    cursor = start
    while True:
        position = text.find("<", cursor)
        if position < 0:
            return None
        parsed = _tag_at(text, position)
        if parsed and parsed[0] == name and (closing is None or parsed[1] == closing):
            return position, parsed[2], parsed[1]
        cursor = position + 1


def extract_public_response(text: str, end_token: str = "") -> tuple[str, bool]:
    """Extract only client-facing text, failing closed on unclosed reasoning markup."""
    raw = str(text or "").strip()
    if not raw or _has_incomplete_internal_tag(raw):
        return "", False

    opening = _find_tag(raw, "response", closing=False)
    if opening is None:
        thought = _find_tag(raw, "think", closing=False)
        if thought is not None:
            thought_end = _find_tag(raw, "think", closing=True, start=thought[1])
            if thought_end is None:
                return "", False
            return extract_public_response(raw[thought_end[1] :], end_token)
        if any(_find_tag(raw, tag) is not None for tag in ("assessment", "client_state", "skill", "strategy")):
            return "", False
        public_text = raw
    else:
        content_start = opening[1]
        cursor = content_start
        content_end = len(raw)
        configured_end = False
        internal_tags = {"think", "assessment", "client_state", "skill", "strategy"}
        while True:
            position = raw.find("<", cursor)
            if position < 0:
                break
            parsed = _tag_at(raw, position)
            if parsed is None:
                cursor = position + 1
                continue
            name, closing, after = parsed
            if name == "response" and closing:
                content_end = position
                break
            if name == "end":
                content_end = position
                configured_end = raw[position:after] == end_token if end_token else False
                break
            if name in internal_tags:
                content_end = position
                break
            cursor = after
        public_text = raw[content_start:content_end].strip()

    has_end = bool(end_token and raw.endswith(end_token))
    if end_token and public_text.endswith(end_token):
        public_text = public_text[: -len(end_token)].rstrip()
        has_end = True
    for marker in ("</end>", "<end>"):
        if public_text.endswith(marker):
            public_text = public_text[: -len(marker)].rstrip()
            has_end = has_end or bool(end_token and marker == end_token)
            break
    return public_text, has_end or configured_end if opening is not None else has_end


def remove_tags(text: str, tag: str = "response") -> str:
    if not text:
        return ""
    if tag == "skill":
        return RE_TAG_SKILL.sub("", text).strip()
    return re.sub(rf"<{tag}>.*?</{tag}>", "", text, flags=re.S | re.IGNORECASE).strip()


def safe_json_loads(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("empty text for JSON parse")

    content = extract_tag_content(text, tag="response") or ""
    candidate = _strip_code_fence(content)

    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    match = RE_JSON_CODE_BLOCK.search(content) or RE_JSON_BRACE.search(content)
    if match:
        blob = _strip_code_fence(match.group(1))
        parsed = json.loads(blob)
        if isinstance(parsed, dict):
            return parsed

    raise ValueError("JSON parse failed: no valid JSON object found")


def format_transcript(transcript: List[Dict[str, Any]], *, for_profile: bool = False) -> str:
    lines: List[str] = []
    for msg in transcript:
        role = msg.get("role")
        content = str(msg.get("content") or "")
        if role == "system" or not content.strip():
            continue

        if for_profile:
            content = extract_tag_content(content, tag="response") or ""
        else:
            content = remove_tags(content, tag="skill")

        content = content.replace("\n", " ").strip()
        if not content:
            continue

        speaker = "counsel" if role == "assistant" else "client"
        lines.append(f"{speaker}：{content}")

    return "\n".join(lines)


def strip_end_token(text: str, end_token: str) -> tuple[str, bool]:
    cleaned = (text or "").strip()
    if not end_token:
        return cleaned, False
    if cleaned.endswith(end_token):
        return cleaned[: -len(end_token)].strip(), True
    return cleaned, False


def _strip_code_fence(text: str) -> str:
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
    if raw.endswith("```"):
        raw = re.sub(r"```$", "", raw).strip()
    return raw
