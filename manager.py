import os
import json
import getpass
import hashlib
import datetime

from entry import PasswordDatabase

class PasswordManager:
    
    database: PasswordDatabase = None
    
    menu_options = {
        "open_database": "Open Database",
        "create_new_database": "Create New Database",
        "exit": "Exit"
    }
    
    def __init__(self) -> None:
        pass
    
    def main(self):
        """The main function of the password manager. This handles the input choices and calls the appropriate functions.

        Returns:
            bool: True if the user wants to continue, False if they want to exit
        """
        
        if self.database:
            # we have a database open, so run its main loop
            if not self.database.main():
                # the user wants to exit the database
                self.database = None
                self.cls()
            else:
                return True
        
        for index, option in enumerate(self.menu_options.values()):
            print(f"{index+1}: {option}")
            
        choice = list(self.menu_options.keys())[int(input("> "))-1]
        
        if choice == "open_database":
            path = input("Enter the path/file name to/of the password database:\n> ")
            self.database = self.open_database(path)
            self.cls()
        elif choice == "create_new_database":
            self.database = self.create_database()
        elif choice == "exit":
            return False
        else:
            print("Unknown choice.")
            
        return True
    
    def open_database(self, path: str, password: str = None):
        """Opens a password database.

        Args:
            path (str): The path to the password database
        """
        if not password:
            password = getpass.getpass("Enter the encryption password for the database:\n> ")
        
        return PasswordDatabase(path, password)
    
    def create_database(self):
        """Creates and opens a new password database."""
        
        database_name = input("Enter the name of the new database file:\n> ")
        database_password = getpass.getpass("Enter the encryption password for the database:\n> ")
        
        PasswordDatabase.create(database_name, database_password)
        return self.open_database(database_name, database_password)
    
    def cls(self):
        os.system('cls' if os.name=='nt' else 'clear')
        
        