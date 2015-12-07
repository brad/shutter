import envoy
import unittest

from mock import patch
from nose.tools import eq_

from shutter.api import gp_library_version
from shutter.constants import GP_VERSION_SHORT, GP_VERSION_VERBOSE


class TestAPI(unittest.TestCase):
    def setUp(self):
        res = envoy.run('gphoto2 -v')
        line = [line for line in res.std_out.split('\n')
                if line.startswith('libgphoto2 ')][0]
        self.version_arr = [val.replace(',', '') for val in
                            list(filter(None, line.split(' ')))][1:]

    def test_library_version(self):
        assert gp_library_version().startswith(self.version_arr[0])
        eq_(gp_library_version(verbose=False).replace('\n', ' ').strip(),
            ' '.join(self.version_arr))

        with patch('shutter.api.gp.gp_library_version') as mock_version:
            mock_version.return_value = []
            eq_(gp_library_version(), '')
            eq_(gp_library_version(verbose=False), '')
            mock_version.assert_any_call(GP_VERSION_SHORT)
            mock_version.assert_any_call(GP_VERSION_VERBOSE)
