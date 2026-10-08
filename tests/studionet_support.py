"""Shared helpers for opt-in StudioNet verification."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import time
from typing import Any
from urllib import error, request

from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus


STUDIONET_RPC = "https://studio.genlayer.com/api"


def ok(receipt: dict[str, Any]) -> dict[str, Any]:
    assert tx_execution_succeeded(receipt), json.dumps(receipt, default=str)
    assert receipt.get("status_name") == TransactionStatus.FINALIZED.value
    assert receipt.get("result_name") in (None, "AGREE", "MAJORITY_AGREE")
    assert receipt.get("tx_execution_result_name") in (None, "FINISHED_WITH_RETURN")
    return receipt


def _rpc(method: str, params: list[Any]) -> Any:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(8):
        try:
            call = request.Request(
                STUDIONET_RPC,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "Codex-GenLayer-Audit/1.0",
                },
            )
            with request.urlopen(call, timeout=30) as response:
                decoded = json.loads(response.read().decode("utf-8"))
            if decoded.get("error"):
                raise AssertionError(json.dumps(decoded["error"], sort_keys=True))
            return decoded["result"]
        except (error.HTTPError, error.URLError, TimeoutError, AssertionError) as exc:
            last_error = exc
            if attempt == 7:
                break
            time.sleep(6)
    raise AssertionError(f"StudioNet RPC verification failed: {last_error}")


def source_schema_proof(address: str, source_path: Path, required_methods: set[str]) -> dict[str, Any]:
    local_source = source_path.read_bytes()
    deployed_source = base64.b64decode(_rpc("gen_getContractCode", [address]), validate=True)
    assert deployed_source == local_source
    schema = _rpc("gen_getContractSchema", [address])
    assert isinstance(schema, dict) and isinstance(schema.get("methods"), dict)
    methods = set(schema["methods"])
    assert required_methods <= methods
    return {
        "source_sha256": hashlib.sha256(local_source).hexdigest(),
        "deployed_source_sha256": hashlib.sha256(deployed_source).hexdigest(),
        "schema_methods_verified": sorted(required_methods),
    }
