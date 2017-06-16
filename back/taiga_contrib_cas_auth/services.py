from django.db import transaction as tx
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from taiga.base import exceptions as exc
from taiga.auth.services import make_auth_response_data
from django.conf import settings
from . import connector
import gettext
import os
from pkg_resources import resource_filename
from taiga_contrib_cas_auth import cas_auth_exception as c_a_e

CAS_BIND = getattr(settings, "CAS_BIND", True)
CAS_OVERWRITE = getattr(settings, "CAS_OVERWRITE", True)
CAS_CREATE = getattr(settings, "CAS_CREATE", True)


def bind_if_equals(user1, user2, cas_id):
    """
    if users are different it will raise an Integrity error
    else if CAS_BIND is enabled it will let cas_register bind
    :param:user1: a Taiga user
    :param:user2: a Taiga user
    """
    ErrorMessage_username_mail_diff_account = _(
        "One user already registered your cas username, and another user"
        " registered your cas email")
    ErrorMessage_CAS_BIND = _("CAS_BIND disabled")
    auth_data_model = apps.get_model("users", "AuthData")
    if user1 == user2:
        if not CAS_BIND:
            raise c_a_e.CAS_Bind_Error(ErrorMessage_CAS_BIND)
        else:
            auth_data_model.objects.create(user=user1, key="cas",
                                           value=cas_id,
                                           extra={})
    else:
        raise c_a_e.Username_Email_Diff_Account_Error(
            ErrorMessage_username_mail_diff_account)


def sync_if_free(user, username=None, email=None):
    """
        verify that an email or a username is free:
        if it is free and CAS_OVERWRITE is enabled it synchronizes some data
        else it raises an integrity error
        :param user: A Taiga user
        :param username: a username
        :param email: an email
        """
    ErrorMessage_email = _("Another user has already registered with your "
                           "CAS account's email")
    ErrorMessage_username = _("Another user has already registered with your"
                              " CAS account's username")
    user_model = apps.get_model("users", "User")
    if username is not None:
        try:
            user_model.objects.get(username=username)
            # username is in use, wtf ?
            raise c_a_e.Username_Error(ErrorMessage_username)
        except ObjectDoesNotExist:
            # OK, username is not in use
            if CAS_OVERWRITE:
                user.username = username
    if email is not None:
        try:
            user_model.objects.get(email=email)
            # email is in use, wtf ?
            raise c_a_e.Email_Error(ErrorMessage_email)
        except ObjectDoesNotExist:
            # OK, email is not in use
            if CAS_OVERWRITE:
                user.email = email
                user.new_email = None
                user.email_token = None


@tx.atomic
def cas_register(username, email, full_name, cas_id, bio):
    """
    Register a new user from CAS.
    This can raise an IntegrityError exceptions in case of conflicts found.
    :param username: CAS account Username
    :param email: CAS account email
    :param full_name:CAS account full_name
    :param  cas_id: CAS account id
    :param bio: CAS account bio
    :returns: User
    """
    ErrorMessage_CAS_CREATE = _("CAS_CREATE disabled")
    ErrorMessage_no_match = _("Neither your CAS email nor your CAS username "
                              "match with Taiga's username and email")
    ErrorMessage_username_no_email = _("User has already registered your "
                                       "CAS account's username but not your "
                                       "CAS account's email")
    ErrorMessage_email_no_username = _("User has already registered your CAS "
                                       "account's email but not your CAS "
                                       "account's username")
    auth_data_model = apps.get_model("users", "AuthData")
    user_model = apps.get_model("users", "User")
    try:
        # CAS user association exist?
        auth_data = auth_data_model.objects.get(key="cas", value=cas_id)
        # CAS association exist
        user = auth_data.user
        if username == user.username:
            if email == user.email:
                # same user, OK go on
                pass
            else:
                # same username but different emails, sync
                sync_if_free(email=email, user=user)
        else:
            if email == user.email:
                # different username but same emails, sync
                sync_if_free(username=username,
                             user=user)
            else:
                # same cas_id but different users, wtf ?
                raise c_a_e.No_Match_Error(ErrorMessage_no_match)
        if CAS_OVERWRITE:
            # Update and save user
            user.full_name = full_name
            user.save(
                update_fields=["email", "new_email", "email_token",
                               "full_name",
                               "bio"])
    except auth_data_model.DoesNotExist:
        # there is no user associated with this cas_id
        try:
            user = user_model.objects.get(username=username)
            try:
                email_user = user_model.objects.get(email=email)
                bind_if_equals(user, email_user, cas_id)
            except user_model.DoesNotExist:
                # email is free but username is already used
                raise c_a_e.Username_No_Email_Error(
                    ErrorMessage_username_no_email)
        except user_model.DoesNotExist:
            # username does not match with any Taiga account'username
            try:
                user_model.objects.get(email=email)
                # username is free but email is already used
                raise c_a_e.Email_No_Username_Error(
                    ErrorMessage_email_no_username)
            except user_model.DoesNotExist:
                # username and email are free. Create a new user
                if CAS_CREATE:
                    user = user_model.objects.create(email=email,
                                                     username=username,
                                                     full_name=full_name,
                                                     bio=bio)
                    auth_data_model.objects.create(user=user, key="cas",
                                                   value=cas_id, extra={})
                else:
                    raise c_a_e.CAS_CREATE_Error(ErrorMessage_CAS_CREATE)
    return user


def cas_login_func(request):
    """
    
    :param request: 
    :return: 
    """
    language = request.DATA.get('currentLanguage', 'en')
    os.environ["LANGUAGE"] = language
    gettext.install('services', localedir=os.path.abspath(
        resource_filename('taiga_contrib_cas_auth', 'i18n')))
    ticket = request.DATA.get('ticket', None)
    redirect_uri = request.DATA.get('redirectUri', None)
    email, user_info = connector.me(ticket, redirect_uri)
    user = cas_register(username=user_info.username,
                        email=email,
                        full_name=user_info.full_name,
                        cas_id=user_info.id,
                        bio=user_info.bio)
    data = make_auth_response_data(user)
    return data
