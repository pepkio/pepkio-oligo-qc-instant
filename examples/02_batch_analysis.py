# SPDX-License-Identifier: MIT
"""Batch analysis and parameter variation example for pepkio_oligo_qc_instant."""

import os
from pepkio_oligo_qc_instant import PepkioClient


def main():
    api_key = os.getenv("PEPKIO_API_KEY", "your-api-key")
    with PepkioClient(api_key=api_key) as client:
        examples = client.list_examples()
        print(f"Discovered {len(examples)} test configurations for batch execution:")

        batch_results = []
        for name in examples[:3]:
            print(f"-> Processing batch item: {name}")
            try:
                inp = client.get_example_input(name)
                res = client.run(inp, label=f"batch_{name}")
                batch_results.append({
                    "example": name,
                    "status": res.status,
                    "run_id": res.run_id,
                    "permalink": res.permalink,
                })
            except Exception as exc:
                print(f"   Failed to run {name}: {exc}")

        print("\nBatch execution summary:")
        for item in batch_results:
            print(f" - [{item['status']}] {item['example']}: {item['permalink']}")


if __name__ == "__main__":
    main()
