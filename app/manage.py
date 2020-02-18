#!/usr/bin/env ipython

import click
from flask import Flask
from flask.cli import AppGroup
from flask_app import app
from server import utils

dns_cli = AppGroup("dns", help="Add/Delete subdomains in the config")


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@dns_cli.command("add")
@click.argument("subdomain")
@click.option(
    "--secret",
    default=None,
    help="API secret for the subdomain. If non given it will be generated",
)
@click.option(
    "--length", default=25, help="Length of the secret to generate (default:25)"
)
def create_dns_entry(subdomain, secret, length):
    """Add a new subdomain to the config
    """
    print(f"[!] Adding {subdomain} as subdomain")
    if secret is None:
        secret = utils.random_string(length)
        print(f"[!] Generated {secret} as api secret")
    msg = utils.add_subdomain(subdomain, secret)
    print(msg)


@dns_cli.command("del")
@click.argument("subdomain")
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Are you sure you want to remove the subdomain from config",
)
def remove_dns_entry(subdomain):
    """Removes an existing subdomain
    """
    msg = utils.del_subdomain(subdomain)
    print(msg)
    print("[!] {subdomain} removed")


app.cli.add_command(dns_cli)
