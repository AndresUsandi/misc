import os
import sys
from pathlib import Path
from typing import List, Tuple, Union


CCH_RM_SESSION_KEY: int = 32
CCH_RM_MAX_APP_NAME: int = 255
CCH_RM_MAX_SVC_NAME: int = 63

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    class RM_UNIQUE_PROCESS(ctypes.Structure):
        _fields_ = [
            ("dwProcessId", wintypes.DWORD),
            ("ProcessStartTime", wintypes.FILETIME),
        ]

    class RM_PROCESS_INFO(ctypes.Structure):
        _fields_ = [
            ("Process", RM_UNIQUE_PROCESS),
            ("strAppName", wintypes.WCHAR * (CCH_RM_MAX_APP_NAME + 1)),
            ("strServiceShortName", wintypes.WCHAR * (CCH_RM_MAX_SVC_NAME + 1)),
            ("ApplicationType", ctypes.c_int),
            ("AppStatus", wintypes.ULONG),
            ("TSSessionId", wintypes.DWORD),
            ("bRestartable", wintypes.BOOL),
        ]

def get_locking_processes(file_path: Union[str, Path]) -> List[Tuple[int, str]]:
    """
    Uses Windows Restart Manager API (rstrtmgr.dll) to inspect which processes currently hold a lock on file_path.
    Returns a list of (pid, app_name) tuples.
    """
    if sys.platform != "win32":
        return []

    try:
        rstrtmgr = ctypes.windll.rstrtmgr
    except Exception:
        return []

    abs_path = os.path.abspath(str(file_path))
    if not os.path.exists(abs_path):
        return []

    session_handle = wintypes.DWORD()
    session_key = (wintypes.WCHAR * (CCH_RM_SESSION_KEY + 1))()

    res = rstrtmgr.RmStartSession(ctypes.byref(session_handle), 0, session_key)
    if res != 0:
        return []

    try:
        path_arr = (wintypes.LPCWSTR * 1)(abs_path)
        res = rstrtmgr.RmRegisterResources(session_handle, 1, path_arr, 0, None, 0, None)
        if res != 0:
            return []

        proc_info_needed = wintypes.UINT(0)
        proc_info_count = wintypes.UINT(0)
        reboot_reasons = wintypes.DWORD()

        res = rstrtmgr.RmGetList(session_handle, ctypes.byref(proc_info_needed), ctypes.byref(proc_info_count), None, ctypes.byref(reboot_reasons))
        if res not in (0, 234) or proc_info_needed.value == 0:
            return []

        proc_info_count.value = proc_info_needed.value
        proc_info_array = (RM_PROCESS_INFO * proc_info_needed.value)()

        res = rstrtmgr.RmGetList(session_handle, ctypes.byref(proc_info_needed), ctypes.byref(proc_info_count), proc_info_array, ctypes.byref(reboot_reasons))
        if res != 0:
            return []

        results = []
        for i in range(proc_info_count.value):
            results.append((int(proc_info_array[i].Process.dwProcessId), str(proc_info_array[i].strAppName)))
        return results
    except Exception:
        return []
    finally:
        rstrtmgr.RmEndSession(session_handle)