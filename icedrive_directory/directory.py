"""Module for servants implementations."""

from typing import List
import Ice
import IceDrive
import os

Ice.loadSlice
class Directory(IceDrive.Directory):
    #Implementation of the IceDrive.Directory interface.

    def __init__(self, name, root):
        # Create the Directory
        pass

    # REQUIRED METHODS FROM INTERFACE:
    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        #Return the proxy to the parent directory, if it exists. None in other case.
        pass

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        #Return a list of names of the directories contained in the directory.
        pass

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        #Return the proxy to one specific directory inside the current one.
        pass

    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        #Create a new child directory and returns its proxy.
        pass

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        #Remove the child directory with the given name if exists.
        pass

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        #Return a list of the files linked inside the current directory.
        pass

    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        #Return the "blob id" for a given file name inside the directory.
        pass

    def linkFile(self, filename: str, blob_id: str, current: Ice.Current = None) -> None:
        #Link a file to a given blob_id.
        pass

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        #Unlink (remove) a filename from the current directory.
        pass


class DirectoryService(IceDrive.DirectoryService):
    #Implementation of the IceDrive.Directory interface.
    def __init__(self):
        pass

    def getRoot(self, user: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        #Return the proxy for the root directory of the given user.
        pass
        
