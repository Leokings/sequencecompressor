import json


LABELS = json.dumps(["Preparation", "Execution", "Verification"])
ENTRIES = json.dumps([
    "Confirm the public work boundary",
    "Stage the marked equipment",
    "Install the first component",
    "Install the second component",
    "Inspect the completed assembly",
])
POLICY = "Classify each ordered entry by its operational phase without changing or reordering any entry."


def _compile(contract, vm, owner, labels):
    vm.sender = owner
    vm.mock_llm(r".*Assign exactly one indexed label to each ordered public entry.*", json.dumps({"labels": labels}))
    return contract.compile_sequence("assembly-run", LABELS, ENTRIES, POLICY)


def test_adjacent_equal_labels_are_run_length_compressed(contract, direct_vm, direct_alice):
    compilation_id = _compile(contract, direct_vm, direct_alice, [0, 0, 1, 1, 2])
    assert contract.segment_total(compilation_id) == 3
    assert contract.get_segment(compilation_id, 0)["start"] == 0
    assert contract.get_segment(compilation_id, 0)["end"] == 1
    assert contract.get_segment(compilation_id, 1)["label_index"] == 1


def test_every_segment_requires_a_different_operator(contract, direct_vm, direct_alice, direct_bob):
    compilation_id = _compile(contract, direct_vm, direct_alice, [0, 0, 1, 1, 2])
    contract.assign_segment(compilation_id, 0, direct_bob)
    with direct_vm.expect_revert("operator_already_used"):
        contract.assign_segment(compilation_id, 1, direct_bob)


def test_all_segments_must_be_acknowledged_before_seal(contract, direct_vm, direct_alice, direct_bob, direct_charlie, direct_accounts):
    compilation_id = _compile(contract, direct_vm, direct_alice, [0, 0, 1, 1, 2])
    operators = [direct_bob, direct_charlie, direct_accounts[3]]
    for index, operator in enumerate(operators):
        direct_vm.sender = direct_alice
        contract.assign_segment(compilation_id, index, operator)
        direct_vm.sender = operator
        contract.acknowledge_segment(compilation_id, index, f"Segment {index} assignment has been reviewed and acknowledged.")
    direct_vm.sender = direct_alice
    contract.seal_sequence(compilation_id)
    assert contract.get_compilation(compilation_id)["state"] == "SEALED"


def test_wrong_model_length_is_rejected(contract, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*Assign exactly one indexed label.*", json.dumps({"labels": [0, 1]}))
    with direct_vm.expect_revert("[LLM_ERROR] wrong_label_count"):
        contract.compile_sequence("bad-run", LABELS, ENTRIES, POLICY)


def test_duplicate_key_and_non_owner_assignment_are_rejected(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    compilation_id = _compile(contract, direct_vm, direct_alice, [0, 0, 1, 1, 2])
    with direct_vm.expect_revert("sequence_exists"):
        contract.compile_sequence("ASSEMBLY-RUN", LABELS, ENTRIES, POLICY)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("only_owner"):
        contract.assign_segment(compilation_id, 0, direct_charlie)


def test_only_assigned_operator_can_acknowledge(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    compilation_id = _compile(contract, direct_vm, direct_alice, [0, 0, 1, 1, 2])
    contract.assign_segment(compilation_id, 0, direct_bob)
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only_operator"):
        contract.acknowledge_segment(compilation_id, 0, "I checked the assigned segment and accept responsibility.")


def test_boolean_model_label_is_rejected(contract, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*Assign exactly one indexed label.*", json.dumps({"labels": [0, True, 1, 1, 2]}))
    with direct_vm.expect_revert("[LLM_ERROR] invalid_label_index"):
        contract.compile_sequence("boolean-label", LABELS, ENTRIES, POLICY)
