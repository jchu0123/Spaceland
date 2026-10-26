"""ASGI entrypoint for Vercel and other ASGI-compatible hosts."""

from __future__ import annotations

import json
from typing import Any

from planetarium import ROOT, PlanetariumAgent

agent = PlanetariumAgent()


async def _respond(send: Any, status: int, body: bytes, content_type: str) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", content_type.encode("ascii")),
                (b"content-length", str(len(body)).encode("ascii")),
                (b"cache-control", b"no-store"),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def _read_body(receive: Any) -> bytes | None:
    body = bytearray()
    while True:
        message = await receive()
        if message["type"] == "http.disconnect":
            return None
        body.extend(message.get("body", b""))
        if len(body) > 16_384:
            return b""
        if not message.get("more_body", False):
            return bytes(body)


async def app(scope: dict[str, Any], receive: Any, send: Any) -> None:
    if scope["type"] != "http":
        return

    method = scope["method"]
    path = scope["path"]
    if method == "GET" and path == "/":
        body = (ROOT / "index.html").read_bytes()
        await _respond(send, 200, body, "text/html; charset=utf-8")
        return
    if method == "GET" and path == "/api/catalog":
        body = json.dumps(
            {"bodies": agent.planets + agent.solar_bodies},
            ensure_ascii=False,
        ).encode("utf-8")
        await _respond(send, 200, body, "application/json; charset=utf-8")
        return
    if method == "POST" and path == "/api/ask":
        body = await _read_body(receive)
        if body is None:
            return
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            await _respond(send, 400, b'{"error":"Request body must be valid JSON"}', "application/json")
            return
        question = payload.get("question") if isinstance(payload, dict) else None
        if not isinstance(question, str) or not question.strip() or len(question) > 1000:
            await _respond(
                send,
                400,
                b'{"error":"Question must be a non-empty string under 1,000 characters"}',
                "application/json",
            )
            return
        answer = agent.answer(question.strip())
        response = json.dumps({"answer": answer}, ensure_ascii=False).encode("utf-8")
        await _respond(send, 200, response, "application/json; charset=utf-8")
        return

    if path in {"/", "/api/catalog", "/api/ask"}:
        await _respond(
            send,
            405,
            b'{"error":"Method not allowed"}',
            "application/json",
        )
        return
    await _respond(send, 404, b'{"error":"Not found"}', "application/json")
