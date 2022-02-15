import os
import time

os.environ["TERM"] = "xterm"

os.system("clear")
print("[*] Type exit/quit/q to exit room")
print("\n")
print("main >")
time.sleep(2)
print("\033[s" + chr(27) + "[2A\u001B[L\rOutput\033[2B\033[u")
time.sleep(2)
print("\033[s" + chr(27) + "[2A\u001B[S\u001B[L\rOutput\033[2B\033[u")