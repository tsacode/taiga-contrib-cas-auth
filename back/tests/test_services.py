import unittest
import sys
from taiga.base import exceptions as exc
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django
import gettext
import os
from taiga_contrib_cas_auth import cas_auth_exception as c_a_e
from pkg_resources import resource_filename

django.setup()
from taiga_contrib_cas_auth import services

os.path.realpath


gettext.install('services', localedir=os.path.abspath(
    resource_filename('taiga_contrib_cas_auth', 'i18n')))

sys.path.insert(0, "/srv/taiga")


class TestServices(unittest.TestCase):
    """
     Test services.py
    """
    auth_data_model = apps.get_model("users", "AuthData")
    user_model = apps.get_model("users", "User")

    email_1 = "paul.test1@exemple.com"
    username_1 = "ptest1"
    fullname_1 = "Paul TEST"
    cas_id_1 = "cas_id_test_1"

    email_2 = "paul.test2@exemple.com"
    username_2 = "ptest2"
    fullname_2 = "Paula TEST"
    cas_id_2 = "cas_id_test_2"

    email_3 = "paul.test3@exemple.com"
    username_3 = "ptest3"
    fullname_3 = "Patricia TEST"
    cas_id_3 = "cas_id_test_3"

    def init_user(self, email, username, fullname):
        """
               create a user with email, username and fullname
               or delete it and recreate it if it already exist
               :param: email: an email
               :param:username: an username 
               :param:fullname: a fullname
               :return: user created
               """
        try:
            user = self.user_model.objects.get(username=username, email=email)
            user.delete()
        except self.user_model.DoesNotExist:
            pass
        user = self.user_model.objects.create(username=username, email=email,
                                              full_name=fullname)
        return user

    def init_cas_association(self, cas_id, user):
        """
        create a cas_association with cas_id and user 
        or delete it and recreate it if it already exist
        :param cas_id: an id
        :param user: a Taiga user
        :return: cas_association created
        """
        try:
            auth_data = self.auth_data_model.objects.get(key="cas",
                                                         value=cas_id)
            auth_data.delete()
        except ObjectDoesNotExist:
            pass
        self.auth_data_model.objects.create(key="cas", value=cas_id, user=user,
                                            extra={})

    def init_user_and_cas_association(self, email, username, fullname, cas_id):
        """
        init user and cas_association
        """
        user = self.init_user(email=email, username=username,
                              fullname=fullname)
        self.init_cas_association(cas_id, user)

    def clean_database(self, email=None, username=None, cas_id=None):
        """
        if there is a user and/or cas_id associated it deletes it 
        :param :email: an email that's paired with the username
        :param :username: a username that's paired with the email
        :param :cas_id: a cas_id
        """
        if email is not None and username is not None:
            try:
                user = self.user_model.objects.get(email=email,
                                                   username=username)
                user.delete()
            except ObjectDoesNotExist:
                pass

        if cas_id is not None:
            try:
                auth_data = self.auth_data_model.objects.get(key="cas",
                                                             value=cas_id)
                auth_data.delete()
            except ObjectDoesNotExist:
                pass

    def delete_cas_association_and_associated_account(self, cas_id):
        """
        deletes cas_association and the Taiga account associated 
        to this cas_association
        :param : cas_id : cas_id of the cas_association that is cleaned
        """
        try:
            auth_data = self.auth_data_model.objects.get(key="cas",
                                                         value=cas_id)
            user = auth_data.user
            self.clean_database(user.email, user.username, cas_id)
        except ObjectDoesNotExist:
            pass

    def test_registration_new_account_without_matching_true_cas_register(self):
        """
        Tests that if when the data of the user returned by CAS has no matches 
        with existing account it creates a new Taiga account with the data
        (if CAS_CREATE is true)
        """
        self.clean_database(email=self.email_1,
                            username=self.username_1, cas_id=self.cas_id_1)
        services.CAS_CREATE = True
        try:
            user = services.cas_register(self.username_1, self.email_1,
                                         self.fullname_1, self.cas_id_1, "")
            try:
                user_retrieved = self.user_model.objects.get(
                    username=self.username_1)
                self.assertEqual(user_retrieved, user)
            except ObjectDoesNotExist as e:
                self.fail("user has not been create : %s" % e.args[0])
        except exc.IntegrityError as e:
            self.fail("user has not been create : %s" % e.args[0])
        finally:
            self.clean_database(email=self.email_1,
                                username=self.username_1, cas_id=self.cas_id_1)

    def test_registration_new_account_without_matching_false_cas_register(
            self):
        """
        Tests that when the data of the user returned by CAS have no matches 
        with existing account it throw the good exception 
        (if CAS_CREATE is False)
        """
        self.clean_database(email=self.email_1,
                            username=self.username_1, cas_id=self.cas_id_1)
        services.CAS_CREATE = False
        try:
            services.cas_register(self.username_1, self.email_1,
                                  self.fullname_1, self.cas_id_1, "")
            self.fail("user has been created while CAS_CREATE was false")
        except c_a_e.CAS_CREATE_Error:
            pass


        finally:
            self.clean_database(email=self.email_1,
                                username=self.username_1, cas_id=self.cas_id_1)

    def test_no_existent_user_but_existing_email_cas_register(self):
        """
        Tests that when a user tries to connect to taiga with a CAS
        account that is not bound with a Taiga account if the username is free
        but the email is already used by a Taiga account cas_register throws the
        correct authentication exception 
        """

        self.clean_database(self.email_1, self.username_2, self.cas_id_2)
        self.init_user(
            email=self.email_1,
            username=self.username_1,
            fullname=self.fullname_1)
        try:
            try:
                services.cas_register(self.username_2,
                                      self.email_1,
                                      self.fullname_2,
                                      self.cas_id_2,
                                      "")
                self.fail("No IntegrityError raised")
            except c_a_e.Email_No_Username_Error:
                pass
        finally:
            self.clean_database(self.email_1, self.username_2, self.cas_id_2)
            self.clean_database(email=self.email_1,
                                username=self.username_1)

    def test_no_cas_association_same_username_email_free_cas_cas_register(
            self):
        """
        Tests that when there is no auth_data associated to the cas_id,
         if username exists but the email does not exist it throws the 
         correct exception 
        """
        self.clean_database(email=self.email_2, username=self.username_1)
        self.init_user(
            email=self.email_1,
            username=self.username_1,
            fullname=self.fullname_1)
        try:
            services.cas_register(self.username_1,
                                  self.email_2,
                                  "", self.cas_id_2,
                                  "")
            self.fail("User successfully registered with just username and" +
                      "not the same email")
        except c_a_e.Username_No_Email_Error :
            pass
        finally:
            self.clean_database(email=self.email_1, username=self.username_1)
            self.clean_database(email=self.email_2, username=self.username_1,
                                cas_id=self.cas_id_2)

    def test_bind_on_same_username_email_username_diff_account__cas_register(
            self):
        """
        Tests that when there is no auth_data associated to the cas_id but there
        is an email and a username that exists from different Taiga accounts it
        throws the correct exception
        """
        self.clean_database(self.username_1, self.email_1,
                            cas_id=self.cas_id_1)
        self.init_user(
            email=self.email_1,
            username=self.username_2,
            fullname=self.fullname_1)
        self.init_user(
            email=self.email_2,
            username=self.username_1,
            fullname=self.fullname_2)
        try:
            services.cas_register(self.username_1,
                                  self.email_1,
                                  "", self.cas_id_1,
                                  "")
            self.fail("Bind a taiga account on CAS account while the username"
                      " and the email of your CAS account exist in Different"
                      "Taiga account")

        except c_a_e.Username_Email_Diff_Account_Error:
            pass
        finally:
            self.clean_database(email=self.email_1,
                                username=self.username_1, cas_id=self.cas_id_1)
            self.clean_database(email=self.email_2, username=self.username_1)
            self.clean_database(email=self.email_1, username=self.username_2)

    def test_bind_on_same_username_same_email_true_cas_register(self):
        """
        Tests that when there is no auth_data associated to the cas_id 
        but there is an email and a username that exists from the same Taiga 
        account it binds the CAS account with the Taiga account without 
        overwriting it (if CAS_BIND is true )
        """
        self.clean_database(self.cas_id_2)
        services.CAS_BIND = True
        user = self.init_user(
            email=self.email_1,
            username=self.username_1,
            fullname=self.fullname_1)
        try:
            services.cas_register(self.username_1,
                                  self.email_1,
                                  "", self.cas_id_2,
                                  "")
            auth_data = self.auth_data_model.objects.get(key="cas",
                                                         value=self.cas_id_2)
            self.assertEqual(user, auth_data.user)
        except exc.IntegrityError as e:
            self.fail(e.args[0])
        finally:
            self.clean_database(email=self.email_1,
                                username=self.username_1, cas_id=self.cas_id_2)

    def test_bind_on_same_username_same_email_false_cas_register(self):
        """
        Tests that when there is no auth_data associated to the cas_id but there
        is an email and a username that exists from the same Taiga account it 
        throws the correct exception 
        (if CAS_BIND is false )
        """
        self.clean_database(self.cas_id_2)
        services.CAS_BIND = False
        self.init_user(
            email=self.email_1,
            username=self.username_1,
            fullname=self.fullname_1)
        try:
            user = services.cas_register(self.username_1,
                                         self.email_1,
                                         "", self.cas_id_2,
                                         "")
            auth_data = self.auth_data_model.objects.get(key="cas",
                                                         value=self.cas_id_2)
            if auth_data.user == user:
                self.fail("user has been bind while CAS_Bind was false")
            self.fail("user has been created")
        except c_a_e.CAS_Bind_Error:
            pass
        finally:
            self.clean_database(email=self.email_1,
                                username=self.username_1, cas_id=self.cas_id_2)

    def test_existing_auth_data_without_match_cas_register(self):
        """
        Tests that when there is auth_data associated to the cas_id but that 
        neither CAS username nor CAS email match with the associated Taiga 
        account username and email it throws the correct exception
        """
        self.clean_database(username=self.username_2, email=self.email_2,
                            cas_id=self.cas_id_1)
        self.init_user_and_cas_association(email=self.email_1,
                                           username=self.username_1,
                                           fullname=self.fullname_1,
                                           cas_id=self.cas_id_1)
        try:
            services.cas_register(self.username_2,
                                  self.email_2,
                                  self.fullname_2,
                                  self.cas_id_1,
                                  "bio")
            self.fail("User registered while he has CAs_id matching but" +
                      "neither username nor mail ")
        except c_a_e.No_Match_Error:
            pass
        finally:
            self.delete_cas_association_and_associated_account(self.cas_id_1)
            self.clean_database(email=self.email_2, username=self.username_2)

    def test_cas_association__free_username_same_email_true_cas_register(
            self):
        """
        Tests that when there is auth_data matching with the cas_id, 
        if the username of cas_account does not match with the associated Taiga 
        account but that the username is free if both emails match
        it overwrites the data of the Taiga account with the data of the CAS 
        account, username included (if CAS_OVERWRITE is true)
        """
        self.clean_database(self.email_1, self.username_2)
        self.clean_database(self.email_2, self.username_2)
        services.CAS_OVERWRITE = True
        self.init_user_and_cas_association(email=self.email_1,
                                           username=self.username_1,
                                           fullname=self.fullname_1,
                                           cas_id=self.cas_id_1)
        try:
            user = services.cas_register(self.username_2,
                                         self.email_1,
                                         self.fullname_2,
                                         self.cas_id_1,
                                         "bio")
            self.assertEqual(user.username, self.username_2)
            self.assertEqual(user.full_name, self.fullname_2)

        except exc.IntegrityError as e:
            self.fail(e.args[0])

        finally:
            self.delete_cas_association_and_associated_account(self.cas_id_1)
            self.clean_database(email=self.email_2, username=self.username_2)
            self.clean_database(email=self.email_1, username=self.username_2)
            self.clean_database(email=self.email_1, username=self.username_1)

    def test_cas_association_free_username_same_email_false_cas_register(
            self):
        """
        Tests that when there is auth_data associated with the cas_id of the 
        CAS account if the username of CAS account and the one of Taiga 
        are different but the username of CAS is free if the both emails match 
        it does not bind (if CAS_BIND is false)
        """
        self.clean_database(self.email_1, self.username_2)
        self.clean_database(self.email_2, self.username_2)
        services.CAS_OVERWRITE = False
        self.init_user_and_cas_association(email=self.email_1,
                                           username=self.username_1,
                                           fullname=self.fullname_1,
                                           cas_id=self.cas_id_1)
        try:
            user = services.cas_register(self.username_2,
                                         self.email_1,
                                         self.fullname_2,
                                         self.cas_id_1,
                                         "bio")
            self.assertEqual(user.username, self.username_1)
            self.assertEqual(user.full_name, self.fullname_1)
            self.assertNotEqual(user.bio, "bio")

        except exc.IntegrityError as e:
            self.fail(e.args[0])

        finally:
            self.delete_cas_association_and_associated_account(self.cas_id_1)
            self.clean_database(email=self.email_2, username=self.username_2)
            self.clean_database(email=self.email_1, username=self.username_2)
            self.clean_database(email=self.email_1, username=self.username_1)

    def test_cas_association_username_taken_cas_register(self):
        """
        Tests that when there is an auth_data with the cas_id of 
        the CAS account but username of CAS and Taiga are different and username
        of CAS is already used and emails are same it throws the good exception
        """
        self.init_user_and_cas_association(email=self.email_1,
                                           username=self.username_1,
                                           fullname=self.fullname_1,
                                           cas_id=self.cas_id_1)
        self.init_user_and_cas_association(email=self.email_2,
                                           username=self.username_2,
                                           fullname=self.fullname_2,
                                           cas_id=self.cas_id_2)
        try:
            services.cas_register(self.username_2,
                                  self.email_1,
                                  self.fullname_3,
                                  self.cas_id_1,
                                  "bio")
            self.fail(
                "User registered while he has CAs_id matching but" +
                " username is already taken by another user")
        except c_a_e.Username_Error :
            pass
        finally:
            self.delete_cas_association_and_associated_account(self.cas_id_1)
            self.delete_cas_association_and_associated_account(self.cas_id_2)

    def test__cas_association_same_username_not_email_true_cas_register(self):
        """
        Tests that when cas_id matches with an existing cas_auth
        and that the username is the same but that the email of the cas account 
        is different AND that the new email is free it overwrites it including 
        minor data (if CAS_OVERWRITE is true)
        """
        services.CAS_OVERWRITE = True
        self.init_user_and_cas_association(email=self.email_1,
                                           username=self.username_1,
                                           fullname=self.fullname_1,
                                           cas_id=self.cas_id_1)

        try:
            registered_user = services.cas_register(self.username_1,
                                                    self.email_2,
                                                    self.fullname_2,
                                                    self.cas_id_1,
                                                    "bio")
            self.assertEqual(registered_user.email, self.email_2)
            self.assertEqual(registered_user.full_name, self.fullname_2)
        except exc.IntegrityError as e:
            self.fail(e.args)

        finally:
            self.delete_cas_association_and_associated_account(self.cas_id_1)

    def test__cas_association_same_username_not_email_false_cas_register(self):
        """
        Tests that when cas_id matches with an existing cas_association
        and that the username is the same but that the email of the cas account 
        is different AND that the new email is free it does not overwrite it
        (if CAS_OVERWRITE is false)
        """
        services.CAS_OVERWRITE = False
        self.init_user_and_cas_association(email=self.email_1,
                                           username=self.username_1,
                                           fullname=self.fullname_1,
                                           cas_id=self.cas_id_1)

        try:
            registered_user = services.cas_register(self.username_1,
                                                    self.email_2,
                                                    self.fullname_2,
                                                    self.cas_id_1,
                                                    "bio")
            self.assertEqual(registered_user.email, self.email_1)
            self.assertEqual(registered_user.full_name, self.fullname_1)
            self.assertNotEqual(registered_user.bio, "bio")
        except exc.IntegrityError as e:
            self.fail(e.args)

        finally:
            self.delete_cas_association_and_associated_account(self.cas_id_1)

    def test_login_account_cas_association_taken_username_cas_register(self):
        """
        Tests that when cas_id matches with an existing auth_data and that the 
        username is the same but that the email of the cas account is 
        different AND that another Taiga account already used it,
        it throws the correct exception
        """

        self.clean_database(self.email_2, self.username_1)
        self.clean_database(self.email_1, self.username_2)
        self.init_user_and_cas_association(email=self.email_1,
                                           username=self.username_1,
                                           fullname=self.fullname_1,
                                           cas_id=self.cas_id_1)

        self.init_user_and_cas_association(email=self.email_2,
                                           username=self.username_2,
                                           fullname=self.fullname_2,
                                           cas_id=self.cas_id_2)
        try:
            services.cas_register(self.username_1,
                                  self.email_2,
                                  self.fullname_3,
                                  self.cas_id_1,
                                  "bio")
            self.fail(
                "User successfully registered with existing email")
        except c_a_e.Email_Error:
            pass
        finally:
            self.delete_cas_association_and_associated_account(self.cas_id_1)
            self.delete_cas_association_and_associated_account(self.cas_id_2)

    def test_login_account_cas_association_taken_email_true_cas_register(self):
        """
        Tests that when cas_id matches with an auth_data
        and that the username and the email of the CAS account matches with Taiga 
        account username and email it logs in and overwrites the other data
        (if CAS_OVERWRITE is true)
        """
        services.CAS_OVERWRITE = True
        self.init_user_and_cas_association(email=self.email_1,
                                           username=self.username_1,
                                           fullname=self.fullname_1,
                                           cas_id=self.cas_id_1)
        try:
            registered_user = services.cas_register(self.username_1,
                                                    self.email_1,
                                                    self.fullname_2,
                                                    self.cas_id_1,
                                                    "bio")
            auth_data = self.auth_data_model.objects.get(
                value=self.cas_id_1)
            auth_user = auth_data.user
            self.assertEqual(registered_user, auth_user)
        except exc.IntegrityError as e:
            self.fail(e)
        finally:
            self.delete_cas_association_and_associated_account(
                self.cas_id_1)
            self.clean_database(email=self.email_1, username=self.username_1,
                                cas_id=self.cas_id_1)

    def test_login_account_cas_association_taken_email_false_cas_register(
            self):
        """
        Tests that when cas_id matches with an auth_data
        and that the username and the email of the CAS account matches with 
        Taiga account username and email it logs in and does not overwrite the 
        other data (if CAS_OVERWRITE is false)

        """
        services.CAS_OVERWRITE = False
        self.init_user_and_cas_association(email=self.email_1,
                                           username=self.username_1,
                                           fullname=self.fullname_1,
                                           cas_id=self.cas_id_1)
        user_init = self.auth_data_model.objects.get(
            value=self.cas_id_1).user
        try:
            services.cas_register(self.username_1,
                                  self.email_1,
                                  self.fullname_2,
                                  self.cas_id_1,
                                  "bio")
            auth_data = self.auth_data_model.objects.get(
                value=self.cas_id_1)
            auth_user = auth_data.user
            self.assertEqual(user_init, auth_user)
        except exc.IntegrityError as e:
            self.fail(e)
        finally:
            self.delete_cas_association_and_associated_account(
                self.cas_id_1)
            self.clean_database(email=self.email_1, username=self.username_1,
                                cas_id=self.cas_id_1)


if __name__ == '__main__':
    unittest.main()
