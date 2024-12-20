"""Module for servants implementations."""

from typing import List
import os
import json
import uuid as UD

import Ice
import IceDrive

from icedrive_directory.discovery import Discovery
from icedrive_directory.delayed_response import DirectoryQueryResponse
from icedrive_directory.delayed_response import DirectoryQuery


class Directory(IceDrive.Directory):
    """Implementation of the IceDrive.Directory interface."""
    def __init__(self, name, user: IceDrive.UserPrx, parent=None):
        """Create the Directory"""
        self.name = name
        self.userObj = user
        self.user = self.userObj.getUsername()
        self.parent = parent
        self.childs = {}
        self.files = {}
        self.dataDir = "./USRDIRS/"
        self.discovery = Discovery()  # Create the discovery object

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to the parent directory, if it exists. None in other case."""
        if self.userObj.isAlive():
            if self.parent is not None:
                print(f'Parent of {self.name} requested: {self.parent}')
                proxy = current.adapter.addWithUUID(self.parent)
                return IceDrive.DirectoryPrx.uncheckedCast(proxy)
            raise IceDrive.RootHasNoParent()
        else:
            raise IceDrive.Unauthorized(self.user)

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        """Return a list of names of the directories contained in the directory."""
        if self.userObj.isAlive():
            print(f'List of childs of {self.name} requested: {self.childs.keys()}')
            return list(self.childs.keys())
        else:
            raise IceDrive.Unauthorized(self.user)

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to one specific directory inside the current one."""
        if self.userObj.isAlive():
            try:
                print(f'Child of {self.name}, {self.childs[name]} requested')
                proxy = current.adapter.addWithUUID(self.childs[name])
                return IceDrive.DirectoryPrx.uncheckedCast(proxy)
            except KeyError as e:
                raise IceDrive.ChildNotExists(name, path=self.getPath())
        else:
            raise IceDrive.Unauthorized(self.user)

    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Create a new child directory and returns its proxy."""
        if self.userObj.isAlive():
            if name not in self.childs:  # Check if it already exists
                print(f'Request to create directory {name} in {self.name}')
                child = Directory(name, self.userObj, parent=self)  # Create the child
                self.childs[name] = child  # Add the child to the dictionary
                proxy = current.adapter.addWithUUID(child)
                self.saveToJson()
                return IceDrive.DirectoryPrx.uncheckedCast(proxy)
            raise IceDrive.ChildAlreadyExists(name, path=self.getPath())
        else:
            raise IceDrive.Unauthorized(self.user)  

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        """Remove the child directory with the given name if exists."""
        if self.userObj.isAlive():
            if name in self.childs:  # Check if the child exists
                print(f'Remove the child {name} from {self.name}')
                del self.childs[name]  # Delete the child
                self.saveToJson()
            else:
                raise IceDrive.ChildNotExists(name, path=self.getPath())
        else:
            raise IceDrive.Unauthorized(self.user)

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        """Return a list of the files linked inside the current directory."""
        if self.userObj.isAlive():
            print(f'Request to list files in {self.name}')
            return list(self.files.keys())
        else:
            raise IceDrive.Unauthorized(self.user)

    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        """Return the "blob id" for a given file name inside the directory."""
        if self.userObj.isAlive():
            try:
                return self.files[filename]
                print(f'Request to get BlobId of {filename}: {self.files[filename]}')
            except KeyError as e:
                raise IceDrive.FileNotFound(filename)
        else:
            raise IceDrive.Unauthorized(self.user)

    def linkFile(self, filename: str, blob_id: str, current: Ice.Current = None) -> None:
        """Link a file to a given blob_id."""
        if self.userObj.isAlive():
            BlobServicePrx = self.discovery.selectBlob()  # Get a blob service
            if BlobServicePrx == None:
                raise IceDrive.TemporaryUnavailable('Blob Service')
            else:
                BlobServicePrx.link(blob_id)
                if filename not in self.files:  # Check if the file exists
                    print(f'Request to link file {filename} to {self.name}')
                    self.files[filename] = blob_id  # Create and add the file
                    self.saveToJson()
                else:
                    raise IceDrive.FileAlreadyExists(filename)
        else:
            raise IceDrive.Unauthorized(self.user)

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        """Unlink (remove) a filename from the current directory."""
        if self.userObj.isAlive():
            BlobServicePrx = self.discovery.selectBlob()  # Get a blob service
            if BlobServicePrx == None:
                raise IceDrive.TemporaryUnavailable('Blob Service')
            else:
                BlobServicePrx.unlink(self.getBlobId(filename))
                if filename in self.files:  # Check if it exists
                    print(f'Request to unlink file {filename} from {self.name}')
                    del self.files[filename]  # Delete the file
                    self.saveToJson()
                else:
                    raise IceDrive.FileNotFound(filename)
        else:
            raise IceDrive.Unauthorized(self.user)
   
    def getPath(self, current: Ice.Current = None) -> str:
        """Get the path from root to the current dir"""
        if self.userObj.isAlive():
            if self.parent:  # Check if it has a parent (is not root)
                return os.path.join(self.parent.getPath(), self.name)  # Recursive
            else:
                return ""
        else:
            raise IceDrive.Unauthorized(self.user)

    def saveToJson(self):
        """Save the entire directory structure to a JSON file."""
        root = self
        while root.parent is not None:
            root = root.parent  # Traverse up to find the root

        data = root.serialize()  # Start serialization from the root
        json_path = os.path.join(root.dataDir, f"{root.genUUID(root.user)}.json")
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file)
        return json_path

    def serialize(self):
        """Recursively serialize the directory structure."""
        data = {
            'name': self.name,
            'user': self.user,
            'childs': {name: child.serialize() for name, child in self.childs.items()},
            'files': self.files
        }
        return data

    def loadFromJson(self, json_path):
        """Load the directory structure from a JSON file (USED ON ROOT DIR ONLY)"""
        with open(json_path, 'r',  encoding='utf-8') as json_file:
            data = json.load(json_file)
            self.name = data['name']  # Name of the root is always root but...
            self.user = data['user']  # The Username (UserObj is already there)
            self.files = data['files']  # Files they have saved
            self.childs = {name: self.loadChildFromJson(child_data, parent=self) for
                           name, child_data in data['childs'].items()} # Recursively load other childs

    def loadChildFromJson(self, child_data, parent=None):
        """Recursively load a child directory from JSON data (USED FOR EVERY OTHER DIR)"""
        child = Directory(name=child_data['name'], user=parent.userObj, parent=parent)  # Create user 
        child.user = child_data['user']
        child.files = child_data['files']
        child.childs = {name: child.loadChildFromJson(data, parent=child) for
                        name, data in child_data['childs'].items()}
        return child

    def genUUID(self, user):
        """Generate or resolve a unique user UUID"""
        namespace = UD.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        uuid = UD.uuid5(namespace, user)
        return str(uuid)


class DirectoryService(IceDrive.DirectoryService):
    """Implementation of the IceDrive.Directory interface."""
    def __init__(self):  # When the server is started, check if the folder exists
        self.dataDir = "./USRDIRS/"
        os.makedirs(self.dataDir, exist_ok=True)

    def getRoot(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy for the root directory of the given user."""
        # user = UserPrx
        # self.user = Username

        self.user = user.getUsername()
        json_path = os.path.join(self.dataDir, f"{self.genUUID(self.user)}.json")
        print(f'Request to get root of {user}')
        
        discovery = Discovery()  # Create the discovery object
        AuthServicePrx = discovery.selectAuthenticator()  # Get an authenticator

        #TODO: Wait a max of 5 seconds and if no response is given, try a different one and remove
        #previous one

        if AuthServicePrx == None:  # Check if it is a valid prx
            raise IceDrive.TemporaryUnavailable('Authentication Service')
        else: 
            if AuthServicePrx.verifyUser: # Check if it is valid
                if user.isAlive(): # Check the user is alive
                    if os.path.exists(json_path):  # Root already exists
                        root = Directory(name="root", user=user)
                        root.loadFromJson(json_path)
                    elif False: #TODO: Check if other instances have it
                        pass
                    else:  # Root does not exist
                        root = Directory(name="root", user=user)
                        root.saveToJson()
                    proxy = current.adapter.addWithUUID(root)
                    return IceDrive.DirectoryPrx.uncheckedCast(proxy)
                else:
                    raise IceDrive.Unauthorized(self.user)
            else:  # The user is not valid
                raise IceDrive.Unauthorized(self.user)

    def genUUID(self, user):
        """Generate or resolve a unique user UUID"""
        namespace = UD.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        uuid = UD.uuid5(namespace, user)
        return str(uuid)
