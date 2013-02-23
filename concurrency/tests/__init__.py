from concurrency.tests.all import *
from concurrency.tests.contrib_admin import *
from concurrency.tests.forms import *
from concurrency.tests.middleware import *
from concurrency.tests.conf import *
from concurrency.tests.api import * #NOQA

try:
    from concurrency.tests.south_test import *
except ImportError:
    pass


