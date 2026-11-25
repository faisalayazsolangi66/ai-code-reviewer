# ai-code-reviewer

Send a code file to the OpenAI API for a review. The review covers bugs,
security issues, readability/style, and concrete improvement suggestions.

## Requirements

- Python 3.8+
- No third-party packages (standard library only; API calls use `urllib`)
- An OpenAI account with API access

## API key

The API key is read **only** from the `OPENAI_API_KEY` environment
variable. Never hardcode a key in a file, and never share it.

```bash
export OPENAI_API_KEY='sk-...'
```

If the variable is not set, the tool exits with a clear error and does
not call the API.

## Usage

```bash
python3 main.py app.py
python3 main.py app.py --focus security -o review.md
python3 main.py script.js -m gpt-4o-mini --max-tokens 1500
```

Options:

- `file` — code file to review
- `-m, --model` — model to use (default: gpt-4o-mini)
- `--focus` — ask the reviewer to focus on one area, e.g. `security`
- `-t, --temperature` — sampling temperature 0–2 (default: 0.3)
- `--max-tokens` — maximum tokens in the reply (default: 1000)
- `-o, --output` — save the review to a file

## Example

```bash
$ export OPENAI_API_KEY='sk-...'
$ python3 main.py app.py --focus security
```

Sample output:

```
## Bugs
- `parse_input` does not validate empty strings, so an empty file raises an unhandled IndexError on line 12.

## Security
- The SQL query on line 30 builds its WHERE clause with string formatting; use a parameterized query instead.

## Suggestions
- Add a unit test for the empty-input case and rename `tmp` to something descriptive.
```

## License

MIT — see [LICENSE](LICENSE).
