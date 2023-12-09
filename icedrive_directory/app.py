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

        # USER TEST:
        self.user = "Sergio"

        # Get root directory proxy for the user
        root_directory = server_proxy.getRoot(self.user)

        child3 = root_directory.createChild("Videos")

        # Create directories and files
        child1 = root_directory.createChild("Documents")
        child2 = root_directory.createChild("Pictures")
        child2 = root_directory.createChild("Images")
        root_directory.linkFile("file1.txt", "blob1")
        child1.linkFile("file2.txt", "blob2")
        return 0
