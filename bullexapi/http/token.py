"""Module for Bullex http token resource."""

from bullexapi.http.resource import Resource
from bullexapi.http.auth import Auth


class Token(Resource):
    """Class for Bullex http token resource."""
    # pylint: disable=too-few-public-methods

    url = "/".join((Auth.url, "token"))

    def __init__(self, api):
        super(Token, self).__init__(api)

    def _get(self):
        """Send get request for Bullex API token http resource.

        :returns: The instance of :class:`requests.Response`.
        """
        return self.send_http_request("GET")

    def __call__(self):
        """Method to get Bullex API token http request.

        :returns: The instance of :class:`requests.Response`.
        """
        return self._get()
