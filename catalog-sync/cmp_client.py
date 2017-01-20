"""
A simple client for the CMP API.
"""

import requests


class CMPClient(object):
    """
    A simple client for the CMP API.
    """

    def __init__(self, base_address, api_key, secret_key):
        """
        Create a new CMP API client.

        :param base_address: The base address for the CMP API.
        :param api_key: The API key (username) for authentication to the CMP API.
        :param secret_key: The secret key (password) for authentication to the CMP API.
        """

        self.base_address = base_address
        self._session = requests.session()
        self._session.auth = (api_key, secret_key)

    def create_service_definition(self, service_definition):
        """
        Create a new service definition.

        :param service_definition: The service definition.
        :return: The API response.
        """

        return self._post("/service_defs", service_definition)

    def list_service_definitions(self):
        return self._get("/service_defs")

    def get_service_catalog(self):
        return self._get("/service_catalog")

    def update_service_catalog(self, catalog):
        return self._put("/service_catalog", catalog)

    def list_modules(self):
        return self._get("/modules")

    def create_module(self, name, event_source, source_code):
        return self._post("/modules", {
            "name": name,
            "language": "python",
            "event_source": event_source,
            "file_type": "inline",
            "source_code": source_code
        })

    def update_module(self, id, name, source_code):
        return self._patch("/modules/" + id, {
            "name": name,
            "file_type": "inline",
            "source_code": source_code
        })

    def _get(self, relative_url):
        """
        Perform an HTTP GET.
        :param relative_url: The relative URI to GET.
        :return: The API response.
        """

        return self._session.get(self.base_address + relative_url)

    def _post(self, relative_url, data=None):
        """
        Perform an HTTP POST.
        :param relative_url: The relative URI to POST.
        :param data: The POST body (if any).
        :return: The API response.
        """

        return self._session.post(self.base_address + relative_url, json=data)

    def _put(self, relative_url, data=None):
        """
        Perform an HTTP PUT.
        :param relative_url: The relative URI to PUT.
        :param data: The PUT body (if any).
        :return: The API response.
        """

        return self._session.put(self.base_address + relative_url, json=data)

    def _patch(self, relative_url, data=None):
        """
        Perform an HTTP PATCH.
        :param relative_url: The relative URI to PATCH.
        :param data: The PATCH body (if any).
        :return: The API response.
        """

        return self._session.patch(self.base_address + relative_url, json=data)

    def close(self):
        """
        Dispose of resources being used by the client.
        """

        if self._session:
            self._session.close()
            self._session = None
