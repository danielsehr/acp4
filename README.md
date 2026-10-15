# Setup

## 1. Navigate to a directory

Open a terminal and navigate to the directory where you want to store the repository:

```bash
cd /path/to/your/directory
```

## 2. Clone the repository

```bash
git clone https://github.com/danielsehr/acp4.git
cd ACP4-Seminar
```

## 3. Install dependencies

Make sure [uv](https://docs.astral.sh/uv/) is installed, then run:

```bash
uv sync
```

This creates a virtual environment (if needed) and installs the project dependencies specified in `pyproject.toml` and `uv.lock`.

To run Python commands within the environment, use:

```bash
uv run python your_script.py
```