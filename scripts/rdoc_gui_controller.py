"""
RenderDoc GUI Controller & Desktop Automation Script
Controls RenderDoc Desktop UI via Win32 API to attach to running Android processes.
"""
import ctypes
import ctypes.wintypes
import time
from PIL import Image
import struct

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def init_desktop():
    hDesk = user32.OpenDesktopW("default", 0, False, 0x01FF)
    user32.SetThreadDesktop(hDesk)
    return hDesk

def find_renderdoc_hwnd():
    target_hwnd = None
    def enum_desk_windows(hwnd, extra):
        nonlocal target_hwnd
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if "RenderDoc v1.47" in buf.value:
            target_hwnd = hwnd
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    hDesk = user32.OpenDesktopW("default", 0, False, 0x01FF)
    user32.EnumDesktopWindows(hDesk, WNDENUMPROC(enum_desk_windows), 0)
    return target_hwnd

def capture_window(hwnd, output_path):
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    if w <= 0 or h <= 0:
        return False

    hdc_window = user32.GetWindowDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_window)
    hbm = gdi32.CreateCompatibleBitmap(hdc_window, w, h)
    gdi32.SelectObject(hdc_mem, hbm)

    res = user32.PrintWindow(hwnd, hdc_mem, 2)
    if not res:
        res = user32.PrintWindow(hwnd, hdc_mem, 0)

    bmpinfo = ctypes.create_string_buffer(40)
    bmpinfo[0:4] = struct.pack('<I', 40)
    bmpinfo[4:8] = struct.pack('<i', w)
    bmpinfo[8:12] = struct.pack('<i', -h)
    bmpinfo[12:14] = struct.pack('<H', 1)
    bmpinfo[14:16] = struct.pack('<H', 32)
    bmpinfo[16:20] = struct.pack('<I', 0)

    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(hdc_mem, hbm, 0, h, buf, bmpinfo, 0)

    im = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1)
    im.save(output_path)

    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc_window)
    return True

if __name__ == "__main__":
    init_desktop()
    hwnd = find_renderdoc_hwnd()
    print("RenderDoc HWND:", hex(hwnd) if hwnd else "Not found")
    if hwnd:
        capture_window(hwnd, "renderdoc_status.png")
        print("Captured RenderDoc window to renderdoc_status.png")
