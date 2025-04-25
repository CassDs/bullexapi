"""Module for Bullex http auth resource."""

from bullexapi.http.resource import Resource


class Auth(Resource):
    """Class for Bullex http auth resource."""
    # pylint: disable=too-few-public-methods

    url = "auth"
