"""Dataset specifications for evaluation."""

from typing import Any
import pandas as pd
from sklearn.datasets import load_breast_cancer, load_iris, load_wine


def get_evaluation_datasets() -> dict[str, dict[str, Any]]:
    """Return standard small classification datasets."""
    datasets = {}
    
    # Iris
    iris = load_iris()
    df_iris = pd.DataFrame(iris.data, columns=iris.feature_names)
    df_iris['target'] = iris.target
    datasets['iris'] = {
        'data': df_iris,
        'target_column': 'target',
        'objective': 'Classify iris species and maximize validation accuracy.'
    }
    
    # Breast Cancer
    cancer = load_breast_cancer()
    df_cancer = pd.DataFrame(cancer.data, columns=cancer.feature_names)
    df_cancer['target'] = cancer.target
    datasets['breast_cancer'] = {
        'data': df_cancer,
        'target_column': 'target',
        'objective': 'Classify breast cancer as malignant or benign.'
    }
    
    # Wine
    wine = load_wine()
    df_wine = pd.DataFrame(wine.data, columns=wine.feature_names)
    df_wine['target'] = wine.target
    datasets['wine'] = {
        'data': df_wine,
        'target_column': 'target',
        'objective': 'Classify wine into three different cultivars.'
    }
    
    return datasets
