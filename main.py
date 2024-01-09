import time
from manager import PasswordManager

if __name__ == "__main__":
    
    manager = PasswordManager()
    
    # run the password manager until the user chose exit
    while manager.main():
        time.sleep(0.5)