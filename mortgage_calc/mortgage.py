from dataclasses import dataclass
from enum import Enum

import numpy as np

CLOSING_COST_RATIO = 0.0284
PERCENT_CONVERT = 100
MIN_PERCENT = 0
MAX_PERCENT = 100
MONTHS_YEAR = 12
PMI_EQUITY_STOP = 0.2


class MortgageFields(Enum):
    """Attributes to Mortgage Object subject to change."""

    TAXES = "annual_taxes"
    INTEREST = "percent_interest"
    COST = "house_cost"
    DOWN_PAY = "percent_down"


@dataclass
class mortgageObject:
    """Object that defines parameters of mortgage.

    Attributes:
        house_cost (float): Total cost of house in dollars
        percent_down (float): Total percent down paid from 0 to 100
        annual_takes (float): Total taxes for the year.
        percent_interest (float): APY interest yearly rate on loan.
        percent_pmi (float): Percent PMI for loan.
        annual_homeowner_cost (float): Cost for homeowner ins per year.
        bill_cost_per_mo (flaot): Cost for bills per month.
    """

    house_cost: float
    percent_down: float
    annual_taxes: float
    percent_interest: float
    total_months: int
    percent_pmi: float
    annual_homeowner_cost: float
    bill_cost_per_mo: float

    def __post_init__(self) -> None:
        """Make sure percentages in valid range."""
        if self.percent_down < MIN_PERCENT or self.percent_down > MAX_PERCENT:
            raise ValueError("Not a valid percent down!")

        if self.percent_interest < MIN_PERCENT or self.percent_interest > MAX_PERCENT:
            raise ValueError("Not a valid percent interest!")

    def __repr__(self) -> str:
        """Print version of mortgage object with all calculations."""
        return f"Mortgage Breakdown:\
                \n\nHouse Cost: ${self.house_cost:.2f}\
                \nPercent Down: {self.percent_down:.2f}%\
                \nAnnual Taxes: ${self.annual_taxes:.2f}\
                \nPercent Interest APY {self.percent_interest:.2f}%\
                \nHomeowner Ins: ${self.annual_homeowner_cost:.2f} / year\
                \nBills: ${self.bill_cost_per_mo:.2f} / mo\
                \n\nDown Payment: ${self.down_payment:.2f}\
                \nClosing Costs: ${self.closing_cost:.2f}\
                \nMonth % Interest {self.month_interest_rate * PERCENT_CONVERT:.2f}% / mo\
                \nMonthly P/I Cost: ${self.monthly_mortgage:.2f} / mo\
                \nMonthly PMI Cost: ${self.monthly_pmi_cost:.2f} / mo\
                \nMonthly Tax Cost: ${self.monthly_tax_cost:.2f} / mo\
                \nMonthly Home Ins Cost: ${self.monthly_homeowner_cost:.2f} / mo\
                \n\nMonthly Total Cost: ${self.monthly_total_cost:.2f} / mo\
                \nMonthly Total Cost minus PMI: ${self.monthly_total_cost_minus_pmi:.2f} / mo\
                \n\nTotal Upfront Costs: ${self.upfront_cost:.2f}\
                \nMortgage Amount: ${self.mortgage_amount:.2f}\
                \nMonths of PMI: {self.pmi_months} months\
                \nLifetime Total PMI cost: ${self.total_pmi_cost:.2f}\
                \nLifetime P/I Mortgage Cost: ${self.lifetime_mortgage:.2f}\
                \nLifetime Total Mortgage Cost: ${self.lifetime_cost:.2f}\n"

    @property
    def closing_cost(self) -> float:
        """Closing cost calculate.

        Returns:
            float: Closing cost or CLOSING_COST_RATIO % of house cost.

        """
        return CLOSING_COST_RATIO * self.house_cost

    @property
    def down_payment(self) -> float:
        """Down payment calculate.

        Returns:
            float: Down payment of house cost * percent down
        """
        return self.house_cost * self.percent_down / PERCENT_CONVERT

    @property
    def upfront_cost(self) -> float:
        """Upfront cost calculate.

        Returns:
            float: Upfront cost of closing cost and down payment.
        """
        return self.closing_cost + self.down_payment

    @property
    def mortgage_amount(self) -> float:
        """Mortgage amount calculate.

        Returns:
            float: Mortgage amount of house cost excluding down payment.
        """
        return self.house_cost - self.down_payment

    @property
    def month_interest_rate(self) -> float:
        """Monthly interest rate calculate.

        Returns:
            float: Monthly intetest rate of APR from 0 to 1
        """
        return (self.percent_interest / PERCENT_CONVERT) / MONTHS_YEAR

    @property
    def pmi_months(self) -> int:
        """Calculate number of month of PMI or mortgage insurance.

        First calc compound interest term of  (1 + month_interest) ^ total_months.
        PMI sotop after PMI_EQUITY_STOP % of principal achieved
        Then months of PMI is log(cmpd_i - (1-PMI_EQUIY_STOP) * (cmpd_i - 1) * (house cost/ mortgage amount)) / log(1+month_interest)

        Returns:
            int: Months of PMI
        """
        term = (1.0 + self.month_interest_rate) ** self.total_months
        return int(
            np.ceil(
                np.log(
                    term
                    - (1 - PMI_EQUITY_STOP)
                    * (term - 1.0)
                    * (self.house_cost / self.mortgage_amount)
                )
                / np.log(1.0 + self.month_interest_rate)
            )
        )

    @property
    def monthly_mortgage(self) -> float:
        """Calculate monthly mortgage payment.

        Payment is mortgage_amount * monthly_intest * (1+monthly_interest) ^ months / (1 + mothly_interest) ^ (months - 1)

        Returns:
            float: Monthly mortgage payment for principal/interest
        """
        return (
            self.mortgage_amount
            * (
                self.month_interest_rate
                * (1.0 + self.month_interest_rate) ** self.total_months
            )
            / ((1.0 + self.month_interest_rate) ** self.total_months - 1)
        )

    @property
    def total_pmi_cost(self) -> float:
        """PMI cost is mortgage * percent PMI.

        Returns:
            float: PMI cost total.
        """
        return (
            self.mortgage_amount
            * self.percent_pmi
            * self.pmi_months
            / PERCENT_CONVERT
            / MONTHS_YEAR
        )

    @property
    def monthly_pmi_cost(self) -> float:
        """PMI cost monthly is total PMI cost divided by month with PMI.

        Returns:
            float: Monthly PMI cost
        """
        if self.pmi_months == 0:
            return 0.0
        return self.total_pmi_cost / self.pmi_months

    @property
    def monthly_tax_cost(self) -> float:
        """Monthly cost of taxes.

        Returns:
            float: Taxes per month average.
        """
        return self.annual_taxes / MONTHS_YEAR

    @property
    def monthly_homeowner_cost(self) -> float:
        """Monthly average cost of homeowners insurance.

        Returns:
            float: Homeowner ins per month average.
        """
        return self.annual_homeowner_cost / MONTHS_YEAR

    @property
    def monthly_total_cost(self) -> float:
        """Total monthly cost of monthly cost for P/I mortgage, PMI, taxes, homeowner ins, and bills.

        Returns:
            float: Total monthly cost of mortgage.
        """
        return (
            self.monthly_mortgage
            + self.monthly_pmi_cost
            + self.monthly_tax_cost
            + self.monthly_homeowner_cost
            + self.bill_cost_per_mo
        )

    @property
    def monthly_total_cost_minus_pmi(self) -> float:
        """Monthly cost of everything besides PMI for when PMI ends.

        Returns:
            float: Total monthyl cost minus PMI.
        """
        return self.monthly_total_cost - self.monthly_pmi_cost

    @property
    def lifetime_mortgage(self) -> float:
        """Liftetime mortgage cost is (monthly mortage + PMI) * PMI months + monthly mortgage * (total months - PMI months)

        Returns:
            float: Total lifetme mortgage cost.
        """
        return (
            (self.monthly_mortgage + self.monthly_pmi_cost) * self.pmi_months
            + self.monthly_mortgage * (self.total_months - self.pmi_months)
            + self.down_payment
        )

    @property
    def lifetime_cost(self) -> float:
        """Lifetime total cost which is total month * PMI months + (total month - PMI) * non PMI months + upfront.

        Returns:
            float: Total lifetime mortgage plus other costs.
        """
        return (
            self.monthly_total_cost * self.pmi_months
            + self.monthly_total_cost_minus_pmi * (self.total_months - self.pmi_months)
            + self.upfront_cost
        )
