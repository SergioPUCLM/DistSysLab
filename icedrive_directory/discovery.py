"""Servant implementations for service discovery."""
import random

import Ice
import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    discAuthenticators = {}  # Discovered authenticator services
    discDirectoryServices = {}  # Discovered directory services
    discBlobServices = {}  # Discovered blob services
    def __init__(self):
        pass

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        print(f'Found Authenticator at {prx}')
        discAuthenticators[prx.ice_getIdentity()] = prx

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        print(f'Found DirectoryService at {prx}')
        discDirectoryServices[prx.ice_getIdentity()] = prx

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        print(f'Found BlobService at {prx}')
        discBlobServices[prx.ice_getIdentity()] = prx

    def selectAuthenticator(self):
        if len(discAuthenticators) == 0:
            return None
        else:
            chosen = random.choice(list(discAuthenticators.keys()))
            return discAuthenticators[chosen]

    def selectBlob(self):
        if len(discAuthenticators) == 0:
            return None
        else:
            chosen = random.choice(list(discBlobServices.keys()))
            return discBlobServices[chosen]