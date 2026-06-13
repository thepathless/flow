"""setuptools shim for flow.

All project metadata lives in pyproject.toml. The single job left for
setup.py is to install the extension-less `flow` script as a console program.
PEP 621's [project.scripts] can only point at importable entry-points, but
`flow` is a standalone script (no module to import), so we use the classic
`scripts=` mechanism here. On install, pip rewrites the shebang to the target
interpreter and, on Windows, generates a `flow.exe` launcher automatically.
"""

from setuptools import setup

setup(scripts=["flow"])
