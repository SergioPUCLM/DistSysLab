import sys

from icedrive_directory.app import DirectoryApp

#def client() -> int:
#    """Handler for the ClientApp"""
#    app = ClientApp()
#    return app.main(sys.argv)

def server() -> int:
    """Handler for the DirectoryApp"""
    app = DirectoryApp()
    return app.main(sys.argv)
