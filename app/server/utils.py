#!/usr/bin/env python3
import logging
import random
import string

import yaml
from flask import abort
from server.inwx import DdnsInwx

LOGGER = logging.getLogger(__name__)

CONFIG_FILE = "./config/config.yaml"


def random_string(n):
    pool = string.ascii_letters + string.digits
    return "".join([random.choice(pool) for i in range(n)])


def load_config():
    with open(CONFIG_FILE, "r") as yaml_file:
        try:
            data = yaml.safe_load(yaml_file)
        except yaml.YAMLError as exc:
            LOGGER.exception(exc)
    return data


def write_config(data):
    with open(CONFIG_FILE, "w") as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)


def add_subdomain(subdomain, secret):
    data = load_config()
    domains = data["domains"]

    if subdomain_exists(domains, subdomain):
        return "[X] Subdomain already exists. Please delete the subdomain before adding"

    domains.append({secret: subdomain})
    write_config(data)
    return "[!] Updated config"


def del_subdomain(subdomain):
    data = load_config()
    domains = data["domains"]

    if not subdomain_exists(domains, subdomain):
        return "[X] Subdomain not found in config"

    elem_to_remove = None
    for elem in domains:
        if subdomain in elem.values():
            elem_to_remove = elem
    domains.remove(elem_to_remove)

    write_config(data)


def subdomain_exists(domains, subdomain):
    tmp_domains = {}
    for d in domains:
        tmp_domains.update(d)
    for key, value in tmp_domains.items():
        if value == subdomain:
            return True
    return False


def connect_to_inwx(live):
    client = DdnsInwx(CONFIG_FILE, live)
    try:
        client.login()
    except Exception as ex:
        LOGGER.exception(ex)
        return abort(500)
    return client


def update_record(ipv4, ipv6, key):
    live = True
    client = connect_to_inwx(live)
    success = client.update_record(ipv4, ipv6, key)
    client.logout()
    return success


if __name__ == "__main__":
    live = True
    client = connect_to_inwx(live)
    client.logout()
