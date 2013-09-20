from concurrency.tests.test_all import *  # NOQA
from concurrency.tests.test_forms import WidgetTest, FormFieldTest, ConcurrentFormTest  # NOQA
from concurrency.tests.test_middleware import ConcurrencyMiddlewareTest, TestFullStack  # NOQA
from concurrency.tests.test_conf import SettingsTest  # NOQA
from concurrency.tests.test_api import ConcurrencyTestApi  # NOQA
from concurrency.tests.test_policy import TestPolicy  # NOQA

from concurrency.tests.test_admin_edit import TestAdminEdit, TestConcurrentModelAdmin  # NOQA
from concurrency.tests.test_admin_list_editable import TestListEditable, TestListEditableWithNoActions  # NOQA
from concurrency.tests.test_admin_actions import TestAdminActions  # NOQA
from concurrency.tests.test_issues import *  # NOQA
from concurrency.tests.test_south import *  # NOQA
