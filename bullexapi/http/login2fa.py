"""Module for Bullex http login resource."""

from bullexapi.http.resource import Resource


class Login2FA(Resource):
    """Class for Bullex login resource."""
    # pylint: disable=too-few-public-methods

    url = ""

    def _post(self, data=None, headers=None):
        """Send get request for Bullex API login http resource.

        :returns: The instance of :class:`requests.Response`.
        """
        return self.api.send_http_request_v2(method="POST", url="https://auth.trade.bull-ex.com/api/v2/login",data=data, headers=headers)

    def __call__(self, username, password, token_login):
        """Method to get Bullex API login http request.

        :param str username: The username of a Bullex server.
        :param str password: The password of a Bullex server.
        :param str token: The token of a Bullex server 2FA.

        :returns: The instance of :class:`requests.Response`.
        """
        data = {"identifier": username,
                "password": password,
                "token": token_login}

        return self._post(data=data)
