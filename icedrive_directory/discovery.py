"""Servant implementations for service discovery."""

import Ice

import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    def __init__(self):
        """Keep a list of discovered services"""
        self.discAuthenticators = {}  # Discovered authenticator services
        self.discDirectoryServices = {}  # Discovered directory services
        self.discBlobServices = {}  # Discovered blob services
        self.communicator = None

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        identity = prx.ice_getIdentity()
        self.discAuthenticators[identity.name] = prx

    def announceDirectoryServicey(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        identity = prx.ice_getIdentity()
        self.discDirectoryServices[identity.name] = prx

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        identity = prx.ice_getIdentity()
        self.discBlobServices[identity.name] = prx
    
    def startAnnouncements(self):
        """Start sending announcements periodically."""
        adapter = self.communicator.createObjectAdapter("DiscoveryAdapter")
        proxy = adapter.addWithUUID(IceDrive.DiscoveryPrx.uncheckedCast(adapter.createProxy(adapter.getEndpoints()[0])))
        adapter.activate()

        while True:
            # Send authenticator announcements
            for authenticator_prx in self.discAuthenticators.values():
                authenticator_prx.announceAuthentication(proxy)

            # Send directory announcements
            for directory_prx in self.discDirectoryServices.values():
                directory_prx.announceDirectoryService(proxy)

            # Send blob announcements
            for blob_prx in self.discBlobServices.values():
                blob_prx.announceBlobService(proxy)

            Ice.Util.currentThread().sleep(Ice.Util.Time(5))  # Wait 5 seconds

    def initializeCommunicator(self, args):
        """Initialize the Ice communicator."""
        self.communicator = Ice.initialize(args)

    def destroyCommunicator(self):
        """Destroy the Ice communicator."""
        if self.communicator:
            self.communicator.destroy()