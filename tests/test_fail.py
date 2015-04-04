import pytest


@pytest.mark.xfail
def test_configuration_not_supported():
    """ dummy test to improve Tox responses on not supported configurations
    ie. python3 with django 1.4
    """
    assert False
