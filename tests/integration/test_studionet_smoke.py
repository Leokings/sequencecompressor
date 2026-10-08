import json
import os
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.accounts import create_accounts
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address

from tests.studionet_support import ok, source_schema_proof


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(os.environ.get("RUN_STUDIONET") != "1", reason="opt-in live StudioNet test"),
]


def test_studionet_full_sequence_lifecycle():
    accounts = create_accounts(7)
    owner = accounts[0]
    source = Path(__file__).resolve().parents[2] / "contracts" / "sequence_compressor.py"
    factory = get_contract_factory(contract_file_path=source)
    deployed = ok(factory.deploy_contract_tx(args=[], account=owner, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    print("STUDIONET_DEPLOY_TX=" + deployed["hash"], flush=True)
    contract = factory.build_contract(address, account=owner)
    labels = json.dumps(["Preparation", "Execution", "Verification"])
    entries = json.dumps(["Confirm the public work boundary", "Stage the marked equipment", "Install the first component", "Install the second component", "Inspect the completed assembly"])
    compilation_id = f"{str(owner.address).lower()}:ASSEMBLY-RUN"
    intelligent = ok(contract.compile_sequence(args=["assembly-run", labels, entries, "Classify each ordered entry by operational phase without reordering entries." ]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    print("STUDIONET_INTELLIGENT_TX=" + intelligent["hash"], flush=True)
    state = contract.get_compilation(args=[compilation_id]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["schema"] == "sequencecompressor/compilation/v1" and 1 <= state["segment_count"] <= 5
    assert state["state"] == "COMPILED"
    count = state["segment_count"]
    lifecycle = []
    first = ok(contract.assign_segment(args=[compilation_id, 0, accounts[1].address]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    lifecycle.append(first)
    print("STUDIONET_ASSIGN_TX=" + first["hash"], flush=True)
    reassigned = ok(contract.reassign_segment(args=[compilation_id, 0, accounts[6].address]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    lifecycle.append(reassigned)
    print("STUDIONET_REASSIGN_TX=" + reassigned["hash"], flush=True)
    operators = [accounts[6], *accounts[2:count + 1]]
    for index in range(1, count):
        receipt = ok(contract.assign_segment(args=[compilation_id, index, operators[index].address]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
        lifecycle.append(receipt)
        print("STUDIONET_ASSIGN_TX=" + receipt["hash"], flush=True)
    for index, operator in enumerate(operators):
        operator_contract = factory.build_contract(address, account=operator)
        receipt = ok(operator_contract.acknowledge_segment(args=[compilation_id, index, f"Operator acknowledged segment {index} after review."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
        lifecycle.append(receipt)
        print("STUDIONET_ACK_TX=" + receipt["hash"], flush=True)
        segment = contract.get_segment(args=[compilation_id, index]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
        assert segment["state"] == "ACKNOWLEDGED"
        assert segment["operator"].lower() == str(operator.address).lower()
    sealed = ok(contract.seal_sequence(args=[compilation_id]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    lifecycle.append(sealed)
    print("STUDIONET_SEAL_TX=" + sealed["hash"], flush=True)
    final_state = contract.get_compilation(args=[compilation_id]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert final_state["state"] == "SEALED"
    assert final_state["assigned_count"] == final_state["acknowledged_count"] == count
    proof = source_schema_proof(address, source, {"compile_sequence", "assign_segment", "reassign_segment", "acknowledge_segment", "seal_sequence", "get_compilation", "get_segment", "segment_total"})
    print("STUDIONET_RECORD=" + json.dumps({
        "network": "studionet", "chain_id": 61999, "contract_address": address,
        "deployment_transaction_hash": deployed["hash"],
        "intelligent_transaction_hash": intelligent["hash"],
        "lifecycle_transaction_hashes": [receipt["hash"] for receipt in lifecycle],
        "wallet_addresses": [str(account.address) for account in accounts],
        "wallet_policy": "disposable in-process test wallets; private keys never stored in the repository",
        "source": proof,
        "verification": {"all_receipts_finalized_and_execution_successful": True, "latest_final_readback": True, "deployed_source_exact": True, "final_state": final_state},
    }, sort_keys=True), flush=True)
