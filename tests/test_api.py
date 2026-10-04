from io import BytesIO

from fastapi.testclient import TestClient

from app.api.main import app


def test_run_experiment_response_contains_planning_reason(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fallback")
    client = TestClient(app)
    response = client.post(
        "/api/experiments/run",
        files={
            "file": (
                "dataset.csv",
                BytesIO(b"feature,target\n1,0\n2,0\n3,1\n4,1\n"),
                "text/csv",
            )
        },
        data={
            "objective": "Classify the records.",
            "target_column": "target",
            "max_experiments": "1",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    experiment = payload["experiments"][0]
    assert experiment["configuration"]["planning_reason"]
    assert (
        experiment["configuration"]["planning_reason"]
        == payload["report"]["experiments"][0]["configuration"]["planning_reason"]
    )
