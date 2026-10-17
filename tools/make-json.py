#!/usr/bin/python3

import json
import re

input_path = "output/comfy/steel-sky.txt"
output_path = "image_descriptions.json"

def is_separator(line):
    return set(line.strip()) == {"-"} and len(line.strip()) >= 2

def is_stop_line(line):
    # Add more stop triggers here as needed
    return (line.strip().startswith("Total Token Usage Across All Files:") or
            line.strip().startswith('{') or
            line.strip().startswith('}'))

def is_list_line(line):
    stripped = line.lstrip()
    return (
        stripped.startswith("- ") or
        stripped.startswith("* ") or
        bool(re.match(r"^\d+\.\s", stripped))
    )

def join_summary_lines(lines):
    result = []
    for i, line in enumerate(lines):
        result.append(line)
        if i < len(lines) - 1:
            current_is_list = is_list_line(line)
            next_is_list = is_list_line(lines[i+1])
            if current_is_list and not next_is_list and lines[i+1].strip():
                result.append("")  # add blank line to break list in markdown
    return "\n".join(result)

with open(input_path, "r", encoding="utf-8") as f:
    lines = [line.rstrip() for line in f if line.strip()]

entries = []
i = 0
while i < len(lines):
    if lines[i].endswith(".png"):
        filename = lines[i]
        i += 1
        summary_lines = []
        if i < len(lines) and lines[i].startswith("Summary:"):
            first_summary = lines[i][len("Summary:"):].strip()
            if first_summary:
                summary_lines.append(first_summary)
            i += 1
            # Collect all summary lines until next filename, stop line, or end of file
            while (i < len(lines)
                   and not lines[i].endswith(".png")
                   and not is_stop_line(lines[i])):
                line = lines[i]
                if not is_separator(line):
                    summary_lines.append(line)
                i += 1
        summary = join_summary_lines(summary_lines).strip()
        entries.append({
            "filename": filename,
            "summary": summary
        })
    else:
        i += 1

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)

print(f"✅ Wrote {len(entries)} entries to {output_path}")