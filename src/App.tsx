import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Check,
  ChevronRight,
  CircleAlert,
  Database,
  FileText,
  FlaskConical,
  Gauge,
  Info,
  Loader2,
  Microscope,
  RotateCcw,
  Sparkles,
  Target,
  UploadCloud,
  X,
  Zap,
} from "lucide-react";
import {
  type ChangeEvent,
  type DragEvent,
  type FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import { useRunExperiment } from "./hooks/useRunExperiment";
import type {
  Experiment,
  ExperimentRunResponse,
} from "./types";

const STAGES = [
  { label: "Dataset analysis", icon: Database },
  { label: "Experiment planning", icon: Microscope },
  { label: "Model execution", icon: FlaskConical },
  { label: "Evaluation", icon: BarChart3 },
  { label: "Next experiment", icon: Zap },
];

const RESEARCH_STAGES = [
  { number: "01", label: "Analyze Dataset", icon: Database },
  { number: "02", label: "Plan Experiment", icon: Microscope },
  { number: "03", label: "Execute Model", icon: FlaskConical },
  { number: "04", label: "Evaluate Result", icon: BarChart3 },
  { number: "05", label: "Choose Next Experiment", icon: Zap },
];

function formatModel(model: string) {
  return model
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatMetric(metric: string) {
  return metric.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatScore(value: number | undefined) {
  return value === undefined ? "—" : `${(value * 100).toFixed(2)}%`;
}

function formatDuration(seconds: number) {
  return `${seconds.toFixed(3)}s`;
}

function scoreFor(experiment: Experiment | null) {
  if (!experiment) return undefined;
  return experiment.result.metrics[experiment.configuration.evaluation_metric];
}

function responseError(error: unknown) {
  if (error instanceof Error) return error.message;
  return "The experiment could not be completed. Check that the API is running.";
}

function StatCard({
  label,
  value,
  detail,
  icon: Icon,
  accent = "mint",
}: {
  label: string;
  value: string;
  detail?: string;
  icon: typeof Activity;
  accent?: "mint" | "orange" | "ink";
}) {
  const accents = {
    mint: "bg-emerald-50 text-emerald-700",
    orange: "bg-orange-50 text-orange-700",
    ink: "bg-slate-100 text-slate-700",
  };

  return (
    <div className="panel group p-4 transition duration-300 hover:-translate-y-0.5 hover:shadow-lift">
      <div className="flex items-start justify-between gap-3">
        <span className="eyebrow">{label}</span>
        <span className={`rounded-lg p-2 ${accents[accent]}`}>
          <Icon size={16} strokeWidth={2.2} />
        </span>
      </div>
      <p className="mt-4 text-2xl font-extrabold tracking-[-0.04em] text-ink">{value}</p>
      {detail && <p className="mt-1 text-xs text-slate-500">{detail}</p>}
    </div>
  );
}

function LoadingPanel() {
  const [activeStage, setActiveStage] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setActiveStage((stage) => (stage + 1) % STAGES.length);
    }, 1800);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="panel overflow-hidden p-6 sm:p-8">
      <div className="flex items-start gap-4">
        <div className="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-ink text-white">
          <Loader2 className="animate-spin" size={20} />
          <span className="absolute -right-1 -top-1 h-2.5 w-2.5 animate-pulse-dot rounded-full bg-signal" />
        </div>
        <div>
          <p className="eyebrow text-emerald-700">Live run</p>
          <h2 className="mt-1 text-xl font-extrabold tracking-[-0.03em] text-ink">Agent is experimenting</h2>
          <p className="mt-1 text-sm text-slate-500">The workflow is evaluating each result before choosing what comes next.</p>
        </div>
      </div>
      <div className="mt-8 space-y-1">
        {STAGES.map((stage, index) => {
          const Icon = stage.icon;
          const isActive = index === activeStage;
          const isDone = index < activeStage;
          return (
            <div key={stage.label} className="flex items-center gap-3">
              <div className="flex w-7 justify-center">
                <span className={`flex h-7 w-7 items-center justify-center rounded-full border text-xs transition-all duration-500 ${isActive ? "border-ink bg-ink text-white shadow-lg" : isDone ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-slate-200 bg-white text-slate-400"}`}>
                  {isDone ? <Check size={14} /> : <Icon size={13} />}
                </span>
              </div>
              <span className={`text-sm font-semibold transition-colors ${isActive ? "text-ink" : isDone ? "text-emerald-700" : "text-slate-400"}`}>{stage.label}</span>
              {isActive && <span className="ml-auto text-[10px] font-bold uppercase tracking-[0.14em] text-signal">In progress</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ExperimentRow({
  experiment,
  isBest,
  selected,
  onSelect,
}: {
  experiment: Experiment;
  isBest: boolean;
  selected: boolean;
  onSelect: () => void;
}) {
  const score = scoreFor(experiment);
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`group grid w-full grid-cols-[1fr_auto] gap-3 border-b border-slate-100 px-4 py-4 text-left transition last:border-0 hover:bg-slate-50 md:grid-cols-[1.3fr_1.4fr_1fr_0.9fr_0.9fr_0.7fr] ${selected ? "bg-emerald-50/55" : "bg-white"}`}
    >
      <div className="flex items-center gap-3">
        <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg font-mono text-[10px] font-medium ${isBest ? "bg-ink text-white" : "bg-slate-100 text-slate-500"}`}>{experiment.experiment_id.split("experiment-").at(-1)?.padStart(2, "0") ?? "--"}</span>
        <div>
          <p className="text-sm font-bold text-ink">{formatModel(experiment.configuration.model)}</p>
          <p className="mt-0.5 text-xs text-slate-500 md:hidden">{formatMetric(experiment.configuration.evaluation_metric)}</p>
        </div>
      </div>
      <span className="hidden self-center text-sm text-slate-600 md:block">{formatModel(experiment.configuration.model)}</span>
      <span className="hidden self-center text-sm text-slate-500 md:block">{formatMetric(experiment.configuration.evaluation_metric)}</span>
      <span className="self-center text-right text-sm font-extrabold text-ink md:text-left">{formatScore(score)}</span>
      <span className="hidden self-center font-mono text-xs text-slate-500 md:block">{formatDuration(experiment.result.training_time_seconds)}</span>
      <span className="flex items-center justify-end gap-2 self-center text-xs font-bold text-emerald-700"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />Success <ChevronRight className="text-slate-300 transition-transform group-hover:translate-x-0.5" size={14} /></span>
    </button>
  );
}

function DetailPanel({ experiment }: { experiment: Experiment | null }) {
  if (!experiment) return null;
  const { configuration, result } = experiment;
  return (
    <div className="border-t border-slate-200/80 bg-slate-50/70 p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="eyebrow">Selected experiment</p>
          <h3 className="mt-1 text-lg font-extrabold tracking-[-0.03em] text-ink">{formatModel(configuration.model)}</h3>
          <p className="mt-1 font-mono text-xs text-slate-500">{configuration.experiment_id}</p>
        </div>
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-right">
          <p className="eyebrow text-emerald-700">{formatMetric(configuration.evaluation_metric)}</p>
          <p className="mt-0.5 text-lg font-extrabold text-emerald-800">{formatScore(scoreFor(experiment))}</p>
        </div>
      </div>
      <div className="mt-6 grid gap-6 sm:grid-cols-3">
        <div>
          <p className="field-label">Preprocessing</p>
          <div className="flex flex-wrap gap-2">{configuration.preprocessing.map((item) => <span key={item} className="rounded-md bg-white px-2.5 py-1.5 font-mono text-xs text-slate-600 ring-1 ring-slate-200">{item}</span>)}</div>
        </div>
        <div>
          <p className="field-label">Hyperparameters</p>
          <div className="space-y-1.5">{Object.entries(configuration.hyperparameters).map(([key, value]) => <div key={key} className="flex items-center justify-between gap-4 text-sm"><span className="font-mono text-xs text-slate-500">{key}</span><span className="font-bold text-ink">{String(value)}</span></div>)}</div>
        </div>
        <div>
          <p className="field-label">Observations</p>
          <ul className="space-y-1.5 text-sm leading-5 text-slate-600">{result.observations.map((observation) => <li key={observation} className="flex gap-2"><span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-signal" />{observation}</li>)}</ul>
        </div>
      </div>
    </div>
  );
}

function ResultsDashboard({ response }: { response: ExperimentRunResponse }) {
  const [selectedId, setSelectedId] = useState(response.best_experiment?.experiment_id ?? response.experiments[0]?.experiment_id ?? null);
  const best = response.best_experiment;
  const selected = response.experiments.find((experiment) => experiment.experiment_id === selectedId) ?? response.experiments[0] ?? null;
  const bestScore = scoreFor(best);
  const dataset = response.dataset_profile;

  return (
    <section className="animate-drift-in space-y-5" aria-label="Experiment results">
      <div role="status" className="flex flex-wrap items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"><Check size={16} /><span className="font-bold">Run completed successfully.</span><span className="font-mono text-xs text-emerald-700">{response.run_id}</span></div>
      <div className="flex flex-wrap items-end justify-between gap-4 pt-3">
        <div>
          <p className="eyebrow text-signal">Run complete</p>
          <h2 className="mt-2 text-2xl font-extrabold tracking-[-0.045em] text-ink sm:text-3xl">Research readout</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{response.report.objective}</p>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 font-mono text-[10px] text-slate-500"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />{response.run_id.slice(0, 18)}…</div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Experiments run" value={String(response.experiments.length)} detail="Within configured budget" icon={FlaskConical} />
        <StatCard label="Best model" value={best ? formatModel(best.configuration.model) : "—"} detail="Top recorded result" icon={Gauge} accent="orange" />
        <StatCard label="Best metric" value={best ? formatMetric(best.configuration.evaluation_metric) : "—"} detail="Primary evaluation" icon={Target} accent="ink" />
        <StatCard label="Best score" value={formatScore(bestScore)} detail={best ? best.experiment_id : "No successful result"} icon={ArrowUpRight} accent="mint" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="panel p-5 sm:p-6">
          <div className="flex items-center justify-between"><div><p className="eyebrow">Dataset overview</p><h3 className="mt-1 text-lg font-extrabold tracking-[-0.03em] text-ink">The data behind the run</h3></div><Database className="text-emerald-600" size={20} /></div>
          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {[["Rows", dataset.rows.toLocaleString()], ["Columns", String(dataset.columns)], ["Task type", formatModel(dataset.task_type)], ["Target", dataset.target_column], ["Duplicates", String(dataset.duplicate_rows)], ["Unique target values", String(dataset.unique_target_values)]].map(([label, value]) => <div key={label} className="rounded-xl bg-slate-50 p-3.5"><p className="text-[11px] font-semibold text-slate-500">{label}</p><p className="mt-2 truncate text-sm font-extrabold text-ink">{value}</p></div>)}
          </div>
          <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-500"><span className="rounded-md border border-slate-200 bg-white px-2.5 py-1.5"><b className="text-ink">{dataset.numerical_columns.length}</b> numerical features</span><span className="rounded-md border border-slate-200 bg-white px-2.5 py-1.5"><b className="text-ink">{dataset.categorical_columns.length}</b> categorical features</span><span className="rounded-md border border-slate-200 bg-white px-2.5 py-1.5"><b className="text-ink">{Object.keys(dataset.missing_value_columns).length}</b> columns with missing values</span></div>
        </section>

        <section className="panel border-ink/10 bg-ink p-5 text-white shadow-lift sm:p-6">
          <div className="flex items-start justify-between gap-4"><div><p className="eyebrow text-emerald-300">Best experiment</p><h3 className="mt-2 text-2xl font-extrabold tracking-[-0.045em]">{best ? formatModel(best.configuration.model) : "No winner yet"}</h3></div><Sparkles className="text-emerald-300" size={22} /></div>
          {best ? <><div className="mt-7 flex items-end justify-between gap-4"><div><p className="text-xs text-slate-400">{formatMetric(best.configuration.evaluation_metric)}</p><p className="mt-1 text-4xl font-extrabold tracking-[-0.06em] text-emerald-300">{formatScore(bestScore)}</p></div><span className="rounded-lg border border-white/10 px-2.5 py-1.5 font-mono text-[10px] text-slate-400">{best.experiment_id}</span></div><div className="mt-7 border-t border-white/10 pt-4"><p className="text-sm leading-6 text-slate-300">{response.report.final_conclusion}</p></div></> : <p className="mt-8 text-sm text-slate-400">No successful experiment with a recorded metric was available.</p>}
        </section>
      </div>

      <section className="panel overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/80 p-5 sm:p-6"><div><p className="eyebrow">Experiment history</p><h3 className="mt-1 text-lg font-extrabold tracking-[-0.03em] text-ink">Compare every attempt</h3></div><span className="rounded-md bg-slate-100 px-2 py-1 font-mono text-[10px] text-slate-500">{response.experiments.length} runs</span></div>
        <div className="hidden md:block"><div className="grid grid-cols-[1.3fr_1.4fr_1fr_0.9fr_0.9fr_0.7fr] gap-3 bg-slate-50/80 px-4 py-3 font-mono text-[10px] font-medium uppercase tracking-[0.12em] text-slate-400"><span>Experiment</span><span>Model</span><span>Metric</span><span>Score</span><span>Time</span><span>Status</span></div>{response.experiments.map((experiment) => <ExperimentRow key={experiment.experiment_id} experiment={experiment} isBest={experiment.experiment_id === best?.experiment_id} selected={experiment.experiment_id === selectedId} onSelect={() => setSelectedId(experiment.experiment_id)} />)}</div>
        <div className="divide-y divide-slate-100 md:hidden">{response.experiments.map((experiment) => <ExperimentRow key={experiment.experiment_id} experiment={experiment} isBest={experiment.experiment_id === best?.experiment_id} selected={experiment.experiment_id === selectedId} onSelect={() => setSelectedId(experiment.experiment_id)} />)}</div>
        <DetailPanel experiment={selected} />
      </section>

      <section className="panel p-5 sm:p-6">
        <div className="flex items-start gap-3"><div className="rounded-lg bg-signal-soft p-2 text-signal"><FileText size={17} /></div><div><p className="eyebrow">Final report</p><h3 className="mt-1 text-lg font-extrabold tracking-[-0.03em] text-ink">A concise research summary</h3></div></div>
        <div className="mt-6 grid gap-6 md:grid-cols-2"><div><p className="field-label">Objective</p><p className="text-sm leading-6 text-slate-600">{response.report.objective}</p></div><div><p className="field-label">Dataset summary</p><p className="text-sm leading-6 text-slate-600">{dataset.rows} rows across {dataset.columns} columns, targeting <b className="text-ink">{dataset.target_column}</b> for {dataset.task_type}.</p></div><div><p className="field-label">Experiment summary</p><p className="text-sm leading-6 text-slate-600">{response.report.experiments.length} experiment{response.report.experiments.length === 1 ? "" : "s"} recorded in this run.</p></div><div><p className="field-label">Best experiment</p><p className="text-sm leading-6 text-slate-600">{response.report.best_experiment ? `${formatModel(response.report.best_experiment.configuration.model)} · ${formatScore(scoreFor(response.report.best_experiment))}` : "No successful experiment was recorded."}</p></div><div><p className="field-label">Key observations</p><ul className="space-y-2 text-sm leading-6 text-slate-600">{response.report.key_observations.map((observation) => <li key={observation} className="flex gap-2"><span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-signal" />{observation}</li>)}</ul></div><div><p className="field-label">Final conclusion</p><p className="text-sm leading-6 text-slate-600">{response.report.final_conclusion}</p></div></div>
      </section>
    </section>
  );
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [objective, setObjective] = useState("Classify iris species and maximize validation accuracy.");
  const [targetColumn, setTargetColumn] = useState("target");
  const [maxExperiments, setMaxExperiments] = useState(3);
  const [dragActive, setDragActive] = useState(false);
  const [formError, setFormError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  const runMutation = useRunExperiment();

  const response = runMutation.data;
  const hasResult = Boolean(response);

  const chooseFile = (nextFile: File | undefined) => {
    if (!nextFile) return;
    if (!nextFile.name.toLowerCase().endsWith(".csv")) {
      setFormError("Please choose a CSV file to start an experiment.");
      return;
    }
    setFormError("");
    setFile(nextFile);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragActive(false);
    chooseFile(event.dataTransfer.files[0]);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setFormError("Add a CSV dataset before running experiments.");
      return;
    }
    if (!objective.trim()) {
      setFormError("Describe the objective before running experiments.");
      return;
    }
    if (!targetColumn.trim()) {
      setFormError("Enter the target column from your dataset.");
      return;
    }
    if (!Number.isInteger(maxExperiments) || maxExperiments < 1 || maxExperiments > 10) {
      setFormError("Choose between 1 and 10 experiments.");
      return;
    }
    setFormError("");
    runMutation.mutate({ file, objective, targetColumn: targetColumn.trim(), maxExperiments });
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => chooseFile(event.target.files?.[0]);
  const clearFile = () => {
    setFile(null);
    if (fileInput.current) fileInput.current.value = "";
  };

  const handleNewExperiment = () => {
    runMutation.reset();
    setFormError("");
    setFile(null);
    if (fileInput.current) fileInput.current.value = "";
  };

  const backendLabel = runMutation.isError ? "Backend attention" : "API ready";
  const backendTone = runMutation.isError ? "text-orange-700 bg-orange-50" : "text-emerald-700 bg-emerald-50";

  return (
    <div className="min-h-screen text-ink">
      <header className="border-b border-slate-200/80 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-5 py-4 sm:px-8 lg:px-10">
          <div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-xl bg-ink text-emerald-300 shadow-sm"><Activity size={18} /></div><div><p className="text-sm font-extrabold tracking-[-0.02em] text-ink">Agentic ML Experimentation</p><p className="mt-0.5 text-[11px] text-slate-500">Autonomous Machine Learning Research Assistant</p></div></div>
          <div className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em] ${backendTone}`}><span className={`h-1.5 w-1.5 rounded-full ${runMutation.isError ? "bg-orange-500" : "bg-emerald-500"}`} />{backendLabel}</div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 pb-16 pt-8 sm:px-8 lg:px-10 lg:pt-12">
        {!hasResult && <>
          <div className="mb-8 max-w-3xl"><p className="eyebrow text-signal">Research workspace / 01</p><h1 className="mt-3 text-3xl font-extrabold leading-tight tracking-[-0.055em] text-ink sm:text-5xl">Turn a dataset into a sharper next experiment.</h1><p className="mt-4 max-w-2xl text-sm leading-7 text-slate-500 sm:text-base">Set the objective, give the agent a target, and let the research loop compare models against recorded evidence.</p></div>

          <div className="grid gap-5 lg:grid-cols-[minmax(0,0.92fr)_minmax(360px,1.08fr)]">
          <section className="panel p-5 sm:p-7"><div className="mb-6 flex items-start justify-between gap-4"><div><p className="eyebrow">Experiment configuration</p><h2 className="mt-1 text-xl font-extrabold tracking-[-0.04em] text-ink">Define the research question</h2></div><span className="rounded-lg bg-slate-100 px-2.5 py-1.5 font-mono text-[10px] text-slate-500">SETUP</span></div>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div><label className="field-label" htmlFor="dataset-upload">Dataset</label><div role="button" tabIndex={0} onClick={() => fileInput.current?.click()} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") fileInput.current?.click(); }} onDragOver={(event) => { event.preventDefault(); setDragActive(true); }} onDragLeave={() => setDragActive(false)} onDrop={handleDrop} className={`group cursor-pointer rounded-xl border border-dashed p-5 transition ${dragActive ? "border-emerald-500 bg-emerald-50" : file ? "border-emerald-200 bg-emerald-50/45" : "border-slate-300 bg-slate-50/65 hover:border-slate-400 hover:bg-slate-50"}`}><input ref={fileInput} id="dataset-upload" type="file" accept=".csv,text/csv" className="sr-only" onChange={handleFileChange} />{file ? <div className="flex items-center gap-3"><div className="rounded-lg bg-white p-2.5 text-emerald-700 shadow-sm"><FileText size={19} /></div><div className="min-w-0 flex-1"><p className="truncate text-sm font-bold text-ink">{file.name}</p><p className="mt-1 font-mono text-[11px] text-slate-500">{(file.size / 1024).toFixed(1)} KB · CSV dataset</p></div><button type="button" aria-label="Remove selected file" onClick={(event) => { event.stopPropagation(); clearFile(); }} className="rounded-lg p-2 text-slate-400 transition hover:bg-white hover:text-signal"><X size={17} /></button></div> : <div className="flex items-center gap-4"><div className="rounded-lg bg-white p-2.5 text-slate-500 shadow-sm transition group-hover:text-emerald-700"><UploadCloud size={20} /></div><div><p className="text-sm font-bold text-ink">Drop a CSV here or browse files</p><p className="mt-1 text-xs text-slate-500">Use a clean tabular dataset with a named target column.</p></div></div>}</div></div>
              <div><label className="field-label" htmlFor="target-column">Target column</label><div className="relative"><Target className="pointer-events-none absolute left-3.5 top-3.5 text-slate-400" size={16} /><input id="target-column" value={targetColumn} onChange={(event) => setTargetColumn(event.target.value)} className="field-control pl-10" placeholder="e.g. target" /></div></div>
              <div><label className="field-label" htmlFor="objective">Objective</label><textarea id="objective" value={objective} onChange={(event) => setObjective(event.target.value)} className="field-control min-h-[116px] resize-y leading-6" placeholder="Describe what you want the system to optimize..." /></div>
              <div><div className="flex items-center justify-between"><label className="field-label mb-0" htmlFor="max-experiments">Maximum experiments</label><span className="font-mono text-xs text-slate-400">1–10</span></div><div className="mt-2 flex items-center gap-3"><input id="max-experiments" type="number" min={1} max={10} value={maxExperiments} onChange={(event) => setMaxExperiments(Number(event.target.value))} className="field-control max-w-[120px] text-center font-bold" /><span className="text-xs text-slate-500">iterations in this run</span></div></div>
              {(formError || runMutation.isError) && <div role="alert" className="flex items-start gap-2 rounded-xl border border-orange-200 bg-orange-50 px-3.5 py-3 text-sm leading-5 text-orange-800"><CircleAlert className="mt-0.5 shrink-0" size={16} />{formError || responseError(runMutation.error)}</div>}
              <button type="submit" disabled={runMutation.isPending} className="flex w-full items-center justify-center gap-2 rounded-xl bg-ink px-4 py-3.5 text-sm font-extrabold text-white shadow-lg shadow-ink/10 transition hover:-translate-y-0.5 hover:bg-slate-700 focus:outline-none focus:ring-4 focus:ring-ink/15 disabled:cursor-wait disabled:opacity-70">{runMutation.isPending ? <><Loader2 className="animate-spin" size={17} />Running research loop…</> : <><Zap size={17} />Run experiments <ArrowUpRight size={16} /></>}</button>
              <p className="flex items-start gap-2 text-xs leading-5 text-slate-500"><Info className="mt-0.5 shrink-0 text-emerald-700" size={14} />The agent will analyze the dataset, run experiments, evaluate results, and use previous outcomes to select subsequent experiments.</p>
            </form>
          </section>

          <div>{runMutation.isPending ? <LoadingPanel /> : <div className="panel flex h-full flex-col justify-between overflow-hidden p-6 sm:p-8"><div><div className="flex items-center justify-between"><span className="eyebrow">Research loop</span><span className="rounded-full border border-slate-200 px-2.5 py-1 font-mono text-[10px] text-slate-500">SYNC</span></div><div className="mt-8 max-w-md"><h2 className="text-2xl font-extrabold leading-tight tracking-[-0.045em] text-ink sm:text-3xl">Evidence first.<br /><span className="text-emerald-700">Reasonable next moves.</span></h2><p className="mt-4 text-sm leading-6 text-slate-500">Each iteration is evaluated, recorded, and made available to the next planning step. The result is a compact trail of decisions you can inspect.</p></div><div className="mt-8 flex flex-col gap-2 sm:flex-row sm:items-stretch sm:gap-0">{RESEARCH_STAGES.map((stage, index) => { const Icon = stage.icon; return <div key={stage.number} className="flex min-w-0 flex-1 items-center gap-2 sm:gap-1.5"><div className="flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-slate-200/80 bg-slate-50/70 px-2.5 py-2.5 sm:block sm:px-3 sm:py-3"><div className="flex items-center gap-2"><span className="font-mono text-[10px] font-medium text-slate-400">{stage.number}</span><Icon className="text-emerald-700" size={15} /></div><p className="ml-6 mt-0.5 truncate text-xs font-bold text-ink sm:ml-0 sm:mt-2 sm:whitespace-normal">{stage.label}</p></div>{index < RESEARCH_STAGES.length - 1 && <ChevronRight className="mx-1 shrink-0 rotate-90 text-slate-300 sm:rotate-0" size={15} />}</div>; })}</div></div><div className="mt-8 grid grid-cols-2 gap-3 sm:mt-10 sm:grid-cols-3"><div className="rounded-xl bg-slate-50 p-3.5"><p className="eyebrow">Models</p><p className="mt-2 text-sm font-extrabold text-ink">3 supported</p></div><div className="rounded-xl bg-slate-50 p-3.5"><p className="eyebrow">Evaluation</p><p className="mt-2 text-sm font-extrabold text-ink">Accuracy</p></div><div className="rounded-xl bg-signal-soft p-3.5"><p className="eyebrow text-signal">Output</p><p className="mt-2 text-sm font-extrabold text-ink">Research report</p></div></div></div>}</div>
          </div>
        </>}

        {response && <div className="mt-12"><ResultsDashboard response={response} /></div>}
        {response && <button type="button" onClick={handleNewExperiment} className="mx-auto mt-8 flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-bold text-slate-500 transition hover:bg-white hover:text-ink"><RotateCcw size={14} />New experiment</button>}
      </main>
    </div>
  );
}
