"""
Setup configuration for backward compatibility.

This file is kept for backward compatibility with setuptools.
The build system configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="camera-calibration",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
)
