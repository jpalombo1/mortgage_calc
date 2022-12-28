from pathlib import Path

import yaml

from mortgage_calc.analysis import analysisObject
from mortgage_calc.mortgage import mortgageObject

ANALYSIS_KEY = "analysis"
MORTGAGE_KEY = "mortgage"


def load_analysis_object(config_path: Path) -> analysisObject:
    """Using yaml, create analysis object from keys/values in analysis section of config.

    Args:
        config_path (Path): Path to YAML file with config

    Returns:
        analysisObject: Analysis object
    """
    with open(config_path, "r") as yfile:
        config_dict = yaml.safe_load(yfile)
        return analysisObject(**config_dict[ANALYSIS_KEY])


def load_mortgage_object(config_path: Path) -> mortgageObject:
    """Using yaml, create mortgage object from keys/values in object section of config.

    Args:
        config_path (Path): Path to YAML file with config

    Returns:
        analysisObject: Analysis object
    """
    with open(config_path, "r") as yfile:
        config_dict = yaml.safe_load(yfile)
        return mortgageObject(**config_dict[MORTGAGE_KEY])
