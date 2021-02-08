from setuptools import setup


setup(
    # Application name:
    name="VS_Classification",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Carlos Quezada",
    author_email="ciquezada@uc.cl",

    # Packages
    packages=[],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="",#"http://pypi.python.org/pypi/MyApplication_v010/",

    #
    # license="LICENSE.txt",
    description="For variable stars classification.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "feets",
        "scikit-learn",
        "sympy",
        "pybind11",
        "emcee",
        "statsmodels",
        "astropy",
        "symfit",
        "pandas",
        "scipy",
        "numpy",
    ],
)
