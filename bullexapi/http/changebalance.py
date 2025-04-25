"""Module for Bullex changebalance resource."""

from bullexapi.http.resource import Resource
from bullexapi.http.profile import Profile


class Changebalance(Resource):
    """Class for Bullex changebalance resource."""
    # pylint: disable=too-few-public-methods

    url = "/".join((Profile.url, "changebalance"))

    def _post(self, data=None, headers=None):
        """Send get request for Bullex API changebalance http resource.

        :returns: The instance of :class:`requests.Response`.
        """
        return self.send_http_request("POST", data=data, headers=headers)

    def __call__(self,balance_id):
        """Method to get Bullex API changebalance http request.

        :param str balance_id: The balance identifier.

        :returns: The instance of :class:`requests.Response`.
        """
        data = {"balance_id": balance_id}
        return self._post(data)
