"""Module for Bullex register resource."""

from bullexapi.http.resource import Resource


class Register(Resource):
    """Class for Bullex register resource."""
    # pylint: disable=too-few-public-methods

    url = "register"
