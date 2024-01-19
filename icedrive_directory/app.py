"""Directory service application."""

import logging
import sys
import time
from typing import List

import Ice
import IceDrive
import IceStorm

from icedrive_directory.directory import DirectoryService
from icedrive_directory.discovery import Discovery


class DirectoryApp(Ice.Application):
    """Implementation of the Ice.Application for the Directory service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the Directory class."""
        # Directory
        adapter = self.communicator().createObjectAdapter("DirectoryAdapter")  # Obj adapter
        adapter.activate()  # Activate adapter
        servant = DirectoryService()  # Create DirectoryService
        servant_proxy = adapter.addWithUUID(servant)  # Proxy for directory servant (add to adapter)
        logging.info("Proxy: %s", servant_proxy)

        # Discovery
        tp_manager = self.communicator().propertyToProxy('IceStorm.TopicManager.Proxy')
        tp_manager = IceStorm.TopicManagerPrx.checkedCast(tp_manager)

        properties = self.communicator().getProperties()
        try:  # Attempt to obtain the discovery topic from the manager
            discovery_tp = tp_manager.retrieve(properties.getProperty('DiscoveryTopic'))
        except IceStorm.NoSuchTopic:  # If not, create it
            discovery_tp = tp_manager.create('discovery')

        discovery_publisher = discovery_tp.getPublisher()  # Obtain the publisher for the topic
        discovery = IceDrive.DiscoveryPrx.uncheckedCast(discovery_publisher)  # Create a proxy for the discovery service

        qos = {}
        listener = Discovery()
        listener_proxy = adapter.addWithUUID(listener)
        subscriber = IceStorm.TopicPrx.uncheckedCast(listener_proxy)
        discovery_tp.subscribeAndGetPublisher(qos, subscriber)

        directory = IceDrive.DirectoryServicePrx.uncheckedCast(servant_proxy)
        while True:  # Repeat infinitely
            discovery.announceDirectoryService(prx=directory)  # Announce ourselves
            time.sleep(5)  # Wait 5 seconds
        
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = DirectoryApp()
    return app.main(sys.argv)