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

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        print(f'Found Authenticator at {prx}')
        self.discAuthenticators[prx.ice_getIdentity()] = prx

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        print(f'Found DirectoryService at {prx}')
        self.discDirectoryServices[prx.ice_getIdentity()] = prx

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        print(f'Found BlobService at {prx}')
        self.discBlobServices[prx.ice_getIdentity()] = prx
    