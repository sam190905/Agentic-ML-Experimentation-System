import { useMutation } from "@tanstack/react-query";

import { runExperiment } from "../api/experiments";
import type { RunExperimentInput } from "../types";

export function useRunExperiment() {
  return useMutation({
    mutationFn: (input: RunExperimentInput) => runExperiment(input),
  });
}
