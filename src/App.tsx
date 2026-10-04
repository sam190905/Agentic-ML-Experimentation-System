import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Check,
  ChevronRight,
  CircleAlert,
  Code2,
  Database,
  FileText,
  FlaskConical,
  Github,
  Gauge,
  Info,
  Loader2,
  Linkedin,
  Mail,
  Moon,
  Microscope,
  RotateCcw,
  Sparkles,
  Target,
  UploadCloud,
  X,
  Zap,
  Sun,
} from "lucide-react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";
import {
  type ChangeEvent,
  type DragEvent,
  type FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import type { ReactNode } from "react";
import { createContext, useContext } from "react";

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
  { number: "04", label: "Evaluate Evidence", icon: BarChart3 },
  { number: "05", label: "Choose Next Experiment", icon: Zap },
];

type Theme = "light" | "dark";
type ThemeContextValue = { theme: Theme; toggleTheme: () => void };
const ThemeContext = createContext<ThemeContextValue | null>(null);

function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem("agentic-theme");
    if (saved === "light" || saved === "dark") return saved;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    localStorage.setItem("agentic-theme", nextTheme);
  };

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>;
}

function ThemeToggle() {
  const context = useContext(ThemeContext);
  if (!context) return null;
  const isDark = context.theme === "dark";
  return <button type="button" onClick={context.toggleTheme} aria-label={`Switch to ${isDark ? "light" : "dark"} mode`} title={`Switch to ${isDark ? "light" : "dark"} mode`} className="rounded-full border border-slate-200 p-2 text-slate-500 transition hover:border-emerald-500 hover:text-emerald-700 focus:outline-none focus:ring-4 focus:ring-emerald-500/15 dark:border-white/10 dark:text-slate-300 dark:hover:border-emerald-400 dark:hover:text-emerald-300">{isDark ? <Sun size={15} /> : <Moon size={15} />}</button>;
}

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

const RUN_STORAGE_PREFIX = "agentic-ml-experiment-run:";

function storeRun(response: ExperimentRunResponse) {
  sessionStorage.setItem(`${RUN_STORAGE_PREFIX}${response.run_id}`, JSON.stringify(response));
}

function loadRun(runId: string): ExperimentRunResponse | null {
  const stored = sessionStorage.getItem(`${RUN_STORAGE_PREFIX}${runId}`);
  if (!stored) return null;
  try {
    return JSON.parse(stored) as ExperimentRunResponse;
  } catch {
    return null;
  }
}

function AnimatedHeroHeadline() {
  const phrases = ["Give it a\ndataset.", "Let it find\nthe next experiment."];
  const [display, setDisplay] = useState({ phraseIndex: 0, count: 0 });
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) {
      setDisplay({ phraseIndex: 1, count: phrases[1].length });
      setIsTyping(false);
      return;
    }

    let phraseIndex = 0;
    let characterCount = 0;
    let phase: "typing" | "pause" | "deleting" | "transition" = "typing";
    let cancelled = false;
    let timer = 0;

    const tick = () => {
      if (cancelled) return;
      const phrase = phrases[phraseIndex];
      if (phase === "typing") {
        characterCount += 1;
        setDisplay({ phraseIndex, count: characterCount });
        setIsTyping(true);
        if (characterCount >= phrase.length) {
          phase = "pause";
          setIsTyping(false);
          timer = window.setTimeout(tick, 2700);
        } else {
          timer = window.setTimeout(tick, 1750 / phrase.length);
        }
        return;
      }
      if (phase === "pause") {
        phase = "deleting";
        setIsTyping(false);
        timer = window.setTimeout(tick, 900 / phrase.length);
        return;
      }
      if (phase === "deleting") {
        characterCount -= 1;
        setDisplay({ phraseIndex, count: characterCount });
        if (characterCount <= 0) {
          phase = "transition";
          timer = window.setTimeout(tick, 500);
        } else {
          timer = window.setTimeout(tick, 900 / phrase.length);
        }
        return;
      }
      phraseIndex = phraseIndex === 0 ? 1 : 0;
      characterCount = 0;
      phase = "typing";
      setDisplay({ phraseIndex, count: 0 });
      setIsTyping(true);
      timer = window.setTimeout(tick, 1750 / phrases[phraseIndex].length);
    };

    timer = window.setTimeout(tick, 1750 / phrases[0].length);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, []);

  const phrase = phrases[display.phraseIndex];
  const visibleText = phrase.slice(0, display.count);
  const lineBreak = visibleText.indexOf("\n");
  const firstLine = lineBreak === -1 ? visibleText : visibleText.slice(0, lineBreak);
  const secondLine = lineBreak === -1 ? "" : visibleText.slice(lineBreak + 1);
  return (
    <h1 aria-label="Give it a dataset. Let it find the next experiment." className="editorial-heading mt-5 text-5xl font-extrabold leading-[0.98] tracking-[-0.075em] text-ink sm:text-7xl lg:text-[6.8rem]">
      <span aria-hidden="true" className="relative block min-h-[1.96em]">
        <span className="invisible block whitespace-pre-line">{phrases[1]}</span>
        <span className="absolute left-0 top-0 block">
          <span className={display.phraseIndex === 1 ? "text-emerald-800" : "text-ink"}>{firstLine}</span>
          <br />
          <span className="text-ink">{secondLine}</span>
          {isTyping && <motion.span aria-hidden="true" animate={{ opacity: [1, 0.25, 1] }} transition={{ duration: 0.8, repeat: Infinity, ease: "easeInOut" }} className="ml-1 inline-block h-[0.78em] w-[0.055em] translate-y-[0.05em] bg-current align-baseline" />}
        </span>
      </span>
    </h1>
  );
}

function Reveal({ children, delay = 0, className = "" }: { children: ReactNode; delay?: number; className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 22 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

function ResearchField() {
  const { scrollYProgress } = useScroll();
  const lineY = useTransform(scrollYProgress, [0, 1], [0, 190]);
  return (
    <div className="research-field" aria-hidden="true">
      <div className="research-grid" />
      <motion.div className="research-scan" style={{ y: lineY }} />
      <div className="research-node node-one" />
      <div className="research-node node-two" />
      <div className="research-node node-three" />
      <div className="research-connector connector-one" />
      <div className="research-connector connector-two" />
    </div>
  );
}

function DataFlowVisual() {
  const flow = [
    { label: "DATASET", detail: "Signals in", icon: Database },
    { label: "AGENT", detail: "Decisions out", icon: Microscope },
    { label: "EXPERIMENT", detail: "Evidence forward", icon: FlaskConical },
  ];
  return (
    <div className="relative flex h-full min-h-[340px] flex-col justify-center overflow-hidden rounded-[1.75rem] border border-emerald-900/10 bg-[#e9f0e8]/75 px-6 py-8 sm:px-10">
      <div className="absolute right-8 top-8 font-mono text-[10px] uppercase tracking-[0.18em] text-emerald-800/45">system / loop-01</div>
      <div className="space-y-1">
        {flow.map((item, index) => {
          const Icon = item.icon;
          return (
            <div key={item.label}>
              <motion.div
                initial={{ opacity: 0, x: 14 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.55, delay: index * 0.12 }}
                className="flex items-center gap-4 border-b border-emerald-900/10 py-5"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-emerald-900/15 bg-white/65 text-emerald-800"><Icon size={18} /></span>
                <div className="flex-1"><p className="font-mono text-[10px] font-medium tracking-[0.2em] text-emerald-900/45">0{index + 1}</p><p className="mt-1 text-sm font-extrabold tracking-[0.06em] text-ink">{item.label}</p></div>
                <span className="text-xs text-emerald-900/55">{item.detail}</span>
              </motion.div>
              {index < flow.length - 1 && <div className="ml-5 h-3 w-px bg-emerald-900/20" />}
            </div>
          );
        })}
      </div>
      <p className="mt-7 max-w-xs text-xs leading-5 text-emerald-950/60">A compact handoff from raw data to a recorded research trail.</p>
    </div>
  );
}

function WorkflowStory() {
  return (
    <section id="how-it-works" className="scroll-mt-24 border-y border-slate-200/80 bg-white/35 py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-10">
        <Reveal className="max-w-3xl">
          <p className="eyebrow text-signal">The research loop</p>
          <h2 className="editorial-heading mt-4 text-4xl font-extrabold tracking-[-0.06em] text-ink sm:text-6xl">Every result changes<br /><span className="text-emerald-800">the next move.</span></h2>
          <p className="mt-6 max-w-xl text-sm leading-7 text-slate-500 sm:text-base">The agent keeps the work legible. It turns each run into evidence, then uses that evidence to choose a more informed next experiment.</p>
        </Reveal>
        <div className="mt-14 grid gap-3 sm:grid-cols-5">
          {RESEARCH_STAGES.map((stage, index) => {
            const Icon = stage.icon;
            return (
              <Reveal key={stage.number} delay={index * 0.07} className="relative">
                <div className="h-full border-t-2 border-emerald-900/15 pt-4">
                  <div className="flex items-center justify-between"><span className="font-mono text-xs text-signal">{stage.number}</span><Icon className="text-emerald-800" size={18} /></div>
                  <p className="mt-8 max-w-[130px] text-sm font-extrabold leading-5 text-ink">{stage.label}</p>
                </div>
                {index < RESEARCH_STAGES.length - 1 && <ChevronRight className="absolute -right-2.5 top-4 hidden bg-[#f5f7f5] text-slate-300 sm:block" size={17} />}
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function LandingFooter() {
  const links = [
    { label: "GitHub", href: "https://github.com/sam190905", icon: Github },
    { label: "LinkedIn", href: "https://www.linkedin.com/in/samarth-purant-0560a2301", icon: Linkedin },
    { label: "Email", href: "mailto:samarthpurant018@gmail.com", icon: Mail },
    { label: "LeetCode", href: "https://leetcode.com/u/Sam190905/", icon: Code2 },
  ];

  return (
    <footer className="relative z-10 border-t border-slate-200/80 bg-white/45">
      <div className="mx-auto max-w-7xl px-5 py-12 sm:px-8 sm:py-14 lg:px-10">
        <div className="flex flex-col justify-between gap-10 md:flex-row md:items-start">
          <div className="max-w-sm">
            <p className="text-base font-extrabold tracking-[-0.02em] text-ink">Agentic ML Experimentation</p>
            <p className="mt-2 text-xs font-semibold uppercase tracking-[0.12em] text-emerald-800">Autonomous Machine Learning Research Assistant</p>
            <p className="mt-4 text-sm leading-6 text-slate-500">Built with React, FastAPI, LangGraph and Scikit-learn.</p>
          </div>
          <nav className="flex flex-wrap gap-x-6 gap-y-3" aria-label="Social links">
            {links.map(({ label, href, icon: Icon }) => <a key={label} href={href} target={label === "Email" ? undefined : "_blank"} rel={label === "Email" ? undefined : "noreferrer"} className="group flex items-center gap-2 text-sm font-bold text-slate-500 transition hover:text-ink focus:outline-none focus:ring-4 focus:ring-emerald-500/15" aria-label={label}><Icon size={16} className="text-emerald-700 transition-transform group-hover:-translate-y-0.5" />{label}</a>)}
          </nav>
        </div>
        <div className="mt-10 flex flex-col gap-2 border-t border-slate-200/80 pt-5 font-mono text-[10px] uppercase tracking-[0.14em] text-slate-400 sm:flex-row sm:items-center sm:justify-between"><span>© 2026 Agentic ML Experimentation</span><span>Built by Samarth Purant</span></div>
      </div>
    </footer>
  );
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

function ResultsPage() {
  const navigate = useNavigate();
  const { runId } = useParams<{ runId: string }>();
  const response = runId ? loadRun(runId) : null;

  return (
    <div className="relative min-h-screen overflow-hidden text-ink">
      <ResearchField />
      <header className="sticky top-0 z-40 border-b border-slate-200/75 bg-[#f5f7f5]/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-5 py-4 sm:px-8 lg:px-10">
          <button type="button" onClick={() => navigate("/")} className="flex items-center gap-3 text-left"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-ink text-emerald-300 shadow-sm"><Activity size={18} /></span><span><span className="block text-sm font-extrabold tracking-[-0.02em] text-ink">Agentic ML Experimentation</span><span className="mt-0.5 block text-[10px] uppercase tracking-[0.16em] text-slate-500">Research readout</span></span></button>
          <div className="flex items-center gap-2"><ThemeToggle /><button type="button" onClick={() => navigate("/")} className="flex items-center gap-2 rounded-full bg-ink px-4 py-2.5 text-xs font-extrabold text-white transition hover:-translate-y-0.5 hover:bg-slate-700"><RotateCcw size={14} />New experiment</button></div>
        </div>
      </header>
      <main className="relative z-10 mx-auto max-w-7xl px-5 pb-16 pt-10 sm:px-8 lg:px-10 lg:pt-14">
        {response ? <ResultsDashboard response={response} /> : <div className="panel mx-auto max-w-xl p-8 text-center"><CircleAlert className="mx-auto text-orange-600" size={24} /><h1 className="mt-4 text-2xl font-extrabold tracking-[-0.04em] text-ink">This result is no longer available</h1><p className="mt-3 text-sm leading-6 text-slate-500">Results are kept for this browser session only because the backend does not expose a run retrieval endpoint.</p><button type="button" onClick={() => navigate("/")} className="mt-6 rounded-full bg-ink px-4 py-3 text-sm font-extrabold text-white transition hover:bg-slate-700">Back to experiments</button></div>}
      </main>
    </div>
  );
}

function LandingPage() {
  const [file, setFile] = useState<File | null>(null);
  const [objective, setObjective] = useState("Classify iris species and maximize validation accuracy.");
  const [targetColumn, setTargetColumn] = useState("target");
  const [maxExperiments, setMaxExperiments] = useState(3);
  const [dragActive, setDragActive] = useState(false);
  const [formError, setFormError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  const runMutation = useRunExperiment();
  const scrollTo = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
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
    if (!file) return setFormError("Add a CSV dataset before running experiments.");
    if (!objective.trim()) return setFormError("Describe the objective before running experiments.");
    if (!targetColumn.trim()) return setFormError("Enter the target column from your dataset.");
    if (!Number.isInteger(maxExperiments) || maxExperiments < 1 || maxExperiments > 10) return setFormError("Choose between 1 and 10 experiments.");
    setFormError("");
    runMutation.mutate(
      { file, objective, targetColumn: targetColumn.trim(), maxExperiments },
      {
        onSuccess: (result) => {
          storeRun(result);
          navigate(`/results/${encodeURIComponent(result.run_id)}`);
        },
      },
    );
  };
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => chooseFile(event.target.files?.[0]);
  const clearFile = () => {
    setFile(null);
    if (fileInput.current) fileInput.current.value = "";
  };
  const navigate = useNavigate();
  const backendLabel = runMutation.isError ? "Backend attention" : "System ready";
  const backendTone = runMutation.isError ? "text-orange-700 bg-orange-50" : "text-emerald-700 bg-emerald-50";

  return (
    <div className="relative min-h-screen overflow-hidden text-ink">
      <ResearchField />
      <header className="sticky top-0 z-40 border-b border-slate-200/75 bg-[#f5f7f5]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-5 py-4 sm:px-8 lg:px-10">
          <button type="button" onClick={() => scrollTo("research")} className="flex items-center gap-3 text-left"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-ink text-emerald-300 shadow-sm"><Activity size={18} /></span><span><span className="block text-sm font-extrabold tracking-[-0.02em] text-ink">Agentic ML Experimentation</span><span className="mt-0.5 block text-[10px] uppercase tracking-[0.16em] text-slate-500">Research assistant</span></span></button>
          <nav className="hidden items-center gap-7 md:flex" aria-label="Primary navigation"><button type="button" onClick={() => scrollTo("research")} className="text-xs font-bold text-slate-500 transition hover:text-ink">Research</button><button type="button" onClick={() => scrollTo("experiments")} className="text-xs font-bold text-slate-500 transition hover:text-ink">Experiments</button><button type="button" onClick={() => scrollTo("how-it-works")} className="text-xs font-bold text-slate-500 transition hover:text-ink">How it works</button></nav>
          <div className="flex items-center gap-3"><span className={`hidden items-center gap-2 rounded-full px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.1em] sm:flex ${backendTone}`}><span className={`h-1.5 w-1.5 rounded-full ${runMutation.isError ? "bg-orange-500" : "bg-emerald-500"}`} />{backendLabel}</span><ThemeToggle /><button type="button" onClick={() => scrollTo("experiments")} className="rounded-full bg-ink px-4 py-2.5 text-xs font-extrabold text-white transition hover:-translate-y-0.5 hover:bg-slate-700">Start experiment</button></div>
        </div>
      </header>

      <main className="relative z-10">
        <section id="research" className="scroll-mt-20">
          <div className="mx-auto flex min-h-[calc(100svh-72px)] max-w-7xl flex-col justify-center px-5 pb-20 pt-20 sm:px-8 lg:px-10 lg:pb-24 lg:pt-24">
            <div className="grid items-center gap-12 lg:grid-cols-[1.15fr_0.85fr] lg:gap-20">
              <Reveal><p className="eyebrow text-signal">AI-powered ML research agent</p><AnimatedHeroHeadline /><p className="mt-8 max-w-xl text-base leading-7 text-slate-500 sm:text-lg">An autonomous experimentation system that analyzes your data, runs controlled experiments, learns from results, and builds an evidence-backed research trail.</p><div className="mt-9 flex flex-wrap items-center gap-5"><button type="button" onClick={() => scrollTo("experiments")} className="group flex items-center gap-3 rounded-full bg-ink px-5 py-3.5 text-sm font-extrabold text-white shadow-xl shadow-ink/10 transition hover:-translate-y-0.5 hover:bg-slate-700">Start an experiment <ArrowUpRight className="transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" size={17} /></button><span className="font-mono text-[10px] uppercase tracking-[0.14em] text-slate-400">Dataset analysis · Planning · Evaluation · Report</span></div></Reveal>
              <Reveal delay={0.15} className="hidden lg:block"><div className="relative mx-auto h-[420px] w-full max-w-[440px]"><div className="absolute inset-x-10 top-1/2 h-px bg-emerald-900/20" /><div className="absolute left-1/2 top-14 h-[290px] w-px bg-emerald-900/20" /><div className="absolute left-[18%] top-[37%] h-3 w-3 rounded-full border-2 border-emerald-800 bg-[#f5f7f5]" /><div className="absolute right-[18%] top-[62%] h-3 w-3 rounded-full border-2 border-signal bg-[#f5f7f5]" /><div className="absolute left-1/2 top-1/2 flex h-28 w-28 -translate-x-1/2 -translate-y-1/2 flex-col items-center justify-center rounded-full border border-emerald-900/20 bg-white/65 text-center shadow-soft"><Microscope className="text-emerald-800" size={23} /><span className="mt-2 font-mono text-[9px] uppercase tracking-[0.14em] text-slate-500">Agent loop</span></div><div className="absolute left-0 top-[30%] font-mono text-[10px] uppercase tracking-[0.18em] text-emerald-900/50">raw signal</div><div className="absolute right-0 bottom-[28%] font-mono text-[10px] uppercase tracking-[0.18em] text-signal/70">next move</div><div className="absolute bottom-0 left-1/2 flex -translate-x-1/2 items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-slate-400"><span className="h-8 w-px bg-slate-300" />Scroll to begin</div></div></Reveal>
            </div>
          </div>
        </section>

        <section id="experiments" className="scroll-mt-20 border-t border-slate-200/80 bg-white/35 py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-10"><Reveal className="max-w-3xl"><p className="eyebrow text-signal">01 / Dataset input</p><h2 className="editorial-heading mt-4 text-4xl font-extrabold tracking-[-0.06em] text-ink sm:text-6xl">Start with<br /><span className="text-emerald-800">your dataset.</span></h2><p className="mt-6 max-w-xl text-sm leading-7 text-slate-500 sm:text-base">Give the agent a clean target and a question worth testing. It will analyze the shape of the data, build a plan, and keep the evidence in view.</p></Reveal><div className="mt-14 grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-stretch"><Reveal className="panel p-5 sm:p-8"><div className="mb-7 flex items-start justify-between gap-4"><div><p className="eyebrow">Experiment configuration</p><h3 className="mt-2 text-xl font-extrabold tracking-[-0.04em] text-ink">Define the research question</h3></div><span className="rounded-lg bg-slate-100 px-2.5 py-1.5 font-mono text-[10px] text-slate-500">SETUP</span></div><form onSubmit={handleSubmit} className="space-y-5"><div><label className="field-label" htmlFor="dataset-upload">Dataset</label><div role="button" tabIndex={0} onClick={() => fileInput.current?.click()} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") fileInput.current?.click(); }} onDragOver={(event) => { event.preventDefault(); setDragActive(true); }} onDragLeave={() => setDragActive(false)} onDrop={handleDrop} className={`group cursor-pointer rounded-xl border border-dashed p-5 transition ${dragActive ? "border-emerald-500 bg-emerald-50" : file ? "border-emerald-200 bg-emerald-50/45" : "border-slate-300 bg-slate-50/65 hover:border-slate-400 hover:bg-slate-50"}`}><input ref={fileInput} id="dataset-upload" type="file" accept=".csv,text/csv" className="sr-only" onChange={handleFileChange} />{file ? <div className="flex items-center gap-3"><div className="rounded-lg bg-white p-2.5 text-emerald-700 shadow-sm"><FileText size={19} /></div><div className="min-w-0 flex-1"><p className="truncate text-sm font-bold text-ink">{file.name}</p><p className="mt-1 font-mono text-[11px] text-slate-500">{(file.size / 1024).toFixed(1)} KB · CSV dataset</p></div><button type="button" aria-label="Remove selected file" onClick={(event) => { event.stopPropagation(); clearFile(); }} className="rounded-lg p-2 text-slate-400 transition hover:bg-white hover:text-signal"><X size={17} /></button></div> : <div className="flex items-center gap-4"><div className="rounded-lg bg-white p-2.5 text-slate-500 shadow-sm transition group-hover:text-emerald-700"><UploadCloud size={20} /></div><div><p className="text-sm font-bold text-ink">Drop a CSV here or browse files</p><p className="mt-1 text-xs text-slate-500">Use a clean tabular dataset with a named target column.</p></div></div>}</div></div><div><label className="field-label" htmlFor="target-column">Target column</label><div className="relative"><Target className="pointer-events-none absolute left-3.5 top-3.5 text-slate-400" size={16} /><input id="target-column" value={targetColumn} onChange={(event) => setTargetColumn(event.target.value)} className="field-control pl-10" placeholder="e.g. target" /></div></div><div><label className="field-label" htmlFor="objective">Objective</label><textarea id="objective" value={objective} onChange={(event) => setObjective(event.target.value)} className="field-control min-h-[132px] resize-y leading-6" placeholder="Describe what you want the system to optimize..." /></div><div><div className="flex items-center justify-between"><label className="field-label mb-0" htmlFor="max-experiments">Maximum experiments</label><span className="font-mono text-xs text-slate-400">1–10</span></div><div className="mt-2 flex items-center gap-3"><input id="max-experiments" type="number" min={1} max={10} value={maxExperiments} onChange={(event) => setMaxExperiments(Number(event.target.value))} className="field-control max-w-[120px] text-center font-bold" /><span className="text-xs text-slate-500">iterations in this run</span></div></div>{(formError || runMutation.isError) && <div role="alert" className="flex items-start gap-2 rounded-xl border border-orange-200 bg-orange-50 px-3.5 py-3 text-sm leading-5 text-orange-800"><CircleAlert className="mt-0.5 shrink-0" size={16} />{formError || responseError(runMutation.error)}</div>}<button type="submit" disabled={runMutation.isPending} className="flex w-full items-center justify-center gap-2 rounded-xl bg-ink px-4 py-3.5 text-sm font-extrabold text-white shadow-lg shadow-ink/10 transition hover:-translate-y-0.5 hover:bg-slate-700 focus:outline-none focus:ring-4 focus:ring-ink/15 disabled:cursor-wait disabled:opacity-70">{runMutation.isPending ? <><Loader2 className="animate-spin" size={17} />Running research loop…</> : <><Zap size={17} />Run experiments <ArrowUpRight size={16} /></>}</button><p className="flex items-start gap-2 text-xs leading-5 text-slate-500"><Info className="mt-0.5 shrink-0 text-emerald-700" size={14} />The agent will analyze the dataset, run experiments, evaluate results, and use previous outcomes to select subsequent experiments.</p></form></Reveal><Reveal delay={0.1}><DataFlowVisual /></Reveal></div></div>
        </section>

        <section className="relative overflow-hidden border-b border-slate-200/80 bg-ink py-24 text-white sm:py-32"><div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-10"><Reveal><p className="eyebrow text-emerald-300">The point is not the first model</p><p className="editorial-heading max-w-5xl text-5xl font-extrabold leading-[0.95] tracking-[-0.07em] text-[#f4f3ea] sm:text-7xl">It doesn’t just run models.<br /><span className="text-emerald-300">It learns what to try next.</span></p></Reveal></div></section>

        <WorkflowStory />

        <section id="report" className="scroll-mt-20 py-24 sm:py-32"><div className="mx-auto max-w-7xl px-5 sm:px-8 lg:px-10"><Reveal className="max-w-4xl"><p className="eyebrow text-signal">05 / Research report</p><h2 className="editorial-heading mt-4 text-4xl font-extrabold tracking-[-0.06em] text-ink sm:text-6xl">Every experiment<br /><span className="text-emerald-800">becomes evidence.</span></h2><p className="mt-6 max-w-xl text-sm leading-7 text-slate-500 sm:text-base">Run the first loop to see the dataset profile, decisions, metrics, and final conclusion collected in one research readout.</p><button type="button" onClick={() => scrollTo("experiments")} className="mt-8 flex items-center gap-2 rounded-full border border-ink/20 bg-white px-4 py-3 text-sm font-extrabold text-ink transition hover:-translate-y-0.5 hover:border-ink/40">Start the research loop <ArrowUpRight size={16} /></button></Reveal></div></section>
      </main>
      <LandingFooter />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/results/:runId" element={<ResultsPage />} />
        <Route path="*" element={<LandingPage />} />
      </Routes>
    </ThemeProvider>
  );
}
