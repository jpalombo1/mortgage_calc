import numpy as np
from numpy.typing import NDArray

from mortgage_calc.analysis import AnalysisFields, analysisObject
from mortgage_calc.mortgage import MortgageFields, mortgageObject


def get_param_sweep(
    mortgage_obj: mortgageObject,
    input_param: MortgageFields,
    analysis_obj: analysisObject,
    analysis_param: AnalysisFields,
) -> NDArray[np.float_]:
    """Performs parameter sweep of mortgageObject's mortgageField based on analysisObject analysisField and number of values.

    Args:
        mortgage_obj (mortgageObject): Mortgage Object to modify input parameter for.
        input_param (MortgageFields): MortgageFIeld Input parmeter field to change in object.
        analysis_obj (analysisObject): Analysis object to get AnalysisField to modify by.
        analysis_param (AnalysisFields): AnalysisField input parameter to add to mortgage field parameter.

    Returns:
        NDArray[np.float_]: List of sweep values for given MortgageField parameter changed by AnalysisFIeld parameter.
    """
    return np.linspace(
        getattr(mortgage_obj, input_param.value),
        getattr(mortgage_obj, input_param.value)
        + getattr(analysis_obj, analysis_param.value),
        analysis_obj.num_values,
    )


def variable_param(
    input_param: MortgageFields,
    output_param: str,
    mortgage_obj: mortgageObject,
    param_sweep: NDArray[np.float_],
) -> NDArray[np.float_]:
    """Get output param values based on changing input param in param_sweep.

    Args:
        input_param (MortgageFields): mortgageField or mortgageObject param to change.
        output_param (str): String of attribute for analysisObject param.
        obj (mortgageObject): Mortgage object for initialization.
        param_sweep (list[float]): List of sweep values for given input parameter

    Returns:
        np.ndarray: List of values for output param given changed input param for parameter sweep.
    """
    vals = []
    for param_val in param_sweep:
        obj_new = mortgageObject(**mortgage_obj.__dict__)
        obj_new.__dict__[input_param.value] = param_val
        vals.append(getattr(obj_new, output_param))
    return np.array(vals)


def percent_increase(
    percent_increase: float,
    output_vals: np.ndarray,
    input_param_sweep: NDArray[np.float_],
) -> float:
    """Using parameter sweep and output values to single percent increase.

    Get percent changes of output param targeting by getting % difference from first val,
    then get percent_idx closest to target % increase, then interpolate percent_increase from index to target %,
    including change in delta param and interpolating

    e.g. vals = [10,11,12,13] , param_sweep = [5,10,15,20], delta_param= [0,5,10,15] percent_change = [0% ,10%, 20%, 30%]
    percent-incease = 25%, percent_idx = 3 (since val % > 25% at idx 3 or 30%)
    delta = delta_param[3] * percent_increase / percent_change[3] = 15 * 25/30 = 12.5

    Args:
        percent_increase (float): Percent increase to get values for.
        output_vals (np.ndarray): List of values for output param given changed input param for parameter sweep.
        input_param_sweep (np.ndarray): List of sweep values for given input parameter.

    Returns:
        float: Delta of input parameter that yields percent increase of corresponding output parameter.
    """
    percent_change = (output_vals - output_vals[0]) / output_vals[0] * 100
    delta_param = input_param_sweep - input_param_sweep[0]
    percent_idx = 0
    for idx, val in enumerate(percent_change):
        if np.abs(val) > percent_increase:
            percent_idx = idx
            break
    return delta_param[percent_idx] * percent_increase / percent_change[percent_idx]
