"""Servant implementations for service discovery."""
import random

import Ice
import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    def __init__(self):
        self.discAuthenticators = {}  # Discovered authenticator services
        self.discDirectoryServices = {}  # Discovered directory services
        self.discBlobServices = {}  # Discovered blob services

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        self.discAuthenticators[prx.ice_getIdentity()] = prx
        print(f'Found Authenticator at {prx}')
        with open('authenticators.txt', 'a') as file:  # Save to a file
            file.write(f'Found Authenticator at {prx.ice_getIdentity()}\n')

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        self.discDirectoryServices[prx.ice_getIdentity()] = prx
        print(f'Found DirectoryService at {prx}')
        with open('directories.txt', 'a') as file:  # Save to a file
            file.write(f'Found Authenticator at {prx.ice_getIdentity()}\n')

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        self.discBlobServices[prx.ice_getIdentity()] = prx
        print(f'Found BlobService at {prx}')
        with open('blobs.txt', 'a') as file:  # Save to a file
            file.write(f'Found Authenticator at {prx.ice_getIdentity()}\n')

    def selectAuthenticator(self):
        if len(self.discAuthenticators) == 0:
            return None
        else:
            chosen = random.choice(list(self.discAuthenticators.keys()))
            return self.discAuthenticators[chosen]

    def selectBlob(self):
        if len(self.discAuthenticators) == 0:
            return None
        else:
            chosen = random.choice(list(self.discBlobServices.keys()))
            return self.discBlobServices[chosen]