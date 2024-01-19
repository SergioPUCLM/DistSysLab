"""Servant implementations for service discovery."""
import random

import Ice
import IceDrive


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    # Global dictionaries so any object can access them
    authenticators = {}  # Discovered authentication services
    directories = {}  # Discovered directory services
    blobs = {}  # Discovered blob services

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement.""" 
        identity = prx.ice_getIdentity()
        if not(identity in Discovery.authenticators):
            print(f'Authenticator service found: {prx}')
            Discovery.authenticators[identity] = prx

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        identity = prx.ice_getIdentity()
        if not(identity in Discovery.directories):
            print(f'Directory service found: {prx}')
            Discovery.directories[identity] = prx       

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        identity = prx.ice_getIdentity()
        if not(identity in Discovery.blobs):
            print(f'Blob service found: {prx}')
            Discovery.blobs[identity] = prx

    def selectAuthenticator(self):
        """Select a random Authenticator Service"""
        if not Discovery.authenticators:
            return None  # Return none so DirectoryService can throw the exception
        else:
            return Discovery.authenticators[random.choice(list(Discovery.authenticators.keys()))]

    def selectBlob(self):
        """Select a random Blob Service"""
        if not Discovery.blobs:
            return None  # Return none so Directory can throw the exception
        else:
            return Discovery.blobs[random.choice(list(Discovery.blobs.keys()))]
