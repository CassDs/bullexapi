"""Module for Bullex http login resource."""

from bullexapi.http.resource import Resource


class Events(Resource):
    """Class for Bullex login resource."""
    # pylint: disable=too-few-public-methods

    url = ""

    def send_http(self,method, data=None, headers=None):
        """Send get request for Bullex API login http resource.

        :returns: The instance of :class:`requests.Response`.
        """
        return self.api.send_http_request_v2(method=method, url="https://event.trade.bull-ex.com/api/v1/events",data=data)

    def __call__(self,method,data,headers=None):
        """Method to get Bullex API login http request.

        :param str username: The username of a Bullex server.
        :param str password: The password of a Bullex server.

        :returns: The instance of :class:`requests.Response`.
        """
         
         
        return self.send_http(method=method,data=data,headers=headers)
