"""Directory service application."""

import logging
import sys
from typing import List

import Ice
import IceDrive

from icedrive_directory.directory import DirectoryService

class DirectoryApp(Ice.Application):
    """Implementation of the Ice.Application for the Directory service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the Directory class."""
        adapter = self.communicator().createObjectAdapter("DirectoryAdapter")
        adapter.activate()

        servant = DirectoryService()
        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


class ClientApp(Ice.Application):
    def run(self, args: List[str]) -> int:
        if len(args) != 2:
            print("Error: a proxy, and only one proxy, should be passed")
            return 1

        proxy = self.communicator().stringToProxy(args[1])
        server_proxy = IceDrive.DirectoryServicePrx.checkedCast(proxy)

        if not server_proxy:
            print(f"Proxy {server_proxy} is not available.")
            return 2

        # RUBRIC TEST CASES
        # Requirement 1
        self.juan = "Juan"
        root_juan = server_proxy.getRoot(self.juan)
        input("Requirement 1 completed, press enter")

        # Requirement 2
        root_juan = server_proxy.getRoot(self.juan)
        input("Requirement 2 completed, press enter")

        # Requirement 3
        self.david = "David"
        root_david = server_proxy.getRoot(self.david)
        input("Requirement 3 completed, press enter")

        # Requirement 4 <- Problematic
        try:
            root_parent_juan = root_juan.getParent
        except Ice.UnknownException as e:
            print(f'Caught Ice.UnknownException: {e}')
        except IceDrive.RootHasNoParent as e:
            print(f'Caught IceDrive.RootHasNoParent exception: {e}')
        input("Requirement 4 completed [Problematic], press enter")

        # Requirement 5
        documents_juan = root_juan.createChild("Documents")
        print(f'root_juan[childs]: {root_juan.getChilds()}')
        input("Requirement 5 completed, press enter")

        # Requirement 6
        documents_juan2 = root_juan.getChild("Documents")
        print(f'root_juan[childs]: {root_juan.getChilds()}')
        input("Requirement 6 completed, press enter")

        # Requirement 7 <- Problematic
        try:
            non_existant_juan = root_juan.getChild("Non-Existant-Directory")
        except Ice.UnknownException as e:
            print(f'Caught Ice.UnknownException: {e}')
        except IceDrive.ChildNotExists as e:
            print(f'Caught IceDrive.ChildNotExists exception: {e}')
        input("Requirement 7 completed [Problematic], press enter")

        # Requirement 8
        images_juan = root_juan.createChild("Images")
        input("Requirement 8 completed, press enter")

        # Requirement 9
        print(f'root_juan[childs]: {root_juan.getChilds()}')
        input("Requirement 9 completed, press enter")

        # Requirement 10 <- Problematic
        try:
            images_juan = root_juan.createChild("Images")
            print(f'root_juan[childs]: {root_juan.getChilds()}')
        except Ice.UnknownException as e:
            print(f'Caught Ice.UnknownException: {e}')
        except IceDrive.ChildAlreadyExists as e:
            print(f'Caught IceDrive.ChildAlreadyExists exception: {e}')
        input("Requirement 10 completed [Problematic], press enter")

        # Requirement 11
        root_juan.removeChild("Images")
        input("Requirement 11 completed, press enter")

        # Requirement 12
        print(f'root_juan[childs]: {root_juan.getChilds()}')
        input("Requirement 12 completed, press enter")

        # Requirement 13
        documents_juan.linkFile("file1.txt", "blob1")
        print(f'documents_juan[files]: {documents_juan.getFiles()}')
        input("Requirement 13 completed, press enter")

        # Requirement 14
        print(f'documents_juan/file1.txt[blobid]: {documents_juan.getBlobId("file1.txt")}')
        print(f'documents_juan[files]: {documents_juan.getFiles()}')
        input("Requirement 14 completed, press enter")

        # Requirement 15 <- Problematic
        try:
            print(f'documents_juan/naf.f[blobid]: {documents_juan.getBlobId("naf.f")}')
            print(f'documents_juan[files]: {documents_juan.getFiles()}')
        except Ice.UnknownException as e:
            print(f'Caught Ice.UnknownException: {e}')
        except IceDrive.FileNotFound as e:
            print(f'Caught IceDrive.FileNotFound exception: {e}')
        input("Requirement 15 completed [Problematic], press enter")

        # Requirement 16
        documents_juan.linkFile("file2.txt", "blob2")
        input("Requirement 16 completed, press enter")

        # Requirement 17
        print(f'documents_juan[files]: {documents_juan.getFiles()}')
        input("Requirement 17 completed, press enter")

        # Requirement 18
        print(f'documents_juan/file2.txt[blobid]: {documents_juan.getBlobId("file2.txt")}')
        print(f'documents_juan[files]: {documents_juan.getFiles()}')
        input("Requirement 18 completed, press enter")

        # Requirement 19 <- Problematic
        try:
            print(f'documents_juan/file1.txt[blobid]: {documents_juan.getBlobId("file1.txt")}')
            print(f'documents_juan[files]: {documents_juan.getFiles()}')
        except Ice.UnknownException as e:
            print(f'Caught Ice.UnknownException: {e}')
        except IceDrive.FileAlreadyExists as e:
            print(f'Caught IceDrive.FileAlreadyExists exception: {e}')
        input("Requirement 19 completed [Problematic], press enter")

        # Requirement 20
        documents_juan.unlinkFile("file2.txt")
        input("Requirement 20 completed, press enter")

        # Requirement 21
        print(f'documents_juan[files]: {documents_juan.getFiles()}')
        input("Requirement 21 completed, press enter")

        # Requirement 22 <- Problematico
        try:
            print(f'documents_juan/file2.txt[blobid]: {documents_juan.getBlobId("file2.txt")}')
            print(f'documents_juan[files]: {documents_juan.getFiles()}')
        except Ice.UnknownException as e:
            print(f'Caught Ice.UnknownException: {e}')
        except IceDrive.FileNotFound as e:
            print(f'Caught IceDrive.FileNotFound exception: {e}')
        input("Requirement 22 completed [Problematic], press enter")

        # Requirement 23 <- Problematico
        try:
            documents_juan.unlinkFile("naf.f")
            print(f'documents_juan[files]: {documents_juan.getFiles()}')
        except Ice.UnknownException as e:
            print(f'Caught Ice.UnknownException: {e}')
        except IceDrive.FileNotFound as e:
            print(f'Caught IceDrive.FileNotFound exception: {e}')
        input("Requirement 23 completed [Problematic], press enter")
