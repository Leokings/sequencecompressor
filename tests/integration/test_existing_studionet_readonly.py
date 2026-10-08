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
    hashes = [evidence["deployment_transaction_hash"], evidence["intelligent_transaction_hash"], *evidence["lifecycle_transaction_hashes"]]
    for transaction_hash in hashes:
        receipt = client.get_transaction(transaction_hash)
        assert receipt["status_name"] == "FINALIZED"
        assert tx_execution_succeeded(receipt), receipt
    source = root / "contracts" / "sequence_compressor.py"
    proof = source_schema_proof(evidence["contract_address"], source, {"compile_sequence", "assign_segment", "reassign_segment", "acknowledge_segment", "seal_sequence", "get_compilation", "get_segment", "segment_total"})
    assert proof["source_sha256"] == evidence["source"]["source_sha256"]
    factory = get_contract_factory(contract_file_path=source)
    contract = factory.build_contract(evidence["contract_address"], account=create_accounts(1)[0])
    compilation_id = f"{evidence['wallet_addresses'][0].lower()}:ASSEMBLY-RUN"
    state = contract.get_compilation(args=[compilation_id]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["state"] == "SEALED"
    assert state["segment_count"] == evidence["verification"]["segment_count"]
    assert state["assigned_count"] == state["acknowledged_count"] == state["segment_count"]
    assert state["entry_labels"] == [0, 0, 1, 1, 2]
    for index in range(state["segment_count"]):
        segment = contract.get_segment(args=[compilation_id, index]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
        assert segment["state"] == "ACKNOWLEDGED"
    assert contract.get_segment(args=[compilation_id, 0]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)["operator"].lower() == evidence["wallet_addresses"][6].lower()
