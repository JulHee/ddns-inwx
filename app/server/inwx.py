import logging

import yaml
from INWX.Domrobot import ApiClient
from werkzeug.exceptions import abort

LOGGER = logging.getLogger(__name__)


class DdnsInwx:

    domains = {}
    records = {}

    def __init__(self, config_file_path, domain_live=False):
        try:
            username, password, otp_seed, domains, domain = self._load_config(
                config_file_path
            )
        except Exception as ex:
            LOGGER.exception(ex)
            raise ex

        self.api_client = None
        self.username = username
        self.password = password
        self.otp_seed = otp_seed
        self.domain = domain
        self.config_file_path = config_file_path

        self.key_to_domain = {}
        for d in domains:
            self.key_to_domain.update(d)

        if domain_live:
            self.domain_live = ApiClient.API_LIVE_URL
        else:
            self.domain_live = ApiClient.API_OTE_URL

    def _load_config(self, config_file_path):
        with open(config_file_path, "r") as yaml_file:
            try:
                data = yaml.safe_load(yaml_file)
            except yaml.YAMLError as exc:
                LOGGER.exception(exc)
                return None, None, None, []
        username = data["username"]
        password = data["password"]
        otp_seed = data["otpseed"]
        domains = data["domains"]
        domain = data["domain"]

        if username is None or password is None:
            raise Exception(f"No username or password in {self.config_file_path}")
        else:
            return username, password, otp_seed, domains, domain

    def _check_key(self, key):
        """API-Key to check against configured
        domains

        Returns:
            Domain name to update record
        """
        if key in self.key_to_domain.keys():
            return self.find_matching_records(self.key_to_domain[key])
        else:
            LOGGER.exception(f"Could not match {key} with domains")
            return abort(400, "Could not match key")

    def login(self):
        api_client = ApiClient(api_url=self.domain_live, debug_mode=True)
        login_result = api_client.login(
            self.username, self.password, shared_secret=self.otp_seed
        )
        print(login_result)

        if login_result["code"] == 1000:
            self.api_client = api_client
        else:
            raise Exception(
                "Api error. Code: "
                + str(login_result["code"])
                + "  Message: "
                + login_result["msg"]
            )

    def logout(self):
        self.api_client.logout()

    def get_nameserver_info(self):
        nameserver_info = self.api_client.call_api(
            api_method="nameserver.info", method_params={"domain": self.domain}
        )
        if nameserver_info["code"] == 1000:
            if nameserver_info["resData"]["count"] > 0:
                for record in nameserver_info["resData"]["record"]:
                    DdnsInwx.records.update({record["id"]: record})
        else:
            raise Exception(
                "Api error. Code: "
                + str(nameserver_info["code"])
                + "  Message: "
                + nameserver_info["msg"]
            )

    def get_nameserver_list(self):
        nameserver_list_result = self.api_client.call_api(
            api_method="nameserver.list", method_params={"domain": self.domain}
        )
        if nameserver_list_result["code"] == 1000:
            print(nameserver_list_result)
            if nameserver_list_result["resData"]["count"] > 0:
                for domain in nameserver_list_result["resData"]["domains"]:
                    DdnsInwx.domains.update({domain["id"]: domain})
        else:
            raise Exception(
                "Api error. Code: "
                + str(nameserver_list_result["code"])
                + "  Message: "
                + nameserver_list_result["msg"]
            )

    def find_matching_records(self, domain_to_update):
        LOGGER.info(domain_to_update)
        LOGGER.info(DdnsInwx.records.values())

        loaded = False
        count = 0
        found_records = []
        while count <= 1:

            found_records = list(
                filter(
                    lambda record: record["name"] == domain_to_update,
                    DdnsInwx.records.values(),
                )
            )
            # Maybe records are old -> reload
            if len(found_records) == 0 and not loaded:
                self.get_nameserver_info()
                loaded = True
            count += 1

        if len(found_records) == 0:
            LOGGER.info(f"Could not find record for {domain_to_update}")
            return abort(400)
        return found_records

    def api_update_record(self, record_id, record_content):
        LOGGER.info(f"Updating {record_id} with {record_content}")
        nameserver_list_result = self.api_client.call_api(
            api_method="nameserver.updateRecord",
            method_params={"id": record_id, "content": record_content},
        )
        if nameserver_list_result["code"] != 1000:
            raise Exception(
                "Api error. Code: "
                + str(nameserver_list_result["code"])
                + "  Message: "
                + nameserver_list_result["msg"]
            )

    def update_record(self, ipv4, ipv6, key):
        """Updates the record for a given key

        TODO: If record not in cache call functions to
        get data

        """
        records_to_update = self._check_key(key)
        LOGGER.info(records_to_update)
        for record in records_to_update:
            if record["content"] in (ipv4, ipv6):
                LOGGER.info(
                    f"Not updating {record['name']}({record['type']}):"
                    f" {record['content']}, because it is unchanged."
                )
                continue
            if record["type"] == "A":
                # ipv4
                self.api_update_record(record["id"], ipv4)
            elif record["type"] == "AAAA" and ipv4 != ipv6:
                # If no ipv6 adress is available
                self.api_update_record(record["id"], ipv6)
            else:
                LOGGER.info(f"Neither ipv4 nor ipv6 {record}")
        return True
