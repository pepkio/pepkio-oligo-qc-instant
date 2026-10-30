# SPDX-License-Identifier: MIT
"""Quickstart example for pepkio_oligo_qc_instant."""

import os
from pepkio_oligo_qc_instant import PepkioClient


def main():
    api_key = os.getenv("PEPKIO_API_KEY", "your-api-key")
    with PepkioClient(api_key=api_key) as client:
        manifest = client.get_manifest()
        print(f"Tool ID: {manifest.get('tool_id')}")
        print(f"Tool Name: {manifest.get('name')}")

        examples = client.list_examples()
        if examples:
            example_name = examples[0]
            print(f"Running example: {example_name}")
            example_input = client.get_example_input(example_name)
            result = client.run(example_input)
            print(f"Status: {result.status}")
            if isinstance(result.result, dict):
                print(f"Result summary keys: {list(result.result.keys())}")
            else:
                print(f"Result: {result.result}")


if __name__ == "__main__":
    main()
