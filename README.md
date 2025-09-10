# Vijay AI CodeGen: Python Code Generator & Optimizer

An end-to-end project to generate, test, and optimize Python code for algorithms, data structures, and application boilerplates using the Euri AI Python SDK.

## Why this project
- Speed up building correct, well-tested Python code with AI assistance
- Focus on DSA (Data Structures & Algorithms) and extensible specs for new topics
- Enforce quality with tests, formatting, linting, typing, and benchmarks
- Provide a clean CLI and modular architecture you can extend

## What it does
- List available DSA topics with precise requirements
- Generate Python modules and unit tests via Euri AI
- Optimize/refactor code for readability, performance, and memory
- Explain generated code and reasoning
- Run tests and optional micro-benchmarks

## High-level architecture
- `src/euri_codegen/cli.py` – Typer CLI entrypoint
- `src/euri_codegen/config.py` – Config, env, model defaults
- `src/euri_codegen/euri_client.py` – Thin wrapper around Euri AI client
- `src/euri_codegen/codegen/generator.py` – LLM prompts and code generation
- `src/euri_codegen/codegen/optimizer.py` – LLM + tooling optimizations
- `src/euri_codegen/catalog/dsa_catalog.json` – Curated DSA specs
- `src/euri_codegen/prompts/` – Prompt templates (generation, optimization, explain)
- `generated/` – Output folder (modules, tests)

## Installation
1) Python 3.10+ recommended.
2) Create a virtual environment and install the package (editable) + deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

3) Configure your Euri API key securely. Prefer environment variables:

- PowerShell (current session):
```powershell
$env:EURI_API_KEY = "<your-key>"
```

- Or create a local `.env` file (not committed):
```
EURI_API_KEY=<your-key>
```

Optionally choose a default model via env:
```
EURI_MODEL=gpt-4.1-nano
```

## Quick start
List topics:
```powershell
python -m euri_codegen list-topics
```

Generate a topic implementation (module + tests):
```powershell
python -m euri_codegen generate --topic binary_search --out-dir generated
```

List all topics:
```powershell
python -m euri_codegen list-topics
```

Run tests:
```powershell
pytest -q
```

Optimize a file for performance and readability:
```powershell
python -m euri_codegen optimize --path generated/binary_search.py --level all
```

Explain a file:
```powershell
python -m euri_codegen explain --path generated/binary_search.py
```

## Streamlit app
Start the web UI:
```powershell
streamlit run app.py
```
Features in UI:
- Generate one or all topics (module + tests) to the `generated/` folder
- Optimize a Python file with code-fence sanitation
- Explain a Python file
- View and validate the DSA catalog
- Environment doctor panel

### Deploying to Streamlit Cloud
1) Push this repo to GitHub (already done).
2) In Streamlit Cloud, set Secrets with at least:
```
EURI_API_KEY = "your-euri-api-key"
EURI_MODEL = "gpt-4.1-nano"
```
3) Deploy with main module: `app.py`. The app reads the key from secrets or environment.
4) Note: The UI will not ask for API keys. Keys must be configured on the backend (secrets/env) so shared users can use the app without seeing or entering them.

## Notes on safety and keys
- Never commit your API key. Use environment variables or `.env` in local dev only.
- This project will not print your key. It reads from `EURI_API_KEY`.

## Extending the catalog
Add or edit specs in `src/euri_codegen/catalog/dsa_catalog.json`. Each spec includes:
- `id`, `title`, `summary`
- `function_signature`, `inputs`, `outputs`, `constraints`
- `examples`

## Why these choices
- Typer + Rich: ergonomic CLI & output
- Pydantic: robust config validation
- pytest + pytest-benchmark: correctness and perf checks
- black + ruff + mypy: readable, consistent, safe code
- Euri AI SDK: single integration point, easy model swaps

## How it's built
- Clean package layout under `src/` with explicit entry points and small modules
- Prompt templates centralized in `src/euri_codegen/prompts/templates.py`
- Catalog-driven generation using JSON specs in `src/euri_codegen/catalog/dsa_catalog.json`
- CLI subcommands in `src/euri_codegen/cli.py` calling `generator.py` and `optimizer.py`
- Euri AI SDK wrapped by `src/euri_codegen/euri_client.py` for stable I/O

## Why it's built this way
- Separation of concerns keeps prompts, SDK calls, and CLI logic independent
- JSON specs allow easy extension without changing code
- Tests ensure generated code remains correct and improvements don’t regress
- Optional dev tooling improves maintainability for long-term use

## Troubleshooting
- If generation fails, ensure `EURI_API_KEY` is set and network access is available.
- Use `python -m euri_codegen doctor` to run environment checks.
- For large generations, increase `--max-tokens`.

## License
You own your generated code. Dependencies follow their respective licenses.
