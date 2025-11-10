#!/usr/bin/env python3
"""
This script:
1. Reads envs.yaml
2. Picks the environment you asked for (via --env)
3. Renders the Jinja2 template in templates/ using that env data
4. Writes the final YAML to <outdir>/deployment-<env>.yaml
   ...unless you use --dry-run, then it just prints it.

Examples:
    python main.py --env dev
    python main.py --env prod --outdir out/manifests
    python main.py --env staging --dry-run
"""

import argparse
import sys
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# Folder where this script is located
BASE_DIR = Path(__file__).resolve().parent

def load_env_config(env_name: str) -> dict:
    """
    Load envs.yaml and return the section for the given environment.
    """
    config_path = BASE_DIR / "envs.yaml"

    if not config_path.exists():
        print(f"[ERROR] Config file {config_path} not found.")
        sys.exit(1)

    with open(config_path, "r") as f:
        all_envs = yaml.safe_load(f) or {}

    if env_name not in all_envs:
        print(f"[ERROR] Environment '{env_name}' not found in {config_path}.")
        print(f"Available envs: {', '.join(all_envs.keys())}")
        sys.exit(2)

    return all_envs[env_name]

def render_template(template_name: str, context: dict) -> str:
    """
    Render a Jinja2 template from templates/ with the given context.
    """
    templates_dir = BASE_DIR / "templates"
    env = Environment(loader=FileSystemLoader(str(templates_dir)))

    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        print(f"[ERROR] Template {template_name} not found in {templates_dir}")
        sys.exit(3)

    return template.render(**context)

def write_build_file(env_name: str, content: str, outdir: Path):
    """
    Write the rendered YAML to <outdir>/deployment-<env>.yaml.
    Create the directory if it doesn't exist.
    """
    outdir.mkdir(parents=True, exist_ok=True)  # parents=True lets us create nested dirs
    out_file = outdir / f"deployment-{env_name}.yaml"
    out_file.write_text(content)
    print(f"[INFO] Wrote rendered manifest to {out_file}")

def parse_args():
    """
    Define CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Render k8s manifests from YAML env config."
    )

    # required
    parser.add_argument(
        "--env",
        required=True,
        help="Environment name (dev/staging/prod)",
    )

    # optional: choose template
    parser.add_argument(
        "--template",
        default="deployment.yaml.j2",
        help="Template file inside templates/ directory",
    )

    # NEW: optional output directory
    parser.add_argument(
        "--outdir",
        default="build",
        help="Directory where the rendered manifest will be written (default: build)",
    )

    # NEW: dry-run flag (user asked for -dry-run, I'll add both --dry-run and -d)
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Print rendered manifest to stdout instead of writing to file",
    )

    return parser.parse_args()

def main():
    args = parse_args()

    # 1) load env data from YAML
    env_config = load_env_config(args.env)

    # 2) render template with that data
    rendered = render_template(args.template, env_config)

    # 3) if dry-run → just print and exit
    if args.dry_run:
        print("[INFO] Dry run enabled. Rendering to stdout:\n")
        print(rendered)
        # exit 0 → success
        sys.exit(0)

    # 4) otherwise, write to chosen outdir
    outdir_path = (BASE_DIR / args.outdir).resolve()
    write_build_file(args.env, rendered, outdir_path)

    print("[OK] Render finished.")
    sys.exit(0)

if __name__ == "__main__":
    main()
