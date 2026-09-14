from src.query_policy import is_smalltalk, policy_for


def test_smalltalk_does_not_trigger_rag():
    policy = policy_for("merhaba")
    assert policy.smalltalk is True
    assert policy.skip_rag is True
    assert policy.max_tokens <= 96


def test_incident_question_uses_rag():
    policy = policy_for("ransomware uyarısı?")
    assert policy.smalltalk is False
    assert policy.skip_rag is False
    assert is_smalltalk("ransomware uyarısı?") is False
    assert is_smalltalk("hello") is True
