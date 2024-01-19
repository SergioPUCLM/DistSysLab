"""Servant implementations for service discovery."""
import random

import Ice
import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    def __init__(self):
        """Keep a list of discovered services"""
        self.authenticators = {}  # Discovered authentication services
        self.directories = {}  # Discovered directory services
        self.blobs = {}  # Discovered blob services

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement.""" 
        identity = prx.ice_getIdentity()
        if not(identity in self.authenticators):
            print(f'Authenticator service found: {prx}')
            self.authenticators[identity] = prx

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        identity = prx.ice_getIdentity()
        if not(identity in self.directories):
            print(f'Directory service found: {prx}')
            self.directories[identity] = prx       

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        identity = prx.ice_getIdentity()
        if not(identity in self.blobs):
            print(f'Blob service found: {prx}')
            self.blobs[identity] = prx

    def selectAuthenticator():
        """Select a random Authenticator Service"""
        if not self.authenticators:
            return None  # Return none so DirectoryService can throw the exception
        else:
            return authenticators[random.choice(list(authenticators.keys()))]

    def selectBlob():
        """Select a random Blob Service"""
        if not self.blobs:
            return None  # Return none so Directory can throw the exception
        else:
            return blobs[random.choice(list(blobs.keys()))]
