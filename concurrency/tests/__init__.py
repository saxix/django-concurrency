from .all import *
from .contrib_admin import TestDjangoAdmin
from .forms import *


try:
    import south
    from .south_test import *
except ImportError:
    pass
