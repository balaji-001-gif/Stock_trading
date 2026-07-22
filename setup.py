from setuptools import setup, find_packages
from bizaxl import __version__

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="bizaxl",
    version=__version__,
    description="Investment & Wealth Platform — Mutual Funds, PMS, AIF, Hedge Funds, PE, VC, Bonds, Real Estate, Trading, Family Office, Pension, Advisor",
    author="bizaxl Optimisations LLP",
    author_email="dev@bizaxl.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.9",
)
