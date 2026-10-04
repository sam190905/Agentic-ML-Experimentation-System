"""Simple, deterministic LangGraph workflow for ML experimentation."""

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentState
from app.experimentation.executor import ExperimentExecutor
from app.memory.experiment_memory import ExperimentMemory
from app.agent.planner import ExperimentPlanner
from app.profiler.dataset_profiler import DatasetProfiler
from app.schemas.experiment import ExperimentConfig


experiment_memory: ExperimentMemory | None = None


def profile_node(state: AgentState) -> dict[str, Any]:
    """Profile the dataset using the configured target column."""
    profile = DatasetProfiler().profile(state["data"], state["target_column"])
    return {"dataset_profile": profile}


def plan_node(state: AgentState) -> dict[str, Any]:
    """Create the next experiment configuration using the planner."""
    dataset_profile = state["dataset_profile"]
    if dataset_profile is None:
        raise ValueError("Dataset profile is required before planning")

    decision = ExperimentPlanner().plan(
        state["objective"],
        dataset_profile,
        state["experiment_history"],
    )
    experiment_number = state["experiment_count"] + 1
    experiment = ExperimentConfig(
        experiment_id=f"{state['run_id']}-experiment-{experiment_number}",
        task_type=dataset_profile.task_type,
        target_column=dataset_profile.target_column,
        model=decision.model,
        preprocessing=decision.preprocessing,
        hyperparameters=decision.hyperparameters,
        evaluation_metric=decision.evaluation_metric,
        planning_reason=decision.reason,
    )
    return {"current_experiment": experiment}


def execute_node(state: AgentState) -> dict[str, Any]:
    """Execute the current experiment against the dataset."""
    if state["current_experiment"] is None:
        raise ValueError("Current experiment is required before execution")

    result = ExperimentExecutor().execute(
        state["data"], state["current_experiment"]
    )
    return {"latest_result": result}


def save_node(state: AgentState) -> dict[str, Any]:
    """Persist the latest experiment and add it to the in-memory history."""
    global experiment_memory

    if state["current_experiment"] is None or state["latest_result"] is None:
        raise ValueError("Experiment and result are required before saving")

    experiment = state["current_experiment"]
    result = state["latest_result"]
    if experiment_memory is None:
        experiment_memory = ExperimentMemory()
    experiment_memory.save_experiment(experiment, result)
    history = state["experiment_history"] + [(experiment, result)]
    return {
        "experiment_history": history,
        "experiment_count": state["experiment_count"] + 1,
    }


def route_after_save(state: AgentState) -> str:
    """Continue planning while experiments remain in the budget."""
    if state["experiment_count"] < state["max_experiments"]:
        return "continue"
    return "end"


builder = StateGraph(AgentState)
builder.add_node("profile", profile_node)
builder.add_node("plan", plan_node)
builder.add_node("execute", execute_node)
builder.add_node("save", save_node)
builder.add_edge(START, "profile")
builder.add_edge("profile", "plan")
builder.add_edge("plan", "execute")
builder.add_edge("execute", "save")
builder.add_conditional_edges(
    "save",
    route_after_save,
    {
        "continue": "plan",
        "end": END,
    },
)

graph = builder.compile()