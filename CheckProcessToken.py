import ctypes
from ctypes.wintypes import DWORD

# Grab a handle to kernel32.dll & USer32.dll
k_handle = ctypes.WinDLL("Kernel32.dll")
u_handle = ctypes.WinDLL("User32.dll")
a_handle = ctypes.WinDLL("Advapi32.dll")

# Access Rights
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)

SE_PRIVILEGE_ENABLED = 0x00000002
SE_PRIVILEGE_DISABLED = 0x00000000

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
                    TOKEN_ASSIGN_PRIMARY |
                    TOKEN_DUPLICATE |
                    TOKEN_IMPERSONATION |
                    TOKEN_QUERY |
                    TOKEN_QUERY_SOURCE |
                    TOKEN_ADJUST_PRIVILEGES |
                    TOKEN_ADJUST_GROUPS |
                    TOKEN_ADJUST_DEFAULT |
                    TOKEN_ADJUST_SESSIONID)

class LUID(ctypes.Structure):
    _fields_ = [
        ("LowPart", DWORD),
        ("HighPart", DWORD),
    ]

class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Luid", LUID),
        ("Attributes", DWORD),
    ]

class PRIVILEGE_SET(ctypes.Structure):
    _fields_ = [
        ("PriviledgedCount", DWORD),
        ("Control", DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES)
    ]

# Grab The Windows Name from User32
lpWindowName = ctypes.c_char_p(input("Enter Window Name To Hook Into: ").encode('utf-8'))

# Grab a Handle to the Process
hWnd = u_handle.FindWindowA(None, lpWindowName)

# Check to see if we have the Handle
if hWnd == 0:
    print("[ERROR] Could Not Grab Handle! Error Code: {0}".format(k_handle.GetLastError()))
    exit(1)
else:
    print("[INFO] Grabbed Handle...")

# Get the PID of the process at the handle
lpdwProcessId = ctypes.c_ulong()

# We use byref to pass a pointer to the value as needed by the API Call
response = u_handle.GetWindowThreadProcessId(hWnd, ctypes.byref(lpdwProcessId))

# Check to see if the call Completed
if response == 0:
    print("[ERROR] Could Not Get PID from Handle! Error Code: {0}".format(k_handle.GetLastError()))
else:
    print("[INFO] Found PID...")

# Opening the Process by PID with Specific Access
dwDesiredAccess = PROCESS_ALL_ACCESS
bInheritHandle = False
dwProcessId = lpdwProcessId

# Calling the Windows API Call to Open the Process
hProcess = k_handle.OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId)

# Check to see if we have a valid Handle to the process
if hProcess <= 0:
    print("[ERROR] Could Not Grab Privileged Handle! Error Code: {0}".format(k_handle.GetLastError()))
else:
    print("[INFO] Privileged Handle Opened...")

# Open a Handle to the Process's Token Directly
ProcessHandle = hProcess
DesiredAccess = TOKEN_ALL_ACCESS
TokenHandle = ctypes.c_void_p()

# Issue the API Call
response = k_handle.OpenProcessToken(ProcessHandle, DesiredAccess, ctypes.byref(TokenHandle))

# Handle an Error
if response > 0:
    print("[INFO] Handle to Process Token Created! Token: {0}".format(TokenHandle))
else:
    print("[ERROR] Could Not Grab Privileged Handle to Token! Error Code: {0}".format(k_handle.GetLastError()))

lpSystemName = None
lpName = "SeDebugPrivilege"
lpLuid = LUID()

response = a_handle.LookupPrivilegeValueW(lpSystemName, lpName, ctypes.byref(lpLuid))

if response > 0:
    print("[INFO] LUID Found")
else:
    print("[ERROR] Could Not Grab LUID! Error Code: {0}".format(k_handle.GetLastError()))

print("[INFO] LUID High: {0} LUID Low: {1}".format(lpLuid.HighPart, lpLuid.LowPart))

requiredPrivileges = PRIVILEGE_SET()
requiredPrivileges.PrivilegeCount = 1
requiredPrivileges.Privileges = LUID_AND_ATTRIBUTES()
requiredPrivileges.Privileges.LUID = lpLuid
requiredPrivileges.Privileges.Attributes = SE_PRIVILEGE_ENABLED

pfResult = ctypes.c_long()

response = a_handle.PrivilegeCheck(TokenHandle, ctypes.byref(requiredPrivileges), ctypes.byref(pfResult))

if response > 0:
    print("[INFO] Ran Privilege Check")
else:
    print("[ERROR] Could not run Privilege check! Error code: {0}".format(k_handle.GetLastError()))

if pfResult:
    print("[INFO] Privilege enabled {0}".format(lpName))
else:
    print("[INFO] Privilege not enabled {0}".format(lpName))
