import ctypes

k_handle = ctypes.WinDLL("Kernel32.dll")
u_handle = ctypes.WinDLL("User32.dll")

PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)

LpWindowName = ctypes.c_char_p(input("Enter Window Name To Kill: ").encode('UTF-8'))
hWnd = u_handle.FindWindowA(None, LpWindowName)
if hWnd == 0:
    print("Error Code: {0} - Could Not Grab Handle".format(k_handle.GetLastError()))
    exit(1)
else:
    print("Got Handle...")

lpdwProcessId = ctypes.c_ulong()
response = u_handle.GetWindowThreadProcessId(hWnd, ctypes.byref(lpdwProcessId))
if response == 0:
    print("Error Code: {0} - Could Not Grab PID".format(k_handle.GetLastError()))
    exit(1)
else:
    print("Got the PID... ")

dwDesiredAccess = PROCESS_ALL_ACCESS
bInheritHandle = False
lpdwProcessId = lpdwProcessId
hProcess = k_handle.OpenProcess(dwDesiredAccess, bInheritHandle, lpdwProcessId)
if hProcess <= 0:
    print("Error Code: {0} - Could Not Grab Priv Handle".format(k_handle.GetLastError()))
else:
    print("Got Priv Handle...")

uExitCode = 0x1
response = k_handle.TerminateProcess(hProcess, uExitCode)
if response == 0:
    print("Error Code: {0} - Could Not terminate process".format(k_handle.GetLastError()))
else:
    print("...Process Terminated")