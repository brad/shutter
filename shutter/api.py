import ctypes

from .constants import GP_VERSION_SHORT, GP_VERSION_VERBOSE
from .errors import ShutterError


libgphoto2dll = ctypes.util.find_library('gphoto2')
gp = ctypes.CDLL(libgphoto2dll)
gp.gp_context_new.restype = ctypes.POINTER(ctypes.c_char)
PTR = ctypes.pointer


def gp_library_version(verbose=True):
    gp.gp_library_version.restype = ctypes.POINTER(ctypes.c_char_p)
    if not verbose:
        arr_text = gp.gp_library_version(GP_VERSION_SHORT)
    else:
        arr_text = gp.gp_library_version(GP_VERSION_VERBOSE)

    v = ''
    for s in arr_text:
        if s is None:
            break
        v += '%s\n' % s.decode('utf8')
    return v


def check(result):
    if result < 0:
        gp.gp_result_as_string.restype = ctypes.c_char_p
        message = gp.gp_result_as_string(result)
        raise ShutterError(result, message)
    return result


def check_unref(result, camfile):
    if result != 0:
        gp.gp_file_unref(camfile.pointer)
        gp.gp_result_as_string.restype = ctypes.c_char_p
        message = gp.gp_result_as_string(result)
        raise ShutterError(result, message)
