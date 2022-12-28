from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt  # type: ignore

from mortgage_calc.analysis import AnalysisFields
from mortgage_calc.io import load_analysis_object, load_mortgage_object
from mortgage_calc.mortgage import MortgageFields, mortgageObject
from mortgage_calc.plotting import plot_variable_params
from mortgage_calc.utils import get_param_sweep, percent_increase, variable_param


def main() -> None:
    """Create analysis and mortgage objects from yaml and print out total mortgage calculations.

    Then using analysis object parameter sweeps and percent changes, calculate percent change in input params for change inoutput param.
    """
    CONFIG_PATH = Path(__file__).parent / "data" / "mortgage.yaml"
    analysis_obj = load_analysis_object(CONFIG_PATH)
    mortgage_obj = load_mortgage_object(CONFIG_PATH)
    field_mapping: Dict[MortgageFields, AnalysisFields] = {
        MortgageFields.COST: AnalysisFields.COST,
        MortgageFields.DOWN_PAY: AnalysisFields.DOWN_PAY,
        MortgageFields.INTEREST: AnalysisFields.INTEREST,
        MortgageFields.TAXES: AnalysisFields.TAXES,
    }
    _, axs = plt.subplots(len(field_mapping), 1)
    print(mortgage_obj)

    for ax, (mort_param, analysis_param) in zip(axs, field_mapping.items()):
        # Get parameter sweep of input variable and output results
        mortgage_obj_copy = mortgageObject(**mortgage_obj.__dict__)
        param_sweep = get_param_sweep(
            mortgage_obj=mortgage_obj_copy,
            input_param=mort_param,
            analysis_param=analysis_param,
            analysis_obj=analysis_obj,
        )
        vals = variable_param(
            input_param=mort_param,
            output_param=analysis_obj.survey_param,
            mortgage_obj=mortgage_obj_copy,
            param_sweep=param_sweep,
        )

        # Get delta of output impact by input change
        delta = percent_increase(
            percent_increase=analysis_obj.percent_increase,
            output_vals=vals,
            input_param_sweep=param_sweep,
        )
        output_increase = analysis_obj.percent_increase / 100.0 * vals[0]
        total_input_change = delta * analysis_obj.survey_change / output_increase
        print(
            f"A {analysis_obj.percent_increase}% increase or {output_increase:.2f} in {analysis_obj.survey_param} corresponds to increase in {mort_param.value} by {delta:.2f}"
        )
        print(
            f"An increase in {analysis_obj.survey_param} by ${analysis_obj.survey_change:.2f} corresponds to a change in {mort_param.value} by {total_input_change:.2f}\n"
        )

        # Plot trends
        plot_variable_params(
            input_param=mort_param,
            output_param=analysis_obj.survey_param,
            output_vals=vals,
            input_param_sweep=param_sweep,
            ax=ax,
            use_absolute=analysis_obj.plot_absolute,
        )
        ax.legend()

    plt.show()


if __name__ == "__main__":
    main()
