import json
from pathlib import Path
from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address


def _ok(receipt):
    assert tx_execution_succeeded(receipt), json.dumps(receipt, default=str)


def test_five_validator_sequence_compression():
    owner = create_accounts(1)[0]
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "sequence_compressor.py")
    receipt = factory.deploy_contract_tx(args=[], account=owner, wait_transaction_status=TransactionStatus.FINALIZED)
    _ok(receipt)
    contract = factory.build_contract(extract_contract_address(receipt), account=owner)
    labels = json.dumps(["Preparation", "Execution", "Verification"])
    entries = json.dumps(["Confirm the public work boundary", "Stage the marked equipment", "Install the first component", "Install the second component", "Inspect the completed assembly"])
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {"Assign exactly one indexed label to each ordered public entry": json.dumps({"labels": [0, 0, 1, 1, 2]})}})
    context = {"validators": [v.to_dict() for v in validators], "genvm_datetime": "2026-08-25T12:00:00Z"}
    compilation_id = f"{str(owner.address).lower()}:ASSEMBLY-RUN"
    _ok(contract.compile_sequence(args=["assembly-run", labels, entries, "Classify each ordered entry by its operational phase without reordering entries."]).transact(transaction_context=context, wait_transaction_status=TransactionStatus.FINALIZED))
    assert contract.segment_total(args=[compilation_id]).call() == 3
