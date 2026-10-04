from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

import app.agent.planner as planner_module
from app.agent.planner import ExperimentPlanner
from app.schemas.agent import AgentDecision
from app.schemas.dataset import DatasetProfile
from app.schemas.experiment import ExperimentConfig, ExperimentResult


@pytest.fixture
def dataset_profile() -> DatasetProfile:
    return DatasetProfile(
        rows=4,
        columns=2,
        target_column="target",
        task_type="classification",
        numerical_columns=["feature"],
        categorical_columns=[],
        missing_value_columns={},
        duplicate_rows=0,
        unique_target_values=2,
        target_distribution={"0": 2, "1": 2},
    )


@pytest.fixture
def experiment_history() -> list[tuple[ExperimentConfig, ExperimentResult]]:
    return [
        (
            ExperimentConfig(
                experiment_id="experiment-1",
                task_type="classification",
                target_column="target",
                model="logistic_regression",
                preprocessing=["standard_scaler"],
                hyperparameters={"C": 1.0},
                evaluation_metric="accuracy",
            ),
            ExperimentResult(
                experiment_id="experiment-1",
                status="success",
                metrics={"accuracy": 0.9},
                training_time_seconds=0.2,
                observations=["Baseline completed"],
            ),
        )
    ]


@pytest.fixture
def mocked_structured_model(monkeypatch) -> tuple[MagicMock, AgentDecision]:
    decision = AgentDecision(
        config_id="rf-default",
        reason="A tree-based model provides a useful alternative baseline.",
    )
    structured_model = MagicMock()
    structured_model.invoke.return_value = decision
    chat_google = MagicMock()
    chat_google.return_value.with_structured_output.return_value = structured_model
    monkeypatch.setattr(
        planner_module, "ChatGoogleGenerativeAI", chat_google
    )
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    return structured_model, decision


def test_planner_returns_agent_decision(
    dataset_profile: DatasetProfile,
    mocked_structured_model: tuple[MagicMock, AgentDecision],
) -> None:
    structured_model, expected_decision = mocked_structured_model
    decision = ExperimentPlanner().plan("Classify records", dataset_profile, [])

    assert decision == expected_decision
    structured_model.invoke.assert_called_once()


def test_planner_preserves_reason(
    dataset_profile: DatasetProfile,
    mocked_structured_model: tuple[MagicMock, AgentDecision],
) -> None:
    _, expected_decision = mocked_structured_model
    decision = ExperimentPlanner().plan("Classify records", dataset_profile, [])

    assert decision.reason == expected_decision.reason


def test_planner_passes_history_to_prompt(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
    mocked_structured_model: tuple[MagicMock, AgentDecision],
) -> None:
    structured_model, _ = mocked_structured_model
    ExperimentPlanner().plan("Classify records", dataset_profile, experiment_history)

    prompt = structured_model.invoke.call_args.args[0]
    assert "experiment-1" in prompt
    assert "Baseline completed" in prompt
    assert "0.9" in prompt


def test_planner_passes_dataset_profile_to_prompt(
    dataset_profile: DatasetProfile,
    mocked_structured_model: tuple[MagicMock, AgentDecision],
) -> None:
    structured_model, _ = mocked_structured_model
    decision = ExperimentPlanner().plan("Classify records", dataset_profile, [])

    prompt = structured_model.invoke.call_args.args[0]
    assert dataset_profile.model_dump_json() in prompt


def test_planner_passes_objective_to_prompt(
    dataset_profile: DatasetProfile,
    mocked_structured_model: tuple[MagicMock, AgentDecision],
) -> None:
    structured_model, _ = mocked_structured_model
    objective = "Classify customer records"
    ExperimentPlanner().plan(objective, dataset_profile, [])

    prompt = structured_model.invoke.call_args.args[0]
    assert objective in prompt


def test_invalid_agent_decision_is_rejected() -> None:
    with pytest.raises(ValidationError):
        # Validation error if missing required fields
        AgentDecision(
            reason="Unsupported model",
        )


def test_planner_retries_transient_errors(
    dataset_profile: DatasetProfile,
    mocked_structured_model: tuple[MagicMock, AgentDecision],
    monkeypatch,
) -> None:
    structured_model, expected_decision = mocked_structured_model
    structured_model.invoke.side_effect = [
        RuntimeError("503 UNAVAILABLE"),
        RuntimeError("429 RESOURCE_EXHAUSTED"),
        expected_decision,
    ]
    waits: list[int] = []
    monkeypatch.setattr(planner_module.time, "sleep", waits.append)

    decision = ExperimentPlanner().plan("Classify records", dataset_profile, [])

    assert decision == expected_decision
    assert waits == [2, 4]
    assert structured_model.invoke.call_count == 3


def test_planner_does_not_retry_non_transient_errors(
    dataset_profile: DatasetProfile,
    mocked_structured_model: tuple[MagicMock, AgentDecision],
    monkeypatch,
) -> None:
    structured_model, _ = mocked_structured_model
    error = ValueError("Invalid structured response")
    structured_model.invoke.side_effect = error
    sleep = MagicMock()
    monkeypatch.setattr(planner_module.time, "sleep", sleep)

    with pytest.raises(ValueError) as caught:
        ExperimentPlanner().plan("Classify records", dataset_profile, [])

    assert caught.value is error
    structured_model.invoke.assert_called_once()
    sleep.assert_not_called()


def test_planner_reraises_after_three_transient_retries(
    dataset_profile: DatasetProfile,
    mocked_structured_model: tuple[MagicMock, AgentDecision],
    monkeypatch,
) -> None:
    structured_model, _ = mocked_structured_model
    error = RuntimeError("503 UNAVAILABLE")
    structured_model.invoke.side_effect = [error, error, error, error]
    waits: list[int] = []
    monkeypatch.setattr(planner_module.time, "sleep", waits.append)

    with pytest.raises(RuntimeError) as caught:
        ExperimentPlanner().plan("Classify records", dataset_profile, [])

    assert caught.value is error
    assert waits == [2, 4, 8]
    assert structured_model.invoke.call_count == 4


def build_config_history(
    config_ids: list[str],
) -> list[tuple[ExperimentConfig, ExperimentResult]]:
    return [
        (
            ExperimentConfig(
                experiment_id=f"{c_id}-experiment",
                config_id=c_id,
                task_type="classification",
                target_column="target",
                model="some_model",
                preprocessing=["standard_scaler"],
                hyperparameters={},
                evaluation_metric="accuracy",
            ),
            ExperimentResult(
                experiment_id=f"{c_id}-experiment",
                status="success",
                metrics={"accuracy": 0.8},
                training_time_seconds=0.1,
                observations=[],
            ),
        )
        for c_id in config_ids
    ]


def test_fallback_provider_does_not_call_gemini(
    dataset_profile: DatasetProfile, monkeypatch
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fallback")
    gemini = MagicMock(side_effect=AssertionError("Gemini should not be called"))
    monkeypatch.setattr(planner_module, "ChatGoogleGenerativeAI", gemini)

    decision = ExperimentPlanner().plan("Classify records", dataset_profile, [])

    assert isinstance(decision, AgentDecision)
    gemini.assert_not_called()


def test_fallback_selects_logistic_regression_first(
    dataset_profile: DatasetProfile, monkeypatch
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fallback")

    decision = ExperimentPlanner().plan("Classify records", dataset_profile, [])

    assert decision.config_id == "lr-default"
    assert decision.reason == (
        "Deterministic development/demo fallback selected "
        "lr-default because it has not been tried yet for "
        "the objective: Classify records"
    )


def test_fallback_selects_random_forest_after_logistic(
    dataset_profile: DatasetProfile, monkeypatch
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fallback")

    decision = ExperimentPlanner().plan(
        "Classify records",
        dataset_profile,
        build_config_history(["lr-default"]),
    )

    assert decision.config_id == "rf-default"


def test_fallback_selects_gradient_boosting_after_previous_models(
    dataset_profile: DatasetProfile, monkeypatch
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fallback")

    decision = ExperimentPlanner().plan(
        "Classify records",
        dataset_profile,
        build_config_history(["lr-default", "rf-default"]),
    )

    assert decision.config_id == "gb-default"


def test_fallback_avoids_repeating_existing_models(
    dataset_profile: DatasetProfile, monkeypatch
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fallback")
    existing_configs = ["lr-default", "rf-default"]

    decision = ExperimentPlanner().plan(
        "Classify records",
        dataset_profile,
        build_config_history(existing_configs),
    )

    assert decision.config_id not in existing_configs
