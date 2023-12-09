"""Module for servants implementations."""

from typing import List
import Ice
import IceDrive
import os
import json
import uuid as UD
import hashlib

class Directory(IceDrive.Directory):
    """Implementation of the IceDrive.Directory interface."""
    def __init__(self, name, root):
        """Create the Directory"""
        self.name = name
        self.parent = parent
        self.childs = {}
        self.files = {}

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to the parent directory, if it exists. None in other case."""
        proxy = current.adapter.addWithUUID(self.parent)
        return IceDrive.DirectoryPrx.uncheckedCast(proxy)

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        """Return a list of names of the directories contained in the directory."""
        return list(self.childs.keys())

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to one specific directory inside the current one."""
        try:
            proxy = current.adapter.addWithUUID(self.childs[name])
            return IceDrive.DirectoryPrx.uncheckedCast(proxy)
        except KeyError:
            raise ChildNotExists(name, path=self.getPath())

    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Create a new child directory and returns its proxy."""
        if name not in self.childs:  # Check if it already exists
            child = Directory(name, parent=self)  # Create the child
            self.childs[name] = child  # Add the child to the dictionary
            proxy = current.adapter.addWithUUID(child)
            return IceDrive.DirectoryPrx.uncheckedCast(proxy)
        else:  # If it already exists throw an exception
            raise ChildAlreadyExists(name, path=self.getPath())  

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        """Remove the child directory with the given name if exists."""
        if name in self.childs:  # Check if the child exists
            del self.childs[name]  # Delete the child
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
            raise FileNotFound(filename)

    def linkFile(self, filename: str, blob_id: str, current: Ice.Current = None) -> None:
        """Link a file to a given blob_id."""
        if filename not in self.files:  # Check if the file exists
            self.files[filename] = blob_id  # Create and add the file
        else:  # If it already exists, throw exception
            raise FileAlreadyExists(filename)

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        """Unlink (remove) a filename from the current directory."""
        if filename in self.files:  # Check if it exists
            del self.files[filename]  # Delete the file
        else:  # If it doesn"t exist, throw exception
            raise FileNotFound(filename)
    
    def getPath(self):
        """Get the path from root to the current dir"""
        if self.parent:  # Check if it has a parent (is not root)
            return os.path.join(self.parent.getPath(), self.name)  # Recursive
        else:
            return ""


class DirectoryService(IceDrive.DirectoryService):
    """Implementation of the IceDrive.Directory interface."""
    def __init__(self):
        self.dataDir = "./USRDIRS/"
        os.makedirs(self.dataDir, exist_ok=True)

    def getRoot(self, user: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy for the root directory of the given user."""
        userFilePath = self.getUserFilePath(user)
        if os.path.exists(userFilePath):
            with open(userFilePath, "r") as file:
                userData = json.load(file)
                proxy = current.adapter.addWithUUID(self.loadDirectory(userData))
                return IceDrive.DirectoryPrx.uncheckedCast(proxy)
        else:
            root = Directory(name="root")
            self.saveDirectory(root, user)
            proxy = current.adapter.addWithUUID(root)
            return IceDrive.DirectoryPrx.uncheckedCast(proxy)

    def getUserFilePath(self, user):
        """Resolve the path to the user directory"""
        uuid = self.genUUID(user)
        return os.path.join(self.dataDir, f"{uuid}.json")

    def saveDirectory(self, directory, user):
        """Save the data to the JSON file"""
        userFilePath = self.getUserFilePath(user)
        data = self.serializeDirectory(directory)
        with open(userFilePath, "w") as file:
            json.dump(data, file)

    def genUUID(self, user):
        """Generate or resolve a unique user UUID"""
        namespace = UD.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        uuid = UD.uuid5(namespace, user)
        return str(uuid)

    def loadDirectory(self, data):
        """Create a directory object from the JSON file"""
        directory = DirectoryI(name=data["name"])
        for childName, childData in data.get("childs", {}).items():
            child = self.loadDirectory(childData)
            directory.childs[childName] = child
            child.parent = directory
        directory.files = data.get("files", {})
        return directory

    def serializeDirectory(self, directory):
        """Convert the structure to JSON format"""
        data = {"name": directory.name}
        if directory.childs:  # Check for child directories
            data["childs"] = {name: self.serializeDirectory(child) 
                for name, child in directory.childs.items()}
        if directory.files:  # Check for files
            data["files"] = directory.files
        return data


# Exceptions: 
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
