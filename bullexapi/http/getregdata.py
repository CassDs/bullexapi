"""Module for Bullex http getregdata resource."""

from bullexapi.http.resource import Resource
from bullexapi.http.register import Register


class Getprofile(Resource):
    """Class for Bullex getregdata resource."""
    # pylint: disable=too-few-public-methods

    url = "/".join((Register.url, "getregdata"))

    def _get(self):
        """Send get request for Bullex API getregdata http resource.

        :returns: The instance of :class:`requests.Response`.
        """
        return self.send_http_request("GET")

    def __call__(self):
        """Method to get Bullex API getregdata http request.

        :returns: The instance of :class:`requests.Response`.
        """
        return self._get()
