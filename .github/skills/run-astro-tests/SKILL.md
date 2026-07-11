---
name: run-astro-tests
description: Runs pytest for the astronomy package and specifically checks for Astropy unit/quantity warnings and WCS errors.
parameters:
  properties:
    target_dir:
      type: string
      description: The relative directory path containing the test files to run.
  required:
    - target_dir
---

# Action Intention

Execute the local testing framework to validate the astronomical physics logic, data schema constraints (such as FITS headers), and overall software stability.

# Execution Guidelines

When this skill is invoked by the Agent:

1. Ensure you activate the local Python virtual environment containing `astropy` and `pytest`.
2. Run the command: `python -m pytest {target_dir} --tb=short` in the terminal.
3. Capture the stdout/stderr. Pay special attention to warnings related to `astropy.units` and `astropy.wcs`.
4. Provide the test tracebacks and summary directly back to the active Agent session for further refactoring decisions.
