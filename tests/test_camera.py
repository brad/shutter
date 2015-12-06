import re
import unittest

from mock import patch
from nose.tools import eq_

from shutter import Camera
from shutter.api import PTR
from shutter.errors import ShutterError
from shutter.shutter import context


def gp_list_get_name(camera, index, name_ptr):
    names = ['Other camera', 'Canon Camera']
    name_ptr.contents.value = names[index].encode('utf8')
    return 0


def gp_list_get_value(camera, index, value_ptr):
    values = ['usb:001,098', 'usb:021,098']
    value_ptr.contents.value = values[index].encode('utf8')
    return 0


def gp_camera_get_about(camera, txt_ptr, context):
    txt_ptr.contents.text = 'About FAKE camera'.encode('utf8')
    return 0


def gp_camera_get_summary(camera, txt_ptr, context):
    txt_ptr.contents.text = 'X\nfirst: FAKE1\nsecond: FAKE2'.encode('utf8')
    return 0


class TestCamera(unittest.TestCase):

    @patch('shutter.api.gp.gp_camera_init')
    @patch('shutter.api.gp.gp_list_count')
    @patch('shutter.api.gp.gp_list_get_name', side_effect=gp_list_get_name)
    @patch('shutter.api.gp.gp_list_get_value', side_effect=gp_list_get_value)
    @patch('shutter.api.gp.gp_abilities_list_lookup_model')
    def test_init(self, mock_lookup, mock_value, mock_name, mock_count, mock_init):
        mock_init.return_value = 0
        camera = Camera()
        eq_(camera.pointer, camera._ptr)
        mock_init.assert_called_once_with(camera._ptr, context)
        eq_(mock_lookup.call_count, 0)
        eq_(mock_value.call_count, 0)
        eq_(mock_name.call_count, 0)
        eq_(mock_count.call_count, 0)

        mock_lookup.return_value = 0
        mock_count.return_value = 2
        camera = Camera(re.compile('canon'))
        eq_(mock_init.call_count, 2)
        eq_(mock_lookup.call_count, 1)
        pointer_arg = mock_lookup.call_args[0][0]
        mock_lookup.assert_called_once_with(pointer_arg, 'Canon Camera')
        eq_(mock_value.call_count, 2)
        eq_(mock_name.call_count, 2)
        for i in range(2):
            value_call = mock_value.call_args_list[i][0]
            mock_value.assert_any_call(value_call[0], i, value_call[2])
            name_call = mock_name.call_args_list[i][0]
            mock_name.assert_any_call(name_call[0], i, name_call[2])
        eq_(mock_count.call_count, 1)
        mock_count.assert_called_once_with(mock_count.call_args[0][0])

        mock_init.return_value = -60
        self.assertRaises(ShutterError, Camera)
        eq_(mock_init.call_count, 3)
        eq_(mock_lookup.call_count, 1)
        eq_(mock_value.call_count, 2)
        eq_(mock_name.call_count, 2)
        eq_(mock_count.call_count, 1)

    @patch('shutter.api.gp.gp_camera_init')
    @patch('shutter.api.gp.gp_camera_get_about', side_effect=gp_camera_get_about)
    def test_about(self, mock_about, mock_init):
        mock_init.return_value = 0
        camera = Camera()
        eq_(camera.pointer, camera._ptr)
        eq_(camera.about, 'About FAKE camera')
        eq_(mock_about.call_count, 1)
        text_arg = mock_about.call_args[0][1]
        mock_about.assert_called_once_with(camera._ptr, text_arg, context)

    @patch('shutter.api.gp.gp_camera_init')
    @patch('shutter.api.gp.gp_camera_get_summary', side_effect=gp_camera_get_summary)
    def test_summary(self, mock_summary, mock_init):
        mock_init.return_value = 0
        camera = Camera()
        eq_(camera.pointer, camera._ptr)
        eq_(sorted(camera.summary.items()),
            sorted({'first': 'FAKE1', 'second': 'FAKE2'}.items()))
        eq_(mock_summary.call_count, 1)
        text_arg = mock_summary.call_args[0][1]
        mock_summary.assert_called_once_with(camera._ptr, text_arg, context)
