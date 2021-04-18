import os
from typing import Generator, Union
import json

import requests
import pathlib
import dotenv

from .vodcomment import VODCleanedComment
from .utils import validate_path
from .exceptions import TwitchApiException

# check for a .env file and get the "client-id" Twitch API key
# if there is no such key or it is empty, we use a default key
dotenv.load_dotenv()
client_id = os.getenv("client-id")
client_id = client_id if client_id else "jzkbprff40iqj646a697cyrvl0zt2m6"

base_url = "https://api.twitch.tv/v5/videos/{}/comments"  # videos/979245105/ for example
headers = {"client-id": client_id, "accept": "application/vnd.twitchtv.v5+json"}


class VODChat:
    """ A class which represents the VOD stream chat. We store here both the 'raw_comment' data (i.e. the JSON) for
        and the 'cleaned_comments'.

        There should be no need to create a instance of this class manually.
    """

    def __init__(self, vod_id: str):
        self.vod_id = vod_id

        self.vod_comments = list()  # the cleaned comments
        self.raw_comments = dict()  # the comments in still raw form (JSON)

        # request base url for requesting VOD comment data
        self.url = base_url.format(self.vod_id)

        # a flag we set if the first request response contains an empty "comments" list value
        self._no_first_comments_response = False

    @property
    def comments(self) -> list:
        return self.vod_comments

    @property
    def raw(self) -> dict:
        return self.raw_comments

    @staticmethod
    def _get_channel(channel_id: str) -> tuple:
        """ Get the channel for the specified channel ID. Also fetches additional data, such as the amount of
            followers of the channel, the name of the channel, the amount of views and the broadcaster type.
        """

        channel_url = "https://api.twitch.tv/v5/channels/{channel_id}".format(channel_id=channel_id)
        response = requests.get(url=channel_url, headers=headers).json()

        return response["display_name"], response["views"], response["followers"], response["broadcaster_type"]

    @staticmethod
    def _get_vod_date(vod_id: str) -> tuple:
        """ Get the date the VOD has been live-streamed at (and the channel ID for further use). """

        vod_url = "https://api.twitch.tv/v5/videos/{}".format(vod_id)
        response = requests.get(url=vod_url, headers=headers).json()
        return "".join(response["created_at"][:10]), response["channel"]["_id"]

    def _extract_comments(self) -> Generator:
        """ Gets the raw comments from the VOD. 'raw comments', because all the other 'junk' the request response gives
            us, has yet to be properly cleaned and only the relevant information extracted.

            For this cleaning and processing, see the class method :meth:`get_comments()`.
        """

        counter = 1
        _next = ""  # for our first request, we don't have a _next cursor, so we simply use an empty string
        while True:

            # make new request with the _next cursor, so we can get the next comments payload
            _request_response = requests.get(url=self.url, headers=headers, params={"cursor": _next})
            _json_body = _request_response.json()

            if _request_response.status_code != 200:
                msg_from_twitch = _json_body["message"]
                raise TwitchApiException(
                    "Twitch API responded with '{1}' (status code {0}). Expected 200 (OK)."
                    .format(_request_response.status_code, msg_from_twitch)
                )

            # if the first response contains a empty list of "comments",
            # we set our flag to let the program know to stop trying to extract more comments
            if counter == 1 and not _json_body["comments"]:
                self._no_first_comments_response = True

            _next = _json_body.get("_next", 0)  # get the key, if not found default to 0

            # add the next/new batch of comments to the raw_comments, which we can later clean
            self.raw_comments["Batch {}".format(counter)] = _json_body

            counter += 1

            yield _json_body

            if _next == 0:  # if there are no more chat comments to fetch, we are done
                break

    def get_comments(self) -> list:
        """
        Cleans the raw_comments. Here we go through the dictionary and extract only the needed comment data.

        Meaning: user name, when it was posted, and the body/text of the chat comment.

        If the raw data is wanted (JSON),
        simply call the class instance attribute `raw_comments` or its property `raw`.

        :return: the extracted comments from the raw data - these are VODCleanedComment instances (tuples)
                 with additional property attributes (name, timestamp, message)
        """

        _raw_comments = self._extract_comments()  # Generator with the raw comments (batch for batch)

        for comment_dict in _raw_comments:  # for each dict (i.e. yield) we have in our generator
            if self._no_first_comments_response:  # if True, no comment data is available
                return self.comments
            for comment_data_list_of_dicts in comment_dict["comments"]:  # list of dicts in the overall comment_dict

                created_at = comment_data_list_of_dicts["created_at"]
                commenter = comment_data_list_of_dicts["commenter"]["display_name"]  # or "name" key value
                message = comment_data_list_of_dicts["message"]["body"]

                # we now have the needed comment data, which we store in a tuple VODCleanedComments,
                # which is itself stored in the 'vod_comments' class instance variable, which holds all the comments
                comment_data = VODCleanedComment((created_at, commenter, message))
                self.vod_comments.append(comment_data)

        return self.comments

    def to_file(self, dirpath: Union[pathlib.Path, str] = None, save_json: bool = True) -> None:
        """
        Saves the cleaned vod comment data in a plain .txt file.
        The raw JSON data can additionally be saved in a separate .json file, if `save_json` is set (default behavior).

        Only a valid directory path pointing to a folder is allowed.

        :param dirpath: the path pointing to a directory in which the file(s) are to be saved.
                        Defaults to the current working directory as returned by `os.getcwd()`
        :param save_json: whether or not a separate .json file containing the raw JSON data should be created

        :raises DirectoryDoesNotExistError | DirectoryIsAFileError: if either the path does not exist,
                                                                    or the path points to a file
        """

        # base file name which we use for our output files
        file_name = "VOD_{}_{}.{}"  # 1. vod_id, 2. CHAT or RAW, 3. file extension

        # handle the supplied directory path, if needed
        directory_path = validate_path(provided_path=dirpath) if dirpath else pathlib.Path(os.getcwd())

        chat_filepath = directory_path / file_name.format(self.vod_id, "CHAT", "txt")
        with chat_filepath.open(mode="w", encoding="utf-8") as c_file:

            for created_at, commenter, message in self.vod_comments:
                c_file.write("{:<30} {:<30} {}\n".format(created_at, commenter, message))

            # additional data which might be of interest
            date_of_stream, channel_id = self._get_vod_date(vod_id=self.vod_id)
            name, views, followers, broadcaster_type = self._get_channel(channel_id=channel_id)
            amt_of_comments = len(self.vod_comments)

            # now we add some additional data at the end of the .txt file
            # (i.e. VOD ID, date of stream, streamer name, etc.)
            c_file.write("\n\n\n\n"
                         "Date of Stream: {date}\n"
                         "Streamer: {name}\n"
                         "\tChannel ID: {channel_id}\n"
                         "\tChannel views: {views}\n"
                         "\tFollowers: {followers}\n"
                         "\tBroadcaster type: {broadcaster_type}\n"
                         "VOD ID: {vod}\n"
                         "Amount of comments: {amount}\n"
                         .format(date=date_of_stream,
                                 name=name,
                                 channel_id=channel_id,
                                 views=views,
                                 followers=followers,
                                 broadcaster_type=broadcaster_type,
                                 vod=self.vod_id,
                                 amount=amt_of_comments,
                                 )
                         )

        # additionally save the raw comment JSON data we extracted from the Twitch API
        # we also don't care here if we overwrite existing files as well
        if save_json:
            json_filepath = directory_path / file_name.format(self.vod_id, "RAW", "json")
            json.dump(obj=self.raw_comments,
                      fp=json_filepath.open(mode="w"),
                      indent=4)
