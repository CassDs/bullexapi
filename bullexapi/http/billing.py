"""Module for Bullex billing resource."""

from bullexapi.http.resource import Resource


class Billing(Resource):
    """Class for Bullex billing resource."""
    # pylint: disable=too-few-public-methods

    url = "billing"
