#!/usr/bin/env python3
import argparse
from pathlib import Path


parser = argparse.ArgumentParser(description="Rename a model folder and its prefixed files.")
parser.add_argument("--model_name_current", required=True)
parser.add_argument("--model_name_new", required=True)
args = parser.parse_args()

if args.model_name_current == args.model_name_new:
    parser.error("The current and new model names must differ.")
if Path(args.model_name_current).name != args.model_name_current or Path(args.model_name_new).name != args.model_name_new:
    parser.error("Model names must be folder names, not paths.")

models_dir = Path(__file__).resolve().parent
current_dir = models_dir / args.model_name_current
new_dir = models_dir / args.model_name_new

if not current_dir.is_dir():
    parser.error(f"Model folder does not exist: {current_dir}")
if new_dir.exists():
    parser.error(f"Destination already exists: {new_dir}")

current_dir.rename(new_dir)
for path in list(new_dir.iterdir()):
    if path.is_file() and path.name.startswith(args.model_name_current):
        new_path = path.with_name(args.model_name_new + path.name[len(args.model_name_current):])
        print(f"Renaming file: {path.name} -> {new_path.name}")
        path.rename(new_path)

print(f"Renamed folder: {current_dir.name} -> {new_dir.name}")
