# custom exceptions

class TwitchApiException(Exception):
    """ An exception for when the Twitch API response fails / does not respond with status code 200. """
    pass


class DirectoryDoesNotExistError(Exception):
    """ An exception for when a supplied directory path does not exist. """
    pass


class DirectoryIsAFileError(Exception):
    """ An exception for when a supplied directory path points to a file instead of a folder. """
    pass
