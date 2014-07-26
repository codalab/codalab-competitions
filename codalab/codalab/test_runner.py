import warnings
import exceptions

from django_nose import NoseTestSuiteRunner


class CodalabTestRunner(NoseTestSuiteRunner):

    def __init__(self, *args, **kwargs):
        warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning, module='django.db.models.fields', lineno=827)
        super(CodalabTestRunner, self).__init__(*args, **kwargs)
