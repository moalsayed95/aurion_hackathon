from aurion_claim_workflow.models import (
    ClassificationResult,
    DecisionResult,
    ExtractedClaimData,
)


def test_classification_result_parses():
    raw = '{"document_type":"new_claim","urgency":"high","confidence":0.95,"reasoning":"Schadensmeldung"}'
    result = ClassificationResult.model_validate_json(raw)
    assert result.document_type == "new_claim"
    assert result.urgency == "high"
    assert result.confidence == 0.95


def test_extracted_claim_data_parses():
    raw = (
        '{"policy_number":"WH-2024-881234","customer_name":"Maria Huber",'
        '"incident_date":"2026-03-15","claim_amount":3200.0,"damage_type":"Wasserschaden",'
        '"incident_description":"Rohrbruch","missing_fields":[],"data_quality_score":0.9}'
    )
    result = ExtractedClaimData.model_validate_json(raw)
    assert result.policy_number == "WH-2024-881234"
    assert result.claim_amount == 3200.0
    assert result.missing_fields == []


def test_extracted_claim_data_with_missing_fields():
    raw = (
        '{"policy_number":null,"customer_name":"Anna Berger",'
        '"incident_date":null,"claim_amount":null,"damage_type":"Autoschaden",'
        '"incident_description":null,"missing_fields":["policy_number","incident_date","claim_amount"],'
        '"data_quality_score":0.3}'
    )
    result = ExtractedClaimData.model_validate_json(raw)
    assert result.policy_number is None
    assert len(result.missing_fields) == 3


def test_decision_result_parses():
    raw = '{"action":"auto_process","reasoning":"Alle Daten vorhanden","priority":"normal"}'
    result = DecisionResult.model_validate_json(raw)
    assert result.action == "auto_process"

    raw2 = '{"action":"escalate","reasoning":"Hoher Betrag","priority":"critical"}'
    result2 = DecisionResult.model_validate_json(raw2)
    assert result2.action == "escalate"
