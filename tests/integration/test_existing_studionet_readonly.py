"""Recheck the recorded StudioNet deployment without sending a new transaction."""

import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionHashVariant
from genlayer_py.client import create_client
from genlayer_py.chains import studionet

from tests.studionet_support import source_schema_proof


@pytest.mark.integration
def test_recorded_studionet_deployment_remains_valid():
    root = Path(__file__).resolve().parents[2]
    evidence = json.loads((root / "deployments" / "studionet.json").read_text(encoding="utf-8"))
    client = create_client(chain=studionet)
    for field in ("deployment_transaction_hash", "intelligent_transaction_hash"):
        receipt = client.get_transaction(evidence[field])
        assert receipt["status_name"] == "FINALIZED"
        assert tx_execution_succeeded(receipt), receipt
    source = root / "contracts" / "sequence_compressor.py"
    proof = source_schema_proof(evidence["contract_address"], source, {"compile_sequence", "get_segment", "segment_total"})
    assert proof["source_sha256"] == evidence["source"]["source_sha256"]
    factory = get_contract_factory(contract_file_path=source)
    contract = factory.build_contract(evidence["contract_address"], account=create_accounts(1)[0])
    compilation_id = f"{evidence['wallet_addresses'][0].lower()}:ASSEMBLY-RUN"
    state = contract.get_compilation(args=[compilation_id]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["state"] == "COMPILED"
    assert state["segment_count"] == 3
    assert state["entry_labels"] == [0, 0, 1, 1, 2]
