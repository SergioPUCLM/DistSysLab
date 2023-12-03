from directory_manager import Directory, DirectoryService

def print_directory_structure(directory, indent=0):
    print("  " * indent + f"{directory.name}/")
    for child_name, child in directory.childs.items():
        print_directory_structure(child, indent + 1)
    for file_name in directory.files.keys():
        print("  " * (indent + 1) + f"{file_name}")

def main():
    user = "test_user"
    service = DirectoryService()

    # Get root directory for the user
    root_directory = service.getRoot(user)

    # Print initial directory structure
    print("Initial Directory Structure:")
    print_directory_structure(root_directory)

    # Create directories and files
    child1 = root_directory.createChild("Documents")
    child2 = root_directory.createChild("Pictures")
    child2 = root_directory.createChild("Images")
    root_directory.linkFile("file1.txt", "blob1")
    child1.linkFile("file2.txt", "blob2")

    # Print updated directory structure
    print("\nUpdated Directory Structure:")
    print_directory_structure(root_directory)

    # Save and load the directory to simulate a restart
    service.saveDirectory(root_directory, user)
    loaded_directory = service.getRoot(user)

    # Print loaded directory structure
    print("\nLoaded Directory Structure:")
    print_directory_structure(loaded_directory)

if __name__ == "__main__":
    main()
