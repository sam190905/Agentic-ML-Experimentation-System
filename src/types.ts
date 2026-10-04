export type DatasetProfile = {
  rows: number;
  columns: number;
  target_column: string;
  task_type: "classification" | "regression";
  numerical_columns: string[];
  categorical_columns: string[];
  missing_value_columns: Record<string, number>;
  duplicate_rows: number;
  unique_target_values: number;
  target_distribution: Record<string, number>;
};

export type ExperimentConfiguration = {
  experiment_id: string;
  task_type: "classification" | "regression";
  target_column: string;
  model: string;
  preprocessing: string[];
  hyperparameters: Record<string, string | number | boolean>;
  evaluation_metric: string;
  planning_reason?: string;
};

export type ExperimentResult = {
  experiment_id: string;
  status: "success" | "failed";
  metrics: Record<string, number>;
  training_time_seconds: number;
  observations: string[];
};

export type Experiment = {
  experiment_id: string;
  configuration: ExperimentConfiguration;
  result: ExperimentResult;
};

export type BestExperiment = Experiment | null;

export type Report = {
  objective: string;
  dataset_summary: DatasetProfile;
  experiments: Experiment[];
  best_experiment: BestExperiment;
  key_observations: string[];
  final_conclusion: string;
};

export type ExperimentRunResponse = {
  run_id: string;
  dataset_profile: DatasetProfile;
  experiments: Experiment[];
  best_experiment: BestExperiment;
  report: Report;
};

export type RunExperimentInput = {
  file: File;
  objective: string;
  targetColumn: string;
  maxExperiments: number;
};
