# SPDX-License-Identifier: MIT
"""Error handling, input validation, and retry example for pepkio_oligo_qc_instant."""

import os
import time
from pepkio_oligo_qc_instant import PepkioAPIError, PepkioClient


def run_with_retry(client, payload, max_retries=3):
    """Execute tool run with exponential backoff for server errors."""
    for attempt in range(1, max_retries + 1):
        try:
            return client.run(payload)
        except PepkioAPIError as exc:
            if exc.status_code and exc.status_code >= 500 and attempt < max_retries:
                sleep_time = 2 ** attempt
                print(f"[Attempt {attempt}] Server error {exc.status_code}, retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                continue
            raise


def main():
    api_key = os.getenv("PEPKIO_API_KEY", "your-api-key")
    with PepkioClient(api_key=api_key) as client:
        print("1. Testing invalid input error handling...")
        try:
            client.run({})
        except PepkioAPIError as exc:
            print(f"Caught expected API error: HTTP {exc.status_code} - {exc}")
        except Exception as exc:
            print(f"Caught validation error: {exc}")

        print("\n2. Testing resilient execution with valid manifest input...")
        examples = client.list_examples()
        if examples:
            valid_input = client.get_example_input(examples[0])
            try:
                result = run_with_retry(client, valid_input)
                print(f"Resilient run succeeded: status={result.status}")
            except PepkioAPIError as exc:
                print(f"Run failed after retries: {exc}")


if __name__ == "__main__":
    main()
