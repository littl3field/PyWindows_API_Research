import ctypes

k_handle = ctypes.WinDLL("Kernel32.dll")
u_handle = ctypes.WinDLL("User32.dll")

PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)

# Token Access Rights
STANDARD_RIGHTS_REQUIRED = 0x000F0000
STANDARD_RIGHTS_READ = 0x00020000
TOKEN_ASSIGN_PRIMARY = 0x0001
TOKEN_DUPLICATE = 0x0002
TOKEN_IMPERSONATION = 0x0004
TOKEN_QUERY = 0x0008
TOKEN_QUERY_SOURCE = 0x0010
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_ADJUST_GROUPS = 0x0040
TOKEN_ADJUST_DEFAULT = 0x0080
TOKEN_ADJUST_SESSIONID = 0x0100
TOKEN_READ = (STANDARD_RIGHTS_READ | TOKEN_QUERY)
TOKEN_ALL_ACCESS = (STANDARD_RIGHTS_REQUIRED |
					TOKEN_ASSIGN_PRIMARY     |
					TOKEN_DUPLICATE          |
					TOKEN_IMPERSONATION      |
					TOKEN_QUERY              |
					TOKEN_QUERY_SOURCE       |
					TOKEN_ADJUST_PRIVILEGES  |
					TOKEN_ADJUST_GROUPS      |
					TOKEN_ADJUST_DEFAULT     |
					TOKEN_ADJUST_SESSIONID)

LpWindowName = ctypes.c_char_p(input("Enter Process Name to Hook Into: ").encode('UTF-8'))

hWnd = u_handle.FindWindowA(None, LpWindowName)

if hWnd == 0:
    print("[ERROR] Code: {0} - Could Not Grab Handle".format(k_handle.GetLastError()))
    exit(1)
else:
    print("[INFO] Got Handle...")

lpdwProcessId = ctypes.c_ulong()
response = u_handle.GetWindowThreadProcessId(hWnd, ctypes.byref(lpdwProcessId))
if response == 0:
    print("[ERROR] Code: {0} - Could Not Grab PID".format(k_handle.GetLastError()))
    exit(1)
else:
    print("[INFO] Found the PID... ")

#Open process by PID with Specific Access
dwDesiredAccess = PROCESS_ALL_ACCESS
bInheritHandle = False
dwProcessId = lpdwProcessId

# Calling the Windows API calls to open the process
hProcess = k_handle.OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId)

# Check to see if we have a valid handle to the process
if hProcess <= 0:
    print("[ERROR] Code: {0} - Could Not Grab Priv Handle".format(k_handle.GetLastError()))
else:
    print("[INFO] Opened Priv Handle...")

ProcessHandle = hProcess
DesiredAccess = TOKEN_ALL_ACCESS
TokenHandle = ctypes.c_void_p()
response = k_handle.OpenProcessToken(ProcessHandle, DesiredAccess, ctypes.byref(TokenHandle))

if response > 0:
    print("[INFO] Got Handle...")
else:
    print("[ERROR] Code: {0} - Could Not Grab Priv Token Handle".format(k_handle.GetLastError()))
