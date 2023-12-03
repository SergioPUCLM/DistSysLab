import os
import json
from typing import List

class Directory:
    def __init__(self, name, parent=None):  # Create a directory
        self.name = name
        self.parent = parent
        self.childs = {}
        self.files = {}

    def getParent(self):  # Return the parent of a directory
        return self.parent

    def getChilds(self)-> List[str]:  # Return a list of childs
        return list(self.childs.keys())

    def getChild(self, name):  # Return a Directory child object
        return self.childs.get(name)

    def createChild(self, name):  # Create a child
        if name not in self.childs:  # Check if it already exists
            child = Directory(name, parent=self)  # Create the child
            self.childs[name] = child  # Add the child to the dictionary
            return child
        else:  # If it already exists throw an exception
            raise ChildAlreadyExists(name, path=self.getPath())  

    def removeChild(self, name):  # Delete a child
        if name in self.childs:  # Check if the child exists
            del self.childs[name]  # Delete the child
        else:  # If it does not exist, throw exception
            raise ChildNotExists(name, path=self.getPath())

    def getFiles(self)-> List[str]:  # Return a list of files
        return list(self.files.keys())

    def getBlobId(self, filename):  # Find the bloblid of a file
        return self.files.get(filename)

    def linkFile(self, filename, blob_id):  # Add a new file
        if filename not in self.files:  # Check if the file exists
            self.files[filename] = blob_id  # Create and add the file
        else:  # If it already exists, throw exception
            raise FileAlreadyExists(filename)

    def unlinkFile(self, filename):  # Delete a file
        if filename in self.files:  # Check if it exists
            del self.files[filename]  # Delete the file
        else:  # If it doesn't exist, throw exception
            raise FileNotFound(filename)

    def getPath(self):  # Get the path from root to the current dir
        if self.parent:  # Check if it has a parent (is not root)
            return os.path.join(self.parent.getPath(), self.name)  # Recursive
        else:
            return ""

class DirectoryService:
    def __init__(self, dataDir='./USRDIRS/'):  # Initialize the directory
        self.dataDir = dataDir
        os.makedirs(self.dataDir, exist_ok=True)  # Make the base directory if it doesn't exist

    def getUserFilePath(self, user):  # Get the path to the user json file
        return os.path.join(self.dataDir, f'{user}.json')

    def getRoot(self, user):  # Return the root directory 
        userFilePath = self.getUserFilePath(user)  # Find the path to the file
        if os.path.exists(userFilePath):  # Check if the file exists
            with open(userFilePath, 'r') as file:  # Open the file
                userData = json.load(file)
                return self.loadDirectory(userData)
        else:
            root = Directory(name='root')
            self.saveDirectory(root, user)
            return root

    def saveDirectory(self, directory, user):  # Save the directory into a user's json
        userFilePath = self.getUserFilePath(user)
        data = self.serializeDirectory(directory)
        with open(userFilePath, 'w') as file:
            json.dump(data, file)

    def loadDirectory(self, data):  # Create a directory object from the json file
        directory = Directory(name=data['name'])  # Create the directory
        for childName, childData in data.get('childs', {}).items():  # Add the childs
            child = self.loadDirectory(childData)
            directory.childs[childName] = child
            child.parent = directory
        directory.files = data.get('files', {})
        return directory

    def serializeDirectory(self, directory):  # Convert the structure to json data
        data = {'name': directory.name}
        if directory.childs:  # Check for child directories
            data['childs'] = {name: self.serializeDirectory(child) 
                for name, child in directory.childs.items()}
        if directory.files:  # Check for files
            data['files'] = directory.files
        return data

# exceptions:
class ChildAlreadyExists(Exception):
    def __init__(self, childName, path):
        super().__init__(f"Child directory '{childName}' already exists in path: {path}")

class ChildNotExists(Exception):
    def __init__(self, childName, path):
        super().__init__(f"Child directory '{childName}' does not exist in path: {path}")

class FileAlreadyExists(Exception):
    def __init__(self, filename):
        super().__init__(f"File '{filename}' already exists in the directory")

class FileNotFound(Exception):
    def __init__(self, filename):
        super().__init__(f"File '{filename}' not found in the directory")
