"""Directory service application."""

import logging
import sys
import time
from typing import List

import Ice
import IceDrive

from .directory import DirectoryService
from .discovery import Discovery


class DirectoryApp(Ice.Application):
    """Implementation of the Ice.Application for the Directory service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the Directory class."""
        # Directory
        adapter = self.communicator().createObjectAdapter("DirectoryAdapter")
        adapter.activate()
        servant = DirectoryService()
        servant_proxy = adapter.addWithUUID(servant)
        logging.info("Proxy: %s", servant_proxy)

        # Discovery
        ip_vm = '10.200.1.147'
        directory = IceDrive.DirectoryPrx.uncheckedCast(servant_proxy)

        #FIX: TEMPORAL BAND-AID UNTIL I CAN FIGURE OUT HOW TO USE THE MF CONFIG FILE
        tp_manager = self.communicator().stringToProxy(f'IceStorm/TopicManager:tcp -h {ip_vm} -p 10000') 
        tp_manager = IceStorm.TopicManagerPrx.checkedCast(topic_mgr)

        try:  # Attempt to obtain the topic
            discovery_tp = tp_manager.retrieve("discovery")
        except IceStorm.NoSuchTopic:  # If not, create it
            discovery_tp = tp_manager.create("discovery")

        discovery_publisher = discovery_tp.getPublisher()  # Obtain the publisher for the topic
        discovery = IceDrive.DiscoveryPrx.uncheckedCast(discovery_publisher)  # Create a proxy for the discovery service
        
        logging.info("Proxy: %s", servant_proxy)

        while True:
            discovery.announceDirectoryService(directory)  # Announce ourselves
            time.sleep(5)  # Wait 5 seconds
        
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = DirectoryApp()
    return app.main(sys.argv)