#!/usr/bin/python3

import os
import base64
from openai import OpenAI
import subprocess
import time
import random
import json
import sys

# Retrieve the API key from environment variable
XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    raise ValueError("XAI_API_KEY environment variable not set")

# Initialize the OpenAI client
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

def encode_image(image_path):
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def get_image_summary(image_path):
    """Get a summary of the image content and token usage using the xAI API."""
    try:
        base64_image = encode_image(image_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high",
                        },
                    },
                    {
                        "type": "text",
                        "text": "What's in this image?",
                    },
                ],
            },
        ]
        completion = client.chat.completions.create(
            model="grok-2-vision-latest",
            messages=messages,
            temperature=0.01,
        )
        summary = completion.choices[0].message.content
        # Extract token usage
        token_usage = {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens
        } if completion.usage else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        return summary, token_usage
    except Exception as e:
        return f"Error processing {image_path}: {str(e)}", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

def main():
    output_file = "steel-sky.txt"
    # Initialize token counters
    total_token_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }
    # Get all PNG files in the current directory
    png_files = [file for file in os.listdir(".") if file.lower().endswith(".png")]
    total_files = len(png_files)
    print(f"Found {total_files} PNG files to process.", file=sys.stderr)

    # Use subprocess.Popen with tee to write to file and terminal
    process = subprocess.Popen(
        ["tee", "-a", output_file],
        stdin=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    try:
        with process.stdin as pipe:
            for i, image_path in enumerate(png_files, 1):
                summary, token_usage = get_image_summary(image_path)
                # Update total token usage
                total_token_usage["prompt_tokens"] += token_usage["prompt_tokens"]
                total_token_usage["completion_tokens"] += token_usage["completion_tokens"]
                total_token_usage["total_tokens"] += token_usage["total_tokens"]
                # Prepare output string for individual image
                output = (
                    f"{image_path}\n"
                    f"Summary: {summary}\n"
                    f"{'-'*50}\n"
                )
                # Write to pipe (tee will handle file and terminal output)
                pipe.write(output)
                pipe.flush()
                # Add random delay every 10 files
                if i % 10 == 0:
                    time.sleep(random.uniform(0.5, 2.0))
            
            # After processing all files, append total token usage
            total_output = (
                f"\nTotal Token Usage Across All Files:\n"
                f"{json.dumps(total_token_usage, indent=2)}\n"
                f"{'='*50}\n"
            )
            pipe.write(total_output)
            pipe.flush()
    finally:
        process.stdin.close()
        process.wait()

if __name__ == "__main__":
    main()