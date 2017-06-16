from taiga.base import exceptions as exc
from django.core.exceptions import ObjectDoesNotExist

class CAS_CREATE_Error(exc.PermissionDenied):
    pass

class CAS_Bind_Error(exc.PermissionDenied):
    pass

class No_Match_Error (exc.IntegrityError):
    pass

class Email_Error(exc.IntegrityError):
    pass

class Username_Error (exc.IntegrityError):
    pass

class Username_No_Email_Error (exc.IntegrityError):
    pass

class Email_No_Username_Error (exc.IntegrityError):
    pass

class Username_Email_Diff_Account_Error (exc.IntegrityError):
    pass
