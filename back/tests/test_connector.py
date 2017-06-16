import unittest
import sys
from taiga_contrib_cas_auth import connector
from collections import namedtuple

sys.path.insert(0, "/srv/taiga")


class TestConnector(unittest.TestCase):
    """
     Test connector.py
    """
    jtest_data = (
        'jtest', {'uid': 'j.test', 'civilite': '31', 'firstName': 'Jean',
                  'lastName': 'Test', 'login': 'jean.test',
                  'telephone': '0501020304', 'authLevel': '10',
                  'lieuExercice': '', 'ville': 'Bordeaux',
                  'loginTime': '1493726831127', 'authDomain': 'ad',
                  'authDomainLabel': 'NomdeDomaine',
                  'authMode': 'CLASSIC',
                  'remoteAddress': '1.2.3.4',
                  'titreLib': 'Monsieur', 'cp': '33000',
                  'professionAutre': 'Developer', 'adresse1': '1 rue Tête',
                  'fullName': 'Jean TEST',
                  'emailPerso': 'jean.test@yopmail.com'}, None)
    User = namedtuple("User",
                      ["id", "username", "full_name", "bio", "email"])

    def test_non_configured_CAS_FIELD_success_make_user(self):
        """
        tests that when CAS_FIELD is not configured (but defined) make_user 
        is working 
        """
        connector.CAS_FIELD = {}
        self.assertTrue(
            connector.make_user(self.jtest_data) == self.User(id='',
                                                              username='jtest',
                                                              full_name='',
                                                              bio='',
                                                              email=''))

    def test_CAS_FIELD_configured_success_make_user(self):
        """
        tests that when CAS_FIELD is correctly configured make_user is working
        """
        user = self.User(id='j.test',
                         username='jtest',
                         full_name='Jean TEST',
                         bio='',
                         email='jean.test@yopmail.com')
        self.assertTrue(
            connector.make_user(self.jtest_data) == user)

    def test_fail_make_user(self):
        """
        tests that make_user raise the correct error when the type of data is 
        not correct
        """
        self.assertRaises(IndexError, connector.make_user, "")
        self.assertRaises(IndexError, connector.make_user, " ")


if __name__ == '__main__':
    unittest.main()
