import json
import os
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address

from tests.studionet_support import emit_record, ok, source_schema_proof, wallet_accounts


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(os.environ.get("RUN_STUDIONET") != "1", reason="opt-in live StudioNet test"),
]


def test_studionet_semantic_sequence_compression():
    accounts = wallet_accounts("sequencecompressor", 1)
    owner = accounts[0]
    source = Path(__file__).resolve().parents[2] / "contracts" / "sequence_compressor.py"
    factory = get_contract_factory(contract_file_path=source)
    deployed = ok(factory.deploy_contract_tx(args=[], account=owner, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    contract = factory.build_contract(address, account=owner)
    labels = json.dumps(["Preparation", "Execution", "Verification"])
    entries = json.dumps(["Confirm the public work boundary", "Stage the marked equipment", "Install the first component", "Install the second component", "Inspect the completed assembly"])
    compilation_id = f"{str(owner.address).lower()}:ASSEMBLY-RUN"
    intelligent = ok(contract.compile_sequence(args=["assembly-run", labels, entries, "Classify each ordered entry by operational phase without reordering entries." ]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    state = contract.get_compilation(args=[compilation_id]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["schema"] == "sequencecompressor/compilation/v1" and 1 <= state["segment_count"] <= 5
    proof = source_schema_proof(address, source, {"compile_sequence", "get_segment", "segment_total"})
    emit_record("sequencecompressor", "A", address, deployed, [], intelligent, accounts, proof, {"state": state["state"], "segment_count": state["segment_count"], "labels": state["labels"]})
