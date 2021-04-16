from os import getenv
from os import getenv, getcwd
import json
from typing import Generator
from typing import Generator, Union

import requests

import dotenv
import pathlib

# with trying to use it at the inbuilt Terminal here in PyCharm (and prob otherwise) these imports here are failing
# but if we simply use pyinstaller and make it an .exe, then we should be gucci anyway (can be hingeklatscht in GitHub
# as part of a release) - i.e. either use it manually or use it as a Python package/module
# from pyvod.exceptions import TwitchApiException
# from .exceptions import TwitchApiException

# https://dev.twitch.tv/docs/v5
base_url = "https://api.twitch.tv/v5/videos/{}/comments"  # videos/979245105/ for example

# required headers for the API requests
dotenv.load_dotenv()  # no path speficication necessary, if .env file is simply called ".env", otherwise path needed
dotenv.load_dotenv()
headers = {"client-id": getenv("client-id"), "accept": "application/vnd.twitchtv.v5+json"}


# TODO: - custom user defined file paths, both via usage as a module and standalone (via cmd, etc.)
#       --> option -fp (add to argument parser), default None
#       --> in the cleaned_comments method, we simply add a argument to add a file path, default None
#       we then simply make the check against the file path there, and that should be a simple solution


class TwitchApiException(Exception):
    """ An exception for when the Twitch API response fails / does not respond with status code 200. """
    pass


def _validate_path(provided_path: str):
    """ Helper function which checks if the provided path 1. exists, and 2. is not a file.
        With this we can be sure that the path points to a directory.

        :param provided_path the path to validate. Defaults to the current working directory.
        :raise RunTimeError if neither the path is valid or it is a file
    """

    path = pathlib.Path(provided_path)

    if not path.exists():  # if it is not a valid path (either to a directory or file)
        raise RuntimeError("The supplied path does not exist.")

    if path.is_file():
        raise RuntimeError("The supplied path is a file. Only supply a path to a directory.")

    provided_path = path

    return provided_path


class VODChat:
    """ A class which represents the VOD stream chat. We store here both the 'raw_comment' data (i.e. the JSON) for
        and the 'cleaned_comments'.

        To get all the comments from a VOD, we have to make multiple requests with a 'cursor' specified - we get
        this cursor from a previous request. This cursor is stored in the '_next' key of the JSON.
        Hence "Batch X" within the raw_comments dictionary.
        We store the comments in batches within a new dict, before storing it as a class attribute.

        Later on, once we have all the raw_comments data, we will clean the comments via the 'clean_comments' method,
        and storing these inside the 'cleaned_comments' class attribute.
    """

    def __init__(self, vod_id: str):
        if not vod_id or not isinstance(vod_id, str):  # if the supplied vod_id is empty or not a str
        if not vod_id:  # if the supplied vod_id is empty
            raise ValueError("'vod_id' required.")
        self.vod_id = str(vod_id)  # cast it so string, just to be safe
        self.vod_id = str(vod_id)  # cast it to string, just to be safe
        self.cleaned_comments = list()  # None
        self.raw_comments = dict()  # None

        self.url = base_url.format(self.vod_id)

        # first and last comment of the VOD
        # contains both the user name and the timestamp (when the chat comment was sent)
        self.first_comment = None  # tuple()  # None
        self.last_comment = None  # tuple()  # None

    def _get_raw_chat_comments_from_vod(self) -> Generator:
        """ Gets the raw comments from the VOD. 'raw comments', because all the other 'junk' the request response gives
            us, has yet to be properly cleaned and only the relevant information extracted.

            For this cleaning, see the class method :meth:`clean_and_process_comments()`.
        """

        counter = 1
        _next = ""  # for our first request, we don't have a _next cursor, so we simply use an empty string
        no_comments = False  # a flag we set if the first request response contains an empty "comments" list value
        while True:

            # make new request with the _next cursor, so we can get the next comments payload
            _request_response = requests.get(url=self.url, headers=headers, params={"cursor": _next})
            _json = _request_response.json()

            if _request_response.status_code != 200:
                msg_from_twitch = _json["message"]
                raise TwitchApiException(
                    "Twitch API responded with '{1}' (status code {0}). Expected 200 (OK)."
                    .format(_request_response.status_code, msg_from_twitch)
                )

            _next = _json.get("_next", 0)  # get the key, if not found default to 0

            # add the next/new batch of comments to the raw_comments, which we can later clean
            self.raw_comments[f"Batch {counter}"] = _json

            if _next == 0:  # if there are no more chat comments to fetch, we are done
                yield _json  # we yield the last _json here, because otherwise we don't process this last request
                break

            counter += 1

            yield _json

    @staticmethod
    def _get_channel(channel_id: str) -> tuple[str, int, int, str]:
        """ Get the channel for the specified channel ID. Also fetches additional data, such as the amount of
            followers of the channel, the name of the channel, the amount of views and if the broadcaster type.
        """

        channel_url = "https://api.twitch.tv/v5/channels/{channel_id}".format(channel_id=channel_id)
        response = requests.get(url=channel_url, headers=headers).json()

        return response["display_name"], response["views"], response["followers"], response["broadcaster_type"]

    @staticmethod
    def _get_amt_subscribers(channel_id: str):
        """ Get the amount of subscribers for a given channel ID. """

        subs_url = "https://api.twitch.tv/v5/channels/{channel_id}/subscriptions".format(channel_id=channel_id)
        response = requests.get(url=subs_url, headers=headers)
        print(response.json())

    @staticmethod
    def _get_followers(channel_id: str):
        """ Gets the amount of followers for a given channel ID.
            This is actually not needed anymore, since we get the amount of followers directly from the channel request.
        """
        raise NotImplementedError

    @staticmethod
    def get_vod_date(vod_id: str):
        """ Get the date the VOD has been live-streamed at. """

        vod_url = "https://api.twitch.tv/v5/videos/{}".format(vod_id)
        response = requests.get(url=vod_url, headers=headers)
        return "".join(response.json()["created_at"][:10])

    @property
    def get_first_comment(self) -> tuple[str, str, str]:
        # return self.cleaned_comments[0] if self.cleaned_comments else None  # return first comment data
        # or
        return self.first_comment

    @property
    def get_last_comment(self) -> tuple[str, str, str]:
        # return self.cleaned_comments[-1] if self.cleaned_comments else None  # return last comment data
        # or
        return self.last_comment

    def clean_and_process_comments(self, save_as_json: bool = True, dirpath: str = None) -> list[tuple[str, str, str]]:
        """ Cleans the raw_comments provided. Here we go through the dictionary and extract only the comment data.
    def get_comments(self, save_as_json: bool = True, dirpath: Union[str, pathlib.Path] = None) -> list[tuple[str, str, str]]:
        """ Cleans the raw_comments. Here we go through the dictionary and extract only the comment data.

            Meaning: user name, when it was posted, and the body/text of the chat comment.

            :param save_as_json specify if the raw data should be saved as JSON
            :param dirpath the path pointing to a directory where the output file(s) should be saved. Can be
            either a str or a pathlib.Path object. Defaults to None (os.getcwd() will be used).
        """

        # base file name which we use for our output files
        file_name = "VOD_{}_{}.{}"  # 1. vod_id, 2. CHAT or RAW, 3. file extension
        # if no filepath specified, we simply write in the current dir (else block)
        # if a filepath has been specified (if block), we append our file_name to the path
        # TODO: - make it an actual Path object, so we can check if the file path is a directory and
        #           if so, we then create a new text file inside that directory, or something like this
        filepath = dirpath + "\\" + file_name if dirpath else file_name

        _raw_comments = self.get_raw_chat_comments_from_vod()
        filepath = _validate_path(provided_path=dirpath) if dirpath else pathlib.Path(getcwd())

        _raw_comments = self._get_raw_chat_comments_from_vod()  # Generator

        # create a .txt file to dump the comment data into
        # we don't care if we overwrite existing files
        with open(filepath.format(self.vod_id, "CHAT", "txt"), mode="w", encoding="utf-8") as file:
        # https://stackoverflow.com/questions/47518669/create-new-folder-in-python-with-pathlib-and-write-files-into-it
        chat_filepath = filepath / file_name.format(self.vod_id, "CHAT", "txt")
        with chat_filepath.open(mode="w", encoding="utf-8") as c_file:
            for comment_dict in _raw_comments:  # for each dict (i.e. yield) we have in our generator
                for comment_data_list_of_dicts in comment_dict["comments"]:  # list of dicts in the overall comment_dict

                    created_at = comment_data_list_of_dicts["created_at"]
                    commenter = comment_data_list_of_dicts["commenter"]["display_name"]  # or "name" key value
                    message = comment_data_list_of_dicts["message"]["body"]

                    file.write("{:<30} {:<30} {}\n".format(created_at, commenter, message))
                    c_file.write("{:<30} {:<30} {}\n".format(created_at, commenter, message))

                    # we now have the needed comment data, which we store in a tuple which is itself stored in the
                    # 'cleaned_comments' class instance variable
                    needed_comment_data = (created_at, commenter, message)
                    self.cleaned_comments.append(needed_comment_data)

            # set the first and last comment
            self.first_comment = self.cleaned_comments[0]
            self.last_comment = self.cleaned_comments[-1]

            # additional data which might be of interest
            date_of_stream = self.get_vod_date(vod_id=self.vod_id)
            channel_id = comment_data_list_of_dicts["channel_id"]
            name, views, followers, broadcaster_type = self._get_channel(channel_id=channel_id)
            # TODO: not using it anymore, because file is overwriting with seek, gotta do it differently maybe
            amt_of_comments = len(self.cleaned_comments)

            # now we add some additional data into the top of the .txt file (i.e. first/last comment, VOD ID,
            # now we add some additional data at the end of the .txt file (i.e. first/last comment, VOD ID,
            # date of stream, streamer name, etc.
            # go back to the beginning, overwrites shizzle and all, don't wanna bother "fixing" this shit
            # file.seek(0)
            file.write("\n\n\n\n"
                       "Date of Stream: {date}\n"
                       "Streamer: {name}\n"
                       "\tChannel ID: {channel_id}\n"
                       "\tChannel views: {views}\n"
                       "\tFollowers: {followers}\n"
                       "\tBroadcaster type: {broadcaster_type}\n"
                       "VOD ID: {vod}\n"
                       "Amount of comments: {amount}\n"
                       "First comment: {first}\n"
                       "Last comment: {last}"  # \n\n"
                       .format(date=date_of_stream,
                               name=name,
                               channel_id=channel_id,
                               views=views,
                               followers=followers,
                               broadcaster_type=broadcaster_type,
                               vod=self.vod_id,
                               amount=amt_of_comments,
                               first=self.first_comment,  # self.get_first_comment(),
                               last=self.last_comment,  # self.get_last_comment()
                               )
                       )
            c_file.write("\n\n\n\n"
                         "Date of Stream: {date}\n"
                         "Streamer: {name}\n"
                         "\tChannel ID: {channel_id}\n"
                         "\tChannel views: {views}\n"
                         "\tFollowers: {followers}\n"
                         "\tBroadcaster type: {broadcaster_type}\n"
                         "VOD ID: {vod}\n"
                         "Amount of comments: {amount}\n"
                         "First comment: {first}\n"
                         "Last comment: {last}"  # \n\n"
                         .format(date=date_of_stream,
                                 name=name,
                                 channel_id=channel_id,
                                 views=views,
                                 followers=followers,
                                 broadcaster_type=broadcaster_type,
                                 vod=self.vod_id,
                                 amount=amt_of_comments,
                                 first=self.get_first_comment,
                                 last=self.get_last_comment,
                                 )
                         )

        # additionally save the raw comment JSON data we extracted from the Twitch API
        # we also don't care here if we overwrite existing files as well
        if save_as_json:
            # json.dump(obj=self.raw_comments, fp=open(f"VOD_{self.vod_id}_RAW.json", "w"), indent=4)
            json_filepath = filepath / file_name.format(self.vod_id, "RAW", "json")
            json.dump(obj=self.raw_comments,
                      fp=open(filepath.format(self.vod_id, "RAW", "json"), mode="w"),
                      fp=json_filepath.open(mode="w"),
                      indent=4)

        return self.cleaned_comments

    def get_raw_chat_comments_from_vod(self) -> Generator:
        """ Gets the raw comments from the VOD. 'raw comments', because all the other 'junk' the request response gives
            us, has yet to be properly cleaned and only the relevant information extracted.

            For this cleaning, see the class method :meth:`clean_comments()`.
        """

        counter = 1
        _next = ""  # for our first request, we don't have a _next cursor, so we simply use an empty string
        while True:

            # make new request with the _next cursor, so we can get the next comments payload
            _request_response = requests.get(url=self.url, headers=headers, params={"cursor": _next})
            _json = _request_response.json()

            if _request_response.status_code != 200:
                msg_from_twitch = _json["message"]
                raise TwitchApiException(
                    "Twitch API responded with '{1}' (status code {0}). Expected 200 (OK)."
                    .format(_request_response.status_code, msg_from_twitch)
                )

            _next = _json.get("_next", 0)  # get the key, if not found default to 0

            # add the next/new batch of comments to the raw_comments, which we can later clean
            self.raw_comments[f"Batch {counter}"] = _json

            if _next == 0:  # if there are no more chat comments to fetch, we are done
                yield _json  # we yield the last _json here, because otherwise we don't process this last request
                break

            counter += 1

            yield _json

        # if we use a yield (i.e. a generator), the return statement will essentially be ignored
        # meaning, we cannot use the return values afterwards, because it is/stays the generator object
        # return self.raw_comments


#################################################################################################################
# Only run the following piece of code if the script is run directly, i.e. in a CLI environment (cmd/terminal). |
#################################################################################################################
if __name__ == "__main__":
    import sys
    from os import getcwd
    import pathlib

    import argparse

    parser = argparse.ArgumentParser(description="Get the chat comments from a VOD!")
    parser.add_argument("-vod", type=str, help="the VOD ID (Video ID) from the VOD")
    parser.add_argument("-dir", type=str, default=None, help="the directory path where the output is to be saved\n"
                                                             "If not provided, defaults to the directory "
                                                             "in which the script is located")
    args = parser.parse_args()

    vod = args.vod
    if not vod:
        print("Please rerun and specify a VOD ID via 'vodchat.py -vod VOD_ID'.")
        sys.exit(-1)
        # raise RuntimeError("Please rerun and specify a VOD ID via 'vodchat.py -vod VOD_ID'.")

    # TODO: pass the Path() object to the later processes
    fp = args.dir
    path = pathlib.Path(fp)
    if fp:  # if the -dir option has been specified
        print(path)
        path_exists = path.exists()
        is_file = path.is_file()
        # is_dir = path.is_dir()

        if not path_exists:  # if it is not a valid path (either to a directory or file)
            print("The supplied path does not exist.")
            sys.exit(-1)
            # raise RuntimeError("The supplied path does not exist.")

        # if not is_dir and if is_file are mutually exclusive (duh), so they don't really work together like this
        # if not is_dir:  # if it is not a valid directory
        #     print("Not a valid directory.")
        #     sys.exit(-1)
        #     raise RuntimeError("Not a valid directory.")
        if is_file:  # if it is a file
            print("The supplied path is a file. Please provide a directory (folder) path.")
            sys.exit(-1)
            # raise RuntimeError("The supplied path is a file.")
    # import argparse
    #
    # parser = argparse.ArgumentParser(description="Get the chat comments from a VOD!")
    # parser.add_argument("-vod", type=str, help="the VOD ID (Video ID) from the VOD")
    # parser.add_argument("-dir", type=str, default=None, help="the directory path where the output is to be saved\n"
    #                                                          "If not provided, defaults to the directory "
    #                                                          "in which the script is located")
    # args = parser.parse_args()
    #
    # vod = args.vod
    # if not vod:
    #     print("Please rerun and specify a VOD ID via 'vodchat.py -vod VOD_ID'.")
    #     sys.exit(-1)
    #
    # fp = args.dir

    fp = None
    fp = _validate_path(provided_path=fp) if fp else pathlib.Path(getcwd())

    # vod = "979245105"
    vod = "979245101"
    vodchat = VODChat(vod_id=vod)
    print("Getting VOD comments for VOD '{}'...".format(vod))
    print("Writing the output into the following directory: {}".format(fp))

    # get the raw comments and clean them, we don't care here about the return values
    clean = vodchat.get_comments(save_as_json=True, dirpath=fp)

    # clean = vodchat.clean_and_process_comments(save_as_json=True, filepath=fp)
    # print("Comments extracted: ", len(clean))
    # print("See the following files in the '{_dir}' directory: ".format(_dir=fp if fp else getcwd()))
    # print("- VOD_{}_CHAT.txt for the extracted comments (and additional channel information)."
    #       "\n- VOD_{}_RAW.json for the raw data.".format(vod, vod))
    amt_comments = len(clean)
    print("Comments extracted: ", amt_comments)
    if amt_comments:  # > 0:
        print("See the following files in the mentioned directory: ")
        print("- VOD_{}_CHAT.txt for the extracted comments (and additional channel information)."
              "\n- VOD_{}_RAW.json for the raw data.".format(vod, vod))
    else:
        print("No comments for this VOD available. Specify a different VOD ID.")
