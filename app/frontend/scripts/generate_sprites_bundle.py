#!/usr/bin/env python3
"""Generate a JSON bundle of sprites for the frontend.

Usage:
  python app/frontend/scripts/generate_sprites_bundle.py --out app/frontend/src/data/sprites.json
"""
import argparse
import json
from app.backend import sprites_data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(sprites_data.SPRITES, f, indent=2, ensure_ascii=False)
    print("Wrote", args.out)


if __name__ == "__main__":
    main()
