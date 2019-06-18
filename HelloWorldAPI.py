import ctypes

U_Handle = ctypes.WinDLL("User32.dll") #Handle to User32.dll
K_Handle = ctypes.WinDLL("Kernel32.dll") #Handle to Kernal32.dll

HWND = None #Handle to the owner window of the message box to be created. If this parameter is NULL, the message box has no owner window.
LpText = "Hellow World" #Message displayed LPCWSTR
LpCaption = "Monka" #Dialog box title LPCWSTR
uType = 0x00000001 #MB_OKCANCEL Value

response = U_Handle.MessageBoxW(HWND, LpText, LpCaption, uType)
error = K_Handle.GetLastError()
if error !=0:
    print("Error code: {0}".format(error))
    exit(1)

if response == 1:
    print("User clicked OK")
elif response == 2:
    print("User click Cancel")