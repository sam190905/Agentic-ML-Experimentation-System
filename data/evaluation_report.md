# Agentic ML Experimentation Benchmark

## Experimental Setup

Datasets:
- Iris
- Breast_cancer
- Wine

Strategies:
- Baseline
- Gemini Agent

Search space:
9 controlled configurations

Metric:
Accuracy

Validation:
5-fold stratified cross-validation

## Results

| Dataset | Strategy | After 1 | After 2 | After 3 | Final | Best Model | Improvement |
|---------|----------|---------|---------|---------|-------|------------|-------------|
| Iris | Baseline | 0.9533 | 0.9533 | 0.9533 | 0.9533 | gradient_boosting | +0.0000 |
| Iris | Agent | 0.9467 | 0.9533 | 0.9733 | 0.9733 | logistic_regression | +0.0267 |
| Breast_cancer | Baseline | 0.9737 | 0.9737 | 0.9737 | 0.9737 | logistic_regression | +0.0000 |
| Breast_cancer | Agent | 0.9561 | 0.9561 | 0.9737 | 0.9737 | logistic_regression | +0.0176 |
| Wine | Baseline | 0.9833 | 0.9833 | 0.9833 | 0.9833 | logistic_regression | +0.0000 |
| Wine | Agent | 0.9775 | 0.9775 | 0.9833 | 0.9833 | logistic_regression | +0.0059 |

## Agent Trace

### Iris

**Experiment 1**
- **Config ID:** rf-default
- **Model:** random_forest
- **Score:** 0.9467
- **Best So Far:** 0.9467
- **Planning Reason:** Random Forest default is a strong non-linear baseline for multi-class tabular classification with balanced classes and small sample size.

**Experiment 2**
- **Config ID:** lr-default
- **Model:** logistic_regression
- **Score:** 0.9533
- **Best So Far:** 0.9533
- **Planning Reason:** Test a standard logistic regression baseline on this small, low-dimensional dataset, where linear decision boundaries often achieve very high accuracy compared to tree-based ensembles.

**Experiment 3**
- **Config ID:** lr-weak-reg
- **Model:** logistic_regression
- **Score:** 0.9733
- **Best So Far:** 0.9733
- **Planning Reason:** Logistic regression yielded the highest validation accuracy so far (0.9533). Evaluating lr-weak-reg with weaker regularization (C=10.0) tests whether reducing regularization constraint improves performance on the Iris dataset.

### Breast_cancer

**Experiment 1**
- **Config ID:** rf-default
- **Model:** random_forest
- **Score:** 0.9561
- **Best So Far:** 0.9561
- **Planning Reason:** Starting with a default Random Forest provides a strong non-linear baseline well-suited for tabular numerical features with varying scales, without requiring prior feature normalization.

**Experiment 2**
- **Config ID:** gb-default
- **Model:** gradient_boosting
- **Score:** 0.9491
- **Best So Far:** 0.9561
- **Planning Reason:** Gradient boosting explores an alternate ensemble strategy (sequential boosting rather than bagging) that frequently achieves higher classification accuracy on small-to-medium tabular datasets.

**Experiment 3**
- **Config ID:** lr-default
- **Model:** logistic_regression
- **Score:** 0.9737
- **Best So Far:** 0.9737
- **Planning Reason:** Evaluating a linear model (Logistic Regression) introduces a distinct hypothesis class from tree-based ensembles, which is often highly competitive and interpretable on this small, feature-rich continuous dataset.

### Wine

**Experiment 1**
- **Config ID:** rf-default
- **Model:** random_forest
- **Score:** 0.9775
- **Best So Far:** 0.9775
- **Planning Reason:** Starting with a robust Random Forest baseline with default settings, which performs well on small continuous tabular classification datasets without requiring feature scaling.

**Experiment 2**
- **Config ID:** gb-default
- **Model:** gradient_boosting
- **Score:** 0.9271
- **Best So Far:** 0.9775
- **Planning Reason:** Previous experiment evaluated a baseline Random Forest with strong performance (accuracy ~0.977). Evaluating Gradient Boosting introduces an alternative boosting ensemble family on this small tabular multiclass dataset to see if sequential error correction yields higher predictive accuracy.

**Experiment 3**
- **Config ID:** lr-default
- **Model:** logistic_regression
- **Score:** 0.9833
- **Best So Far:** 0.9833
- **Planning Reason:** Previous experiments tested tree-based models (Random Forest and Gradient Boosting), with Random Forest performing very well (97.7% accuracy). The Wine dataset consists entirely of continuous numerical features and is often highly linearly separable. Testing logistic regression with standard L2 regularization establishes a linear baseline and checks whether a simpler, highly interpretable linear model can match or exceed tree ensemble performance.

## Comparison

### Iris

- **Final Score Difference:** +0.0200
- **Experiments to Reach Baseline Best:** 3

- **Failures:** None

### Breast_cancer

- **Final Score Difference:** +0.0000
- **Experiments to Reach Baseline Best:** 3

- **Failures:** None

### Wine

- **Final Score Difference:** +0.0000
- **Experiments to Reach Baseline Best:** 3

- **Failures:** None

## Interpretation

**Iris:**
Agent achieved a higher best score than the baseline.

**Breast_cancer:**
Agent took more experiments to reach the same best score.

**Wine:**
Agent took more experiments to reach the same best score.

## Limitations

- dataset size
- limited configuration space
- classification-only scope
- LLM provider availability
- benchmark does not prove general intelligence
