import ctypes
from ctypes.wintypes import DWORD

k_handle = ctypes.WinDLL("Kernel32.dll")
u_handle = ctypes.WinDLL("User32.dll")
a_handle = ctypes.WinDLL("Advapi32.dll")

# Access Rights
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
                    TOKEN_ASSIGN_PRIMARY |
                    TOKEN_DUPLICATE |
                    TOKEN_IMPERSONATION |
                    TOKEN_QUERY |
                    TOKEN_QUERY_SOURCE |
                    TOKEN_ADJUST_PRIVILEGES |
                    TOKEN_ADJUST_GROUPS |
                    TOKEN_ADJUST_DEFAULT |
                    TOKEN_ADJUST_SESSIONID)

SE_PRIVILEGE_ENABLED = 0x00000002
SE_PRIVILEGE_DISABLED = 0x00000000

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
        ("PrivilegeCount", DWORD),
        ("Control", DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES),
    ]


class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [
        ("PrivilegeCount", DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES),
    ]


lpWindowName = ctypes.c_char_p(input("Enter Window Name To Hook Into: ").encode('utf-8'))

hWnd = u_handle.FindWindowA(None, lpWindowName)

if hWnd == 0:
    print("[ERROR] Could Not Grab Handle! Error Code: {0}".format(k_handle.GetLastError()))
    exit(1)
else:
    print("[INFO] Grabbed Handle...")

lpdwProcessId = ctypes.c_ulong()

response = u_handle.GetWindowThreadProcessId(hWnd, ctypes.byref(lpdwProcessId))

if response == 0:
    print("[ERROR] Could Not Get PID from Handle! Error Code: {0}".format(k_handle.GetLastError()))
else:
    print("[INFO] Found PID...")

dwDesiredAccess = PROCESS_ALL_ACCESS
bInheritHandle = False
dwProcessId = lpdwProcessId

hProcess = k_handle.OpenProcess(dwDesiredAccess, bInheritHandle, dwProcessId)

if hProcess <= 0:
    print("[ERROR] Could Not Grab Privileged Handle! Error Code: {0}".format(k_handle.GetLastError()))
else:
    print("[INFO] Privileged Handle Opened...")

ProcessHandle = hProcess
DesiredAccess = TOKEN_ALL_ACCESS
TokenHandle = ctypes.c_void_p()

response = k_handle.OpenProcessToken(ProcessHandle, DesiredAccess, ctypes.byref(TokenHandle))

if response > 0:
    print("[INFO] Handle to Process Token Created! Token: {0}".format(TokenHandle))
else:
    print("[ERROR] Could Not Grab Privileged Handle to Token! Error Code: {0}".format(k_handle.GetLastError()))

requiredPrivileges = PRIVILEGE_SET()
requiredPrivileges.PrivilegeCount = 1  
requiredPrivileges.Privileges = LUID_AND_ATTRIBUTES() 
requiredPrivileges.Privileges.Luid = LUID()  

lpSystemName = None
lpName = "SEDebugPrivilege"

response = a_handle.LookupPrivilegeValueW(lpSystemName, lpName, ctypes.byref(requiredPrivileges.Privileges.Luid))

if response > 0:
    print("[INFO] Lookup For SEDebugPrivilege Worked...")
else:
    print("[ERROR] Lookup for SEDebugPrivilege Failed! Error Code: {0}".format(k_handle.GetLastError()))

pfResult = ctypes.c_long()

response = a_handle.PrivilegeCheck(TokenHandle, ctypes.byref(requiredPrivileges), ctypes.byref(pfResult))

if response > 0:
    print("[INFO] PrivilegeCheck Worked...")
else:
    print("[ERROR] PrivilegeCheck Failed! Error Code: {0}".format(k_handle.GetLastError()))

if pfResult:
    print("[INFO] Privilege SEDebugPrivilege is Enabled...")
    requiredPrivileges.Privileges.Attributes = SE_PRIVILEGE_DISABLED  
else:
    print("[INFO] Privilege SEDebugPrivilege is NOT Enabled...")
    requiredPrivileges.Privileges.Attributes = SE_PRIVILEGE_ENABLED 

DisableAllPrivileges = False
NewState = TOKEN_PRIVILEGES()
BufferLength = ctypes.sizeof(NewState)
PreviousState = ctypes.c_void_p()
ReturnLength = ctypes.c_void_p()

NewState.PrivilegeCount = 1;
NewState.Privileges = requiredPrivileges.Privileges 

response = a_handle.AdjustTokenPrivileges(
    TokenHandle,
    DisableAllPrivileges,
    ctypes.byref(NewState),
    BufferLength,
    ctypes.byref(PreviousState),
    ctypes.byref(ReturnLength))

if response > 0:
    print("[INFO] AdjustTokenPrivileges Flipped Privilege...")
else:
    print("[ERROR] AdjustTokenPrivileges Failed! Error Code: {0}".format(k_handle.GetLastError()))
