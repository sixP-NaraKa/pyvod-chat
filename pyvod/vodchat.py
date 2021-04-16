from os import getenv, getcwd
import json
from typing import Generator, Union

import requests
import dotenv
import pathlib

# from pyvod.exceptions import TwitchApiException
# from .exceptions import TwitchApiException

# https://dev.twitch.tv/docs/v5
base_url = "https://api.twitch.tv/v5/videos/{}/comments"  # videos/979245105/ for example

# required headers for the API requests
dotenv.load_dotenv()
headers = {"client-id": getenv("client-id"), "accept": "application/vnd.twitchtv.v5+json"}


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
    """

    def __init__(self, vod_id: str):
        if not vod_id:  # if the supplied vod_id is empty
            raise ValueError("'vod_id' required.")
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

    def get_comments(self, save_as_json: bool = True, dirpath: Union[str, pathlib.Path] = None) -> list[tuple[str, str, str]]:
        """ Cleans the raw_comments. Here we go through the dictionary and extract only the comment data.

            Meaning: user name, when it was posted, and the body/text of the chat comment.

            :param save_as_json specify if the raw data should be saved as JSON
            :param dirpath the path pointing to a directory where the output file(s) should be saved. Can be
            either a str or a pathlib.Path object. Defaults to None (os.getcwd() will be used).
        """

        # base file name which we use for our output files
        file_name = "VOD_{}_{}.{}"  # 1. vod_id, 2. CHAT or RAW, 3. file extension

        filepath = _validate_path(provided_path=dirpath) if dirpath else pathlib.Path(getcwd())

        _raw_comments = self._get_raw_chat_comments_from_vod()  # Generator

        # create a .txt file to dump the comment data into
        # we don't care if we overwrite existing files
        # https://stackoverflow.com/questions/47518669/create-new-folder-in-python-with-pathlib-and-write-files-into-it
        chat_filepath = filepath / file_name.format(self.vod_id, "CHAT", "txt")
        with chat_filepath.open(mode="w", encoding="utf-8") as c_file:
            for comment_dict in _raw_comments:  # for each dict (i.e. yield) we have in our generator
                for comment_data_list_of_dicts in comment_dict["comments"]:  # list of dicts in the overall comment_dict

                    created_at = comment_data_list_of_dicts["created_at"]
                    commenter = comment_data_list_of_dicts["commenter"]["display_name"]  # or "name" key value
                    message = comment_data_list_of_dicts["message"]["body"]

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
            amt_of_comments = len(self.cleaned_comments)

            # now we add some additional data at the end of the .txt file (i.e. first/last comment, VOD ID,
            # date of stream, streamer name, etc.
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
            json_filepath = filepath / file_name.format(self.vod_id, "RAW", "json")
            json.dump(obj=self.raw_comments,
                      fp=json_filepath.open(mode="w"),
                      indent=4)

        return self.cleaned_comments


#################################################################################################################
# Only run the following piece of code if the script is run directly, i.e. in a CLI environment (cmd/terminal). |
#################################################################################################################
if __name__ == "__main__":
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

    clean = vodchat.get_comments(save_as_json=True, dirpath=fp)

    amt_comments = len(clean)
    print("Comments extracted: ", amt_comments)
    if amt_comments:  # > 0:
        print("See the following files in the mentioned directory: ")
        print("- VOD_{}_CHAT.txt for the extracted comments (and additional channel information)."
              "\n- VOD_{}_RAW.json for the raw data.".format(vod, vod))
    else:
        print("No comments for this VOD available. Specify a different VOD ID.")
