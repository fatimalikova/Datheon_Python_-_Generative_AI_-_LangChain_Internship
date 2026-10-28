import argparse
import json
import argparse
import time
from google.genai import errors
from pathlib import Path

from google import genai
from google.genai import types
from pydantic import ValidationError

from config import GOOGLE_API_KEY, MODEL
from task1_json_extractor.prompts import build_prompt
from task1_json_extractor.schemas import SCHEMAS

client = genai.Client(api_key=GOOGLE_API_KEY)


def extract(doc_type: str, text: str, max_retries: int = 3):
    schema = SCHEMAS[doc_type]
    prompt = build_prompt(doc_type, text)
    last_error = None

    for attempt in range(1, max_retries + 1):
        full_prompt = prompt
        if last_error:
            full_prompt += f"\n\nPrevious output was invalid: {last_error}\nFix it."

        response = None
        for wait in (2, 5, 10, 20):
            try:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        temperature=0,
                    ),
                )
                break
            except errors.ServerError:
                print(f"Server məşğuldur, {wait} saniyə gözləyirəm...")
                time.sleep(wait)
        if response is None:
            raise RuntimeError("Server cavab vermədi, bir az sonra yenidən cəhd et.")
        try:
            return schema.model_validate_json(response.text)
        except (ValidationError, ValueError) as e:
            last_error = str(e)
            print(f"[attempt {attempt}] validation failed, retrying...")

    raise RuntimeError(f"Could not get valid JSON: {last_error}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["invoice", "resume"], required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--out", default=None, help="optional output .json path")
    args = parser.parse_args()

    text = Path(args.file).read_text(encoding="utf-8")
    result = extract(args.type, text)
    output = json.dumps(result.model_dump(), indent=2, ensure_ascii=False)
    print(output)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()