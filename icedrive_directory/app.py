"""Directory service application."""

import logging
import sys
from typing import List

import Ice
import IceDrive

from icedrive_directory.directory import DirectoryService
from icedrive_directory.discovery import Discovery

class DirectoryApp(Ice.Application):
    """Implementation of the Ice.Application for the Directory service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the Directory class."""
        adapter = self.communicator().createObjectAdapter("DirectoryAdapter")
        adapter.activate()

        servant = DirectoryService()
        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy: %s", servant_proxy)

        discovery_adapter = self.communicator().createObjectAdapter("DiscoveryAdapter")
        discovery_adapter.activate()

        discovery_servant = Discovery()
        discovery_servant_proxy = discovery_adapter.addWithUUID(discovery_servant)

        logging.info("Discovery proxy: %s", discovery_servant_proxy)

        # Start the announcements
        discovery_servant.announceDirectoryService(servant)

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
        self.juan = "Juan"
        root_juan = server_proxy.getRoot(self.juan)


        # Requirement 4 <- Problematic
        try:
            root_parent_juan = root_juan.getParent()
        except IceDrive.RootHasNoParent as e:
            print(f'Caught IceDrive.RootHasNoParent exception: {e}')
        input("Requirement 4 completed [Problematic], press enter")

        documents_juan = root_juan.createChild("Documents")

        # Requirement 7 <- Problematic
        try:
            non_existant_juan = root_juan.getChild("Non-Existant-Directory")
        except IceDrive.ChildNotExists as e:
            print(f'Caught IceDrive.ChildNotExists exception: {e}')
        input("Requirement 7 completed [Problematic], press enter")

        images_juan = root_juan.createChild("Images")

        # Requirement 10 <- Problematic
        try:
            images_juan = root_juan.createChild("Images")
            print(f'root_juan[childs]: {root_juan.getChilds()}')
        except IceDrive.ChildAlreadyExists as e:
            print(f'Caught IceDrive.ChildAlreadyExists exception: {e}')
        input("Requirement 10 completed [Problematic], press enter")

        root_juan.removeChild("Images")
        documents_juan.linkFile("file1.txt", "blob1")

        # Requirement 15 <- Problematic
        try:
            print(f'documents_juan/naf.f[blobid]: {documents_juan.getBlobId("naf.f")}')
            print(f'documents_juan[files]: {documents_juan.getFiles()}')
        except IceDrive.FileNotFound as e:
            print(f'Caught IceDrive.FileNotFound exception: {e}')
        input("Requirement 15 completed [Problematic], press enter")

        documents_juan.linkFile("file2.txt", "blob2")

        print(f'documents_juan[files]: {documents_juan.getFiles()}')

        # Requirement 19 <- Problematic
        try:
            documents_juan.linkFile("file2.txt", "blob2")
        except IceDrive.FileAlreadyExists as e:
            print(f'Caught IceDrive.FileAlreadyExists exception: {e}')
        input("Requirement 19 completed [Problematic], press enter")

        documents_juan.unlinkFile("file2.txt")

        # Requirement 22 <- Problematico
        try:
            print(f'documents_juan/file2.txt[blobid]: {documents_juan.getBlobId("file2.txt")}')
            print(f'documents_juan[files]: {documents_juan.getFiles()}')
        except IceDrive.FileNotFound as e:
            print(f'Caught IceDrive.FileNotFound exception: {e}')
        input("Requirement 22 completed [Problematic], press enter")

        # Requirement 23 <- Problematico
        try:
            documents_juan.unlinkFile("naf.f")
            print(f'documents_juan[files]: {documents_juan.getFiles()}')
        except IceDrive.FileNotFound as e:
            print(f'Caught IceDrive.FileNotFound exception: {e}')
        input("Requirement 23 completed [Problematic], press enter")
