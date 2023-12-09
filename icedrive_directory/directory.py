"""Module for servants implementations."""

from typing import List
import os
import json
import uuid as UD
import Ice
import IceDrive

class Directory(IceDrive.Directory):
    """Implementation of the IceDrive.Directory interface."""
    def __init__(self, name, user, parent=None):
        """Create the Directory"""
        self.name = name
        self.user = user
        self.parent = parent
        self.childs = {}
        self.files = {}
        self.dataDir = "./USRDIRS/"

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to the parent directory, if it exists. None in other case."""
        if self.parent is not None:
            proxy = current.adapter.addWithUUID(self.parent)
            return IceDrive.DirectoryPrx.uncheckedCast(proxy)
        else:
            raise RootHasNoParent(self.name)

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        """Return a list of names of the directories contained in the directory."""
        return list(self.childs.keys())

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to one specific directory inside the current one."""
        try:
            proxy = current.adapter.addWithUUID(self.childs[name])
            return IceDrive.DirectoryPrx.uncheckedCast(proxy)
        except KeyError:
            raise ChildNotExists(name, path=self.getPath()) from KeyError

    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Create a new child directory and returns its proxy."""
        if name not in self.childs:  # Check if it already exists
            child = Directory(name, self.user, parent=self)  # Create the child
            self.childs[name] = child  # Add the child to the dictionary
            proxy = current.adapter.addWithUUID(child)
            self.saveToJson()
            return IceDrive.DirectoryPrx.uncheckedCast(proxy)
        else:  # If it already exists throw an exception
            raise ChildAlreadyExists(name, path=self.getPath())  

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        """Remove the child directory with the given name if exists."""
        if name in self.childs:  # Check if the child exists
            del self.childs[name]  # Delete the child
            self.saveToJson()
        else:  # If it does not exist, throw exception
            raise ChildNotExists(name, path=self.getPath())

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        """Return a list of the files linked inside the current directory."""
        return list(self.files.keys())

    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        """Return the "blob id" for a given file name inside the directory."""
        try:
            return self.files[filename]
        except KeyError:
            raise FileNotFound(filename) from KeyError

    def linkFile(self, filename: str, blob_id: str, current: Ice.Current = None) -> None:
        """Link a file to a given blob_id."""
        if filename not in self.files:  # Check if the file exists
            self.files[filename] = blob_id  # Create and add the file
            self.saveToJson()
        else:  # If it already exists, throw exception
            raise FileAlreadyExists(filename)

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        """Unlink (remove) a filename from the current directory."""
        if filename in self.files:  # Check if it exists
            del self.files[filename]  # Delete the file
            self.saveToJson()
        else:  # If it doesn"t exist, throw exception
            raise FileNotFound(filename)
   
    def getPath(self):
        """Get the path from root to the current dir"""
        if self.parent:  # Check if it has a parent (is not root)
            return os.path.join(self.parent.getPath(), self.name)  # Recursive
        else:
            return ""

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
        """Load the directory structure from a JSON file."""
        with open(json_path, 'r',  encoding='utf-8') as json_file:
            data = json.load(json_file)
            self.name = data['name']
            self.user = data['user']
            self.files = data['files']
            self.childs = {name: self.loadChildFromJson(child_data) for
                name, child_data in data['childs'].items()}

    def loadChildFromJson(self, child_data):
        """Recursively load a child directory from JSON data."""
        child = Directory(name=child_data['name'], user=child_data['user'])
        child.files = child_data['files']
        child.childs = {name: child.loadChildFromJson(data) for
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

    def getRoot(self, user: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy for the root directory of the given user."""
        json_path = os.path.join(self.dataDir, f"{self.genUUID(user)}.json")
        if os.path.exists(json_path):
            root = Directory(name="root", user=user)
            root.loadFromJson(json_path)
        else:
            root = Directory(name="root", user=user)
            root.saveToJson()
        proxy = current.adapter.addWithUUID(root)
        return IceDrive.DirectoryPrx.uncheckedCast(proxy)

    def genUUID(self, user):
        """Generate or resolve a unique user UUID"""
        namespace = UD.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        uuid = UD.uuid5(namespace, user)
        return str(uuid)


# Exceptions: 
class RootHasNoParent(Exception):
    def __init__(self, name):
        super().__init__(f"Directory \"{name}\" is a root directory and therefore has no parent")


class ChildAlreadyExists(Exception):
    def __init__(self, childName, path):
        super().__init__(f"Child directory \"{childName}\" already exists in path: {path}")


class ChildNotExists(Exception):
    def __init__(self, childName, path):
        super().__init__(f"Child directory \"{childName}\" does not exist in path: {path}")


class FileAlreadyExists(Exception):
    def __init__(self, filename):
        super().__init__(f"File \"{filename}\" already exists in the directory")


class FileNotFound(Exception):
    def __init__(self, filename):
        super().__init__(f"File \"{filename}\" not found in the directory")
