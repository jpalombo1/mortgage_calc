from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import yaml

CLOSING_COST_RATIO = 0.04


@dataclass
class analysisObject:
    survey_param: str
    survey_change: float
    num_values: int
    percent_increase: float
    plot_absolute: bool
    house_cost_change: float
    percent_down_change: float
    percent_interest_change: float
    taxes_change: float


@dataclass
class calculateObject:
    input: str
    output: str
    input_change: float
    output_change: float

    def total_input_change(self, output_amount: float) -> float:
        """_summary_

        Args:
            output_amount (float): _description_

        Returns:
            float: _description_
        """
        return self.input_change * output_amount / self.output_change


@dataclass
class mortgageObject:
    house_cost: float
    percent_down: float
    annual_taxes: float
    percent_interest: float
    total_months: int
    percent_pmi: float
    annual_homeowner_cost: float
    bill_cost_per_mo: float

    @property
    def closing_cost(self) -> float:
        return 0.04 * self.house_cost

    @property
    def down_payment(self) -> float:
        return self.house_cost * self.percent_down / 100.0

    @property
    def upfront_cost(self) -> float:
        return self.closing_cost + self.down_payment

    @property
    def mortgage_amount(self) -> float:
        return self.house_cost - self.down_payment

    @property
    def month_interest_rate(self) -> float:
        return (self.percent_interest / 100.0) / 12.0

    @property
    def pmi_months(self) -> int:
        term = (1.0 + self.month_interest_rate) ** self.total_months
        return int(
            np.ceil(
                np.log(
                    term - 0.8 * (term - 1.0) * self.house_cost / self.mortgage_amount
                )
                / np.log(1.0 + self.month_interest_rate)
            )
        )

    @property
    def monthly_mortgage(self) -> float:
        return (
            self.mortgage_amount
            * (
                self.month_interest_rate
                * (1.0 + self.month_interest_rate) ** self.total_months
            )
            / ((1.0 + self.month_interest_rate) ** self.total_months - 1)
        )

    @property
    def monthly_pmi_cost(self) -> float:
        return self.mortgage_amount * self.percent_pmi / 12.0 / 100.0

    @property
    def total_pmi_cost(self) -> float:
        return self.monthly_pmi_cost * self.pmi_months

    @property
    def monthly_tax_cost(self) -> float:
        return self.annual_taxes / 12.0

    @property
    def monthly_homeowner_cost(self) -> float:
        return self.annual_homeowner_cost / 12.0

    @property
    def monthly_total_cost(self) -> float:
        return (
            self.monthly_mortgage
            + self.monthly_pmi_cost
            + self.monthly_tax_cost
            + self.monthly_homeowner_cost
            + self.bill_cost_per_mo
        )

    @property
    def monthly_total_cost_minus_pmi(self) -> float:
        return (
            self.monthly_mortgage
            + self.monthly_tax_cost
            + self.monthly_homeowner_cost
            + self.bill_cost_per_mo
        )

    @property
    def lifetime_mortgage(self) -> float:
        return (
            (self.monthly_mortgage + self.monthly_pmi_cost) * self.pmi_months
            + self.monthly_mortgage * (self.total_months - self.pmi_months)
            + self.down_payment
        )

    @property
    def lifetime_cost(self) -> float:
        return (
            self.monthly_total_cost * self.pmi_months
            + self.monthly_total_cost_minus_pmi * (self.total_months - self.pmi_months)
            + self.upfront_cost
        )


def variable_param(
    input_param: str, output_param: str, obj: mortgageObject, param_sweep: list[float]
) -> np.ndarray:
    vals = []
    for param_val in param_sweep:
        obj_new = mortgageObject(**obj.__dict__)
        obj_new.__dict__[input_param] = param_val
        vals.append(getattr(obj_new, output_param))
    return np.array(vals)


def percent_increase(
    percent_increase: float,
    input_param: str,
    output_param: str,
    vals: np.ndarray,
    param_sweep: np.ndarray,
) -> tuple[float, float]:
    percent_change = (vals - vals[0]) / vals[0] * 100
    percent_idx = 0
    for idx, val in enumerate(percent_change):  # type: ignore
        if np.abs(val) > percent_increase:
            percent_idx = idx
            break
    delta_param = param_sweep - param_sweep[0]
    delta = delta_param[percent_idx] * percent_increase / percent_change[percent_idx]
    output_increase = percent_increase / 100.0 * vals[0]
    print(
        f" A {percent_increase} % increase or {output_increase:.2f} in {output_param} corresponds to increase in {input_param} by {delta:.2f}"
    )
    return (delta, output_increase)


def plot_variable_params(
    input_param: str,
    output_param: str,
    vals: np.ndarray,
    param_sweep: np.ndarray,
    ax: Any,
    use_absolute: bool = False,
):
    if use_absolute:
        use_vals = vals
        use_param = param_sweep
        ax.set_ylabel(output_param)
        ax.set_xlabel("Values")
    else:
        use_vals = (vals - vals[0]) / vals[0] * 100
        use_param = param_sweep - param_sweep[0]
        ax.set_ylabel("% Change")
        ax.set_xlabel(f"Diff from Base val = {param_sweep[0]}")
    return ax.plot(use_param, use_vals, label=input_param)


def main():
    config_path = "data/mortgage.yaml"

    with open(config_path, "r") as yfile:
        config_dict = yaml.safe_load(yfile)
    analysis_obj = analysisObject(**config_dict["analysis"])

    param_change_dict = {
        "annual_taxes": "taxes_change",
        "percent_interest": "percent_interest_change",
        "house_cost": "house_cost_change",
        "percent_down": "percent_down_change",
    }
    _, axs = plt.subplots(len(param_change_dict), 1)
    calcObjs: list[calculateObject] = []
    for ax, (init_param, change_param) in zip(axs, param_change_dict.items()):
        # Get parameter sweep of input variable and output results
        mort_obj = mortgageObject(**config_dict["object"])
        param_sweep = np.linspace(
            getattr(mort_obj, init_param),
            getattr(mort_obj, init_param) + getattr(analysis_obj, change_param),
            analysis_obj.num_values,
        )
        vals = variable_param(
            init_param, analysis_obj.survey_param, mort_obj, param_sweep
        )

        # Get delta of output impact by input change
        delta_in, output_increase = percent_increase(
            analysis_obj.percent_increase,
            init_param,
            analysis_obj.survey_param,
            vals,
            param_sweep,
        )
        calcObjs.append(
            calculateObject(
                init_param, analysis_obj.survey_param, delta_in, output_increase
            )
        )

        # Plot trends
        plot_variable_params(
            init_param,
            analysis_obj.survey_param,
            vals,
            param_sweep,
            ax,
            use_absolute=analysis_obj.plot_absolute,
        )
        ax.legend()

    print_arr = [
        f"An increase in {cobj.output} by ${analysis_obj.survey_change:.2f} corresponds to a change in {cobj.input} by {cobj.total_input_change(analysis_obj.survey_change):.2f}"
        for cobj in calcObjs
    ]
    print("\n".join(print_arr))

    plt.show()


if __name__ == "__main__":
    main()
