import os
import json
import hashlib
import datetime
import nacl.secret
import dataclasses
import base64 as b64
from prettytable import PrettyTable


@dataclasses.dataclass
class PasswordEntry:
    """A dataclass that represents a single entry in the password database."""
    username: str = ""
    password: str = ""
    url: str = ""
    notes: str = ""
    
    @staticmethod
    def from_str(json_str: str):
        """Creates a new PasswordEntry from a json string."""
        # convert the json string to a dict and pass it to the constructor by unpacking all values returned
        return PasswordEntry(**json.loads(json_str))
    
    @staticmethod
    def from_entry(entry):
        """Creates a new PasswordEntry from another PasswordEntry."""
        return PasswordEntry(
            entry.username,
            entry.password,
            entry.url,
            entry.notes
        )
    
class PasswordDatabase:
    
    initialized = False
    
    menu_options = {
        "add_entry": "Add Entry",
        "remove_entry": "Remove Entry",
        "edit_entry": "Edit Entry",
        "list_entries": "List Entries",
        "search_entry": "Search Entries", 
        "save": "Save Database",
        "save_and_close": "Save and close Database",
        "close": "Close without saving the Database"
    }
    
    def encrypt(self, data: str):
        """Encrypts the given data"""
        return self.box.encrypt(data.encode("utf-8"))

    def decrypt(self, data: str):
        """Decrypts the given data"""
        return self.box.decrypt(data).decode("utf-8")
    
    def __init__(self, path: str, password: str) -> None:
        try:
            # append the .pwdb extension if it is not already there
            self.path = self.append_extension(path)
            # open the file in read binary mode
            self.handle = open(self.path, "rb")
            # create a secret box with the password hash
            self.box = nacl.secret.SecretBox(PasswordDatabase.create_hash(password))
            # decrypt the file and load the json
            self.content = json.loads(self.box.decrypt(self.handle.read()).decode("utf-8"))
            
            self.initialized = True
        except Exception as e:
            print("Exception handling:")
            print(e)
    
    def add_entry(self):
        """Adds a new entry to the database."""
        
        entry = PasswordEntry()
        
        entry.username = input("Enter the username:\n> ")
        entry.password = input("Enter the password:\n> ")
        entry.url = input("Enter the url:\n> ")
        entry.notes = input("Enter the notes:\n> ")
        
        encoded = b64.encodebytes( # convert to base64
            self.encrypt( # encrypt json string
                json.dumps( # convert dict to json string
                    dataclasses.asdict( # convert entry to dict
                        entry
                    )
                )
            )    
        ).decode("utf-8")
        self.content["entries"].append(encoded)
        
    def remove_entry(self):
        self.list_entries()
        index = int(input("Enter the index of the entry you want to remove:\n> "))
        del self.content["entries"][index]
        
    def edit_entry(self):
        self.list_entries()
        index = int(input("Enter the index of the entry you want to remove:\n> "))
        entry = PasswordEntry.from_str(
            self.decrypt(
                b64.decodebytes(self.content["entries"][index].encode("utf-8"))
            )
        )
        new_entry = PasswordEntry.from_entry(entry)
        print("Current entry:")
        
        while True:
            self.cls()
            table = PrettyTable()
            table.field_names = ["", "Username", "Password", "URL", "Notes"]
            table.add_row(["Old", entry.username, entry.password, entry.url, entry.notes], divider=True)
            table.add_row(["New", new_entry.username, new_entry.password, new_entry.url, new_entry.notes])
            print(table)
            
            print("What do you want to edit?")
            print("1: Username")
            print("2: Password")
            print("3: URL")
            print("4: Notes")
            print("5: Save and exit")
            print("6: Exit without saving")
            choice = int(input("> "))
            
            if choice == 1:
                new_entry.username = input("Enter the new username:\n> ")
            elif choice == 2:
                new_entry.password = input("Enter the new password:\n> ")
            elif choice == 3:
                new_entry.url = input("Enter the new url:\n> ")
            elif choice == 4:
                new_entry.notes = input("Enter the new notes:\n> ")
            elif choice == 5:
                entry = new_entry
                break
            elif choice == 6:
                break
            else:
                print("Unknown choice.")
                
        encoded = b64.encodebytes( # convert to base64
            self.encrypt( # encrypt json string
                json.dumps( # convert dict to json string
                    dataclasses.asdict( # convert entry to dict
                        entry
                    )
                )
            )    
        ).decode("utf-8")
        # overwrite the old entry with the new one
        self.content["entries"][index] = encoded
                
    def list_entries(self):
        """Lists all entries in the database."""
        
        if len(self.content.get("entries", [])) == 0:
            print("No entries found.")
            return
        
        table = PrettyTable()
        table.field_names = ["Index", "Username", "Password", "URL", "Notes"]
        for i, entry in enumerate(self.content["entries"]):
            # decode the entry from base64
            # decrypt the result
            # and create a PasswordEntry object from the decrypted result
            entry = PasswordEntry.from_str(
                self.decrypt(
                        b64.decodebytes(entry.encode("utf-8"))
                    )
                )
            # add the entry to the table
            table.add_row([i, entry.username, "*****", entry.url, entry.notes])
            
        print(table)
        
    def search_entry(self):
        """Searches for an entry in the database."""
        options = ["Username", "Password", "URL", "Notes"]
        print("What do you want to search for?")
        for i, option in enumerate(options):
            print(f"{i+1}: {option}")
        
        choice = int(input("> "))
        if choice > len(options):
            print("Unknown search option")
            return
        
        search = input("Enter the search term:\n> ")
        if len(search) == 0:
            print("Invalid search term")
            return
        
        found_entries = []

        for i, entry in enumerate(self.content["entries"]):
            entry = PasswordEntry.from_str(
                self.decrypt(
                        b64.decodebytes(entry.encode("utf-8"))
                    )
                )
            
            if search in (
                entry.username if choice == 1 else entry.password if choice == 2 else entry.url if choice == 3 else entry.notes if choice == 4 else ""
            ):
                found_entries.append(entry)
        
        if len(found_entries) == 0:
            print("No entries found.")
            
        table = PrettyTable()
        table.field_names = ["Index"] + options
        for i, entry in enumerate(found_entries):
            table.add_row([i, entry.username, entry.password, entry.url, entry.notes])

        print("Found the following entries:")
        print(table)

        
    def save_database(self):
        # encrypt the json
        encrypted = self.encrypt(json.dumps(self.content))
        
        # write the encrypted json to the file
        with open(self.path, "wb") as f:
            f.write(encrypted)
            print("Successfully saved the database.")
            
    def close_database(self):
        """Closes the database."""
        self.handle.close()       
                    
    def main(self):
        if not self.initialized:
            return False
        
        print(f"Current database: {self.path}")
        
        for index, option in enumerate(self.menu_options.values()):
            print(f"{index+1}: {option}")
            
        choice = list(self.menu_options.keys())[int(input("> "))-1]
        
        if choice == "add_entry":
            self.cls()
            self.add_entry()
        elif choice == "remove_entry":
            self.cls()
            self.remove_entry()
        elif choice == "edit_entry":
            self.cls()
            self.edit_entry()
        elif choice == "list_entries":
            self.cls()
            self.list_entries()
        elif choice == "search_entry":
            self.cls()
            self.search_entry()
        elif choice == "save": # save
            self.save_database()
        elif choice == "save_and_close": # save and close
            self.save_database()
            self.close_database()
            return False
        elif choice == "close": # close without saving
            self.close_database()
            return False    
        else:
            print("Unknown choice.")
        
        return True    
    
    def cls(self):
        os.system('cls' if os.name=='nt' else 'clear')
            
    ############################
    #      static methods      #
    ############################
            
    @staticmethod
    def append_extension(path):
        if not path.endswith(".pwdb"):
            return f"{path}.pwdb"
        return path
    
    @staticmethod
    def create(path: str, password: str):
        password_hash = PasswordDatabase.create_hash(password)

        print("Creating new password database with the following parameters:")
        print(f"Path: {path}")
        print(f"Password Hash: {password_hash.hex()}")
        box = nacl.secret.SecretBox(password_hash)
        
        if not os.path.exists(path):
            with open(f"{path}.pwdb", "wb") as f:
                f.write(
                    box.encrypt(
                        json.dumps({
                            "created": datetime.datetime.now().isoformat(),   
                            "version": "1.0.0",
                            "entries": [],
                        })
                .encode()))

    @staticmethod
    def create_hash(password: str):
        return hashlib.sha256(password.encode()).digest()
