#!/usr/bin/bash

(
  set -e
  count=0
  while IFS= read -r prompt || [[ -n "$prompt" ]]; do
    [[ "$prompt" =~ ^[[:space:]]*$ ]] && continue
    [[ "$prompt" =~ ^[[:space:]]*# ]] && continue

    count=$((count + 1))
    printf -v prefix 'collection/scene-%03d' "$count"

    printf '\nGenerating scene %03d: %s\n' "$count" "$prompt"
    python generate.py "$prompt" --batch 4 --prefix "$prefix"
  done < prompts.txt
)
