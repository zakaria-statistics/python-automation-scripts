# Python Automation Lab

A tiny lab project that keeps environment-specific Kubernetes manifests in code. It reads structured data from `envs.yaml`, renders the `templates/deployment.yaml.j2` Jinja template, and drops fully baked YAML into `build/`.

## Requirements:

- Python 3.10+
- Pip (or another installer that understands `requirements.txt`)

Install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Render all environments to the `build/` directory:

```bash
python main.py
```

Render only staging and prod into a custom directory:

```bash
python main.py --env staging --env prod --outdir out/manifests
```

Preview the output for an environment without writing files:

```bash
python main.py --env dev --dry-run
```

## Project layout

```
python-automation-lab/
├── envs.yaml              # Shared settings + per-environment overrides
├── templates/
│   └── deployment.yaml.j2 # Kubernetes deployment/service/HPA template
├── build/                 # Output directory (safe to clean)
├── main.py                # Entry point for rendering
├── requirements.txt       # Python dependency pins
└── README.md              # You are here
```

Tweak `envs.yaml` or `templates/deployment.yaml.j2`, re-run `python main.py`, and the manifests will be regenerated in seconds.
