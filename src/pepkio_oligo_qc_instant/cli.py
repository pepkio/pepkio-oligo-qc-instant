# SPDX-License-Identifier: MIT
"""Command-line interface for pepkio-oligo-qc-instant."""

from __future__ import annotations

import json
import sys
from typing import Any

import click

from .client import PepkioClient
from .config import resolve_api_key, resolve_base_url
from .exceptions import PepkioAPIError


def _client(api_key: str | None, base_url: str | None) -> PepkioClient:
    resolved_base = resolve_base_url(base_url)
    return PepkioClient(
        api_key=api_key or resolve_api_key(base_url=resolved_base),
        base_url=resolved_base,
    )


@click.group()
@click.option(
    "--api-key",
    default=None,
    help="Pepkio API key (tools:run scope); else LOCAL_PEPKIO_API_KEY or PEPKIO_API_KEY from env",
)
@click.option(
    "--base-url",
    default=None,
    help="Tools API base URL (default: https://tools.pepkio.com or PEPKIO_API_BASE_URL)",
)
@click.pass_context
def main(ctx: click.Context, api_key: str | None, base_url: str | None) -> None:
    """Python client for Pepkio oligo-qc-instant."""
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["base_url"] = base_url


@main.command("manifest")
@click.option("--examples", is_flag=True, help="List example names only")
@click.pass_context
def manifest_cmd(ctx: click.Context, examples: bool) -> None:
    """Fetch and print the tool manifest."""
    with _client(ctx.obj["api_key"], ctx.obj["base_url"]) as client:
        data = client.get_manifest()
    if examples:
        for name in data.get("examples", []):
            if isinstance(name, dict) and name.get("name"):
                click.echo(name["name"])
            elif isinstance(name, str):
                click.echo(name)
        return
    click.echo(json.dumps(data, indent=2))


@main.command("run")
@click.option("--example", "example_name", help="Run a named manifest example")
@click.option("--input-json", "input_json", help="Tool input as JSON object")
@click.option("--label", help="Optional run label")
@click.option("--idempotency-key", help="Optional idempotency key")
@click.pass_context
def run_cmd(
    ctx: click.Context,
    example_name: str | None,
    input_json: str | None,
    label: str | None,
    idempotency_key: str | None,
) -> None:
    """Run the tool and print the result JSON."""
    if bool(example_name) == bool(input_json):
        raise click.UsageError("Provide exactly one of --example or --input-json")

    try:
        with _client(ctx.obj["api_key"], ctx.obj["base_url"]) as client:
            if example_name:
                inp: dict[str, Any] = client.get_example_input(example_name)
            else:
                inp = json.loads(input_json or "{}")
                if not isinstance(inp, dict):
                    raise click.ClickException("--input-json must be a JSON object")
            result = client.run(
                inp,
                idempotency_key=idempotency_key,
                label=label,
            )
        click.echo(json.dumps(result.model_dump(exclude_none=True), indent=2))
    except (PepkioAPIError, ValueError, json.JSONDecodeError) as e:
        click.echo(str(e), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
