from dataclasses import dataclass
from enum import Enum


class AnalysisFields(Enum):
    """Corresponding attributes to Analysis Object subject to change."""

    TAXES = "taxes_change"
    INTEREST = "percent_interest_change"
    COST = "house_cost_change"
    DOWN_PAY = "percent_down_change"


@dataclass
class analysisObject:
    """Object with analysis attributes.

    Attributes:
        survey_param (str): Parameter in mortageObject that is tested based on change in other parameters.
        survey_change (float): Amount to change survey_param by to calculate changes in other input params.
        num_values (int): Number of values to sweep over between initial value and max change.
        percent_increase (float): Percent increase in survey param to calculate changes in other input params.
        plot_absolute (bool): If True plots include absolute values, else plot by percent change.
        house_cost_change (float): Amount to vary house cost by from base to see deviation of survey_param
        percent_down_change (float):
        percent_interest_change (float):
        taxes_change (float):
    """

    survey_param: str
    survey_change: float
    num_values: int
    percent_increase: float
    plot_absolute: bool
    house_cost_change: float
    percent_down_change: float
    percent_interest_change: float
    taxes_change: float
