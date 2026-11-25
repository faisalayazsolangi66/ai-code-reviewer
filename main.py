#!/usr/bin/env python3
"""Send a code file to the OpenAI API for a review.

The API key is read ONLY from the OPENAI_API_KEY environment variable.
Never hardcode a key. Uses urllib from the standard library only.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.openai.com/v1/chat/completions"

DEFAULT_PROMPT = (
    "Review the following code. Report: (1) bugs or logic errors, "
    "(2) security issues, (3) readability and style problems, "
    "(4) concrete suggestions to improve it. Be specific and cite "
    "line numbers or code snippets where helpful. If the code looks "
    "fine, say so briefly."
)


def get_api_key():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("Error: OPENAI_API_KEY is not set.", file=sys.stderr)
        print("Set it before running this tool, for example:", file=sys.stderr)
        print("  export OPENAI_API_KEY='sk-...'", file=sys.stderr)
        print("Never paste your key into a file or share it.", file=sys.stderr)
        return None
    return key


def call_openai(api_key, code, filename, model, temperature, max_tokens, focus):
    prompt = DEFAULT_PROMPT
    if focus:
        prompt += f"\nPay particular attention to: {focus}."
    prompt += f"\n\nFile: {filename}\n```\n{code}\n```"
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system",
             "content": "You are a senior software engineer doing a "
                        "thorough, constructive code review."},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    request = urllib.request.Request(
        API_URL, data=payload,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Error: OpenAI API returned HTTP {exc.code}: {body}",
              file=sys.stderr)
        return None
    except urllib.error.URLError as exc:
        print(f"Error: could not reach the OpenAI API: {exc}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Send a code file to the OpenAI API for a review. "
                    "The API key comes from the OPENAI_API_KEY environment "
                    "variable only.")
    parser.add_argument("file", help="Code file to review.")
    parser.add_argument("-m", "--model", default="gpt-4o-mini",
                        help="Model to use (default: gpt-4o-mini).")
    parser.add_argument("--focus", help="Ask the reviewer to focus on one "
                        "area, e.g. 'security' or 'performance'.")
    parser.add_argument("-t", "--temperature", type=float, default=0.3,
                        help="Sampling temperature 0-2 (default: 0.3).")
    parser.add_argument("--max-tokens", type=int, default=1000,
                        help="Maximum tokens in the reply (default: 1000).")
    parser.add_argument("-o", "--output", help="Save the review to this file.")
    args = parser.parse_args()

    api_key = get_api_key()
    if api_key is None:
        return 1

    try:
        with open(args.file, encoding="utf-8") as f:
            code = f.read()
    except OSError as exc:
        print(f"Error: cannot read {args.file}: {exc}", file=sys.stderr)
        return 1
    if not code.strip():
        print(f"Error: {args.file} is empty.", file=sys.stderr)
        return 1

    data = call_openai(api_key, code, args.file, args.model,
                       args.temperature, args.max_tokens, args.focus)
    if data is None:
        return 1
    try:
        review = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        print(f"Error: unexpected API response: {data}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(review if review.endswith("\n") else review + "\n")
        print(f"Saved review to {args.output}")
    else:
        print(review)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
