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

    def close(self):
        """
        Dispose of resources being used by the client.
        """

        if self._session:
            self._session.close()
            self._session = None
