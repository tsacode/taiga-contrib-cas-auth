import cas
import requests
from collections import namedtuple
from django.conf import settings
from taiga.base import exceptions as exc

CAS_URL = getattr(settings, "CAS_URL")
CAS_FIELD = getattr(settings, "CAS_FIELD")

User = namedtuple("User", ["id", "username", "full_name", "bio", "email"])


def cas_field_search(default_data_name):
    """
    :param: default_data_name: default name of the data in the dictionary
    :return: either the specified data name in CAS_FIELD or standard data name
    """
    return CAS_FIELD.get(default_data_name) or default_data_name


def make_user(data):
    """
    Create a User tuple with the CAS data.
    :param data: data on the cas user send by CAS server
    :return: a User made with these data
    """
    return User(username=data[0],
                id=data[1].get(cas_field_search("id"), ""),
                full_name=data[1].get(cas_field_search("full_name"), ""),
                bio=data[1].get(cas_field_search("bio"), ""),
                email=data[1].get(cas_field_search("email"), ""))


def me(access_ticket: str, redirect_uri: str) -> tuple:
    """
    Validate CAS ticket and extract CAS user's attributes
    :param access_ticket: Ticket given by CAS (Protocol SAML)
    :param redirect_uri: uri of redirection
    :return email, User namedtuple
    """
    client = cas.CASClientWithSAMLV1(None, redirect_uri, CAS_URL)
    try:
        data = client.verify_ticket(access_ticket)
    except requests.exceptions.ConnectionError as e:
        con_error = ConnectionError(
            "Unable to establish connection with CAS server." +
            " Please verify your proxy or CAS_URL")
        raise con_error from e
    user = make_user(data)
    return user.email, user
