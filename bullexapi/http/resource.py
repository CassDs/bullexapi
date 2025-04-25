"""Module for base Bullex API HTTP resource."""


class Resource:
    """Class for base Bullex API HTTP resource."""

    def __init__(self, api):
        """
        :param api: The instance of the Bullex API client.
        """
        self.api = api

    def send_http_request(self, method, endpoint, data=None, params=None, headers=None):
        """Send an HTTP request to the Bullex API.

        :param str method: The HTTP request method (e.g., 'GET', 'POST').
        :param str endpoint: The API endpoint to send the request to.
        :param dict data: (optional) The HTTP request body data.
        :param dict params: (optional) The HTTP request query parameters.
        :param dict headers: (optional) The HTTP request headers.

        :returns: The response object from the HTTP request.
        """
        url = f"{self.api.base_url}/{endpoint}"
        return self.api.send_http_request(method, url, data=data, params=params, headers=headers)