from typing import Any

import numpy as np

from mortgage_calc.mortgage import MortgageFields


def plot_variable_params(
    input_param: MortgageFields,
    output_param: str,
    output_vals: np.ndarray,
    input_param_sweep: np.ndarray,
    ax: Any,
    use_absolute: bool = False,
) -> None:
    """Plot the variable params. Depending on absolute or not either use vals and input sweep or % changes and deltas.

    Args:
        input_param (MortgageFields): mortgageField or mortgageObject param to change.
        output_param (str): String of attribute for analysisObject param.
        output_vals (np.ndarray): List of values for output param given changed input param for parameter sweep.
        input_param_sweep (np.ndarray): List of sweep values for given input parameter.
        ax (Any): Axis to put plot on.
        use_absolute (bool, optional): Option to use absolute value on y axis or just % changes. Defaults to False.
    """
    if use_absolute:
        use_vals = output_vals
        use_param = input_param_sweep
        ax.set_ylabel(output_param)
        ax.set_xlabel("Values")
    else:
        use_vals = (output_vals - output_vals[0]) / output_vals[0] * 100
        use_param = input_param_sweep - input_param_sweep[0]
        ax.set_ylabel("% Change")
        ax.set_xlabel(f"Diff from Base val = {input_param_sweep[0]}")
    return ax.plot(use_param, use_vals, label=input_param.value)
