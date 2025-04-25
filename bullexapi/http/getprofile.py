"""Module for Bullex http getprofile resource."""

from bullexapi.http.resource import Resource


class Getprofile(Resource):
    """Class for Bullex getprofile resource."""
    # pylint: disable=too-few-public-methods

    url = "getprofile"

    def _get(self):
        """Send get request for Bullex API getprofile http resource.

        :returns: The instance of :class:`requests.Response`.
        """
        return self.send_http_request("GET")

    def __call__(self):
        """Method to get Bullex API getprofile http request.

        :returns: The instance of :class:`requests.Response`.
        """
        return self._get()
