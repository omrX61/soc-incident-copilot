from src.answer_cleanup import trim_repeated_content


def test_trims_second_heading_block():
    text = (
        "• Evidence: Archive files in temp\n"
        "• Containment: Block egress\n\n"
        "Evidence:\n"
        "- Archive files in temp directories\n\n"
        "Sources:\n"
        "- Playbook\n\n"
        "Immediate actions:\n"
        "1. Block egress\n\n"
        "Evidence:\n"
        "- Archive files again\n"
    )
    trimmed = trim_repeated_content(text)
    assert "again" not in trimmed
    assert trimmed.lower().count("evidence:") == 2


def test_leaves_single_pass_alone():
    text = "Evidence:\n- temp archives\n\nContainment:\n- isolate host\n"
    assert trim_repeated_content(text) == text
