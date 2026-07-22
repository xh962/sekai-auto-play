#!/usr/bin/env bash
# tools/process_assets.sh
# Script to run locally to process videos in assets/ and generate templates
# Usage: bash tools/process_assets.sh

set -e

# ensure virtualenv or python exists
python -m pip install --upgrade pip
pip install -r requirements.txt

mkdir -p templates/auto_templates
for f in assets/*.mp4; do
  echo "Processing $f"
  base=$(basename "$f" .mp4)
  mkdir -p frames/$base
  ffmpeg -y -i "$f" -vf fps=2 frames/$base/frame_%04d.png
  for img in frames/$base/*.png; do
    echo "Generating templates from $img"
    python tools/auto_template_generator.py --image "$img" --out-dir templates/auto_templates --debug
  done
done

echo "Done. Check templates/auto_templates/ for results."
