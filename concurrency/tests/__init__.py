from concurrency.tests.all import *  # NOQA
from concurrency.tests.contrib_admin import *  # NOQA
from concurrency.tests.forms import *  # NOQA
from concurrency.tests.middleware import *  # NOQA
from concurrency.tests.conf import *  # NOQA
from concurrency.tests.api import *  # NOQA
from concurrency.tests.test_admin import *  # NOQA

try:
    from concurrency.tests.south_test import *  # NOQA
except ImportError:
    pass
