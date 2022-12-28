from setuptools import setup  # type: ignore

setup(
    name="mortgage_calc",
    version="1.0",
    description="Mortgage Calculation and Analysis Package",
    author="Joseh Palombo",
    packages=["mortgage_calc"],
    setup_requires=["numpy", "types-PyYAML"],
)
