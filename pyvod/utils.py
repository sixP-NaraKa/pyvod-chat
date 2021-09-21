"""
pyvod-chat - a simple tool to download a past Twitch.tv broadcasts (VOD) chat comments!

Available on GitHub (+ documentation): https://github.com/sixP-NaraKa/pyvod-chat
"""


import pathlib
from datetime import datetime

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


def get_strptime(datetime_string: str) -> datetime:
    """ Helper function which parses a valid datetime object out of a given datetime string (with a predefined format).

        :param datetime_string: the string to parse the datetime object from
        :return: the valid datetime object
    """

    if "." in datetime_string:
        split = datetime_string.split(".")
        microsecond_split = split[1]
        # 8 because 6 are max. for the datetime.strptime() %f's (microseconds) format code, and 1 is the Z character
        if len(microsecond_split) > 8:
            split[1] = microsecond_split[:6] + "Z"
        datetime_string = ".".join(split)
        return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        return datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%SZ")
