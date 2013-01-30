from concurrency.tests.all import *
from concurrency.tests.contrib_admin import TestDjangoAdmin
from concurrency.tests.forms import *


try:
    from concurrency.tests.south_test import *
except ImportError:
    pass
