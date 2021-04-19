import pathlib

from .exceptions import DirectoryDoesNotExistError, DirectoryIsAFileError


def validate_path(provided_path: str) -> pathlib.Path:
    """ Helper function which checks if the provided path 1. exists, and 2. is not a file.
        With this we can be sure that the path points to a directory.

        :param provided_path: the path to validate.
        :raise DirectoryDoesNotExistError | DirectoryIsAFileError: if neither the path is valid or it is a file
    """

    path = pathlib.Path(provided_path)

    if not path.exists():  # if it is not a valid path (either to a directory or file)
        raise DirectoryDoesNotExistError("The supplied path does not exist.")

    if path.is_file():
        raise DirectoryIsAFileError("The supplied path is a file. Only supply a path to a directory.")

    provided_path = path

    return provided_path
