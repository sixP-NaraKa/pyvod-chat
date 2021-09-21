"""
pyvod-chat - a simple tool to download a past Twitch.tv broadcasts (VOD) chat comments!

Available on GitHub (+ documentation): https://github.com/sixP-NaraKa/pyvod-chat
"""


import os
from typing import Generator, Union
import json

import requests
import pathlib

from .vodcomment import VODSimpleComment
from .utils import validate_path, get_strptime
from .exceptions import TwitchApiException


# request base url
base_url = "https://api.twitch.tv/v5/videos/{}/comments"  # videos/979245105/comments for example


class VODChat:
    """ A class which represents the VOD stream chat. We store here both the 'raw comment' data (i.e. the JSON)
        `raw_comments` and the 'cleaned comments' `vod_comments`.

        There should be no need to create a instance of this class manually.

        Additional Class Attributes
        -----

        The following are class attributes which contain basic information about the VOD and its associated channel.

        - `vod_comments`:
                the VOD comments containing a the name, message and time of a comment (class VODSimpleComment)
        - `raw_comments`:
                the raw comments in JSON
        - `url`:
                the base url for the VOD requests

        :param vod_id: the VOD ID to fetch the information for
    """

    def __init__(self, vod_id: str, _basic_vod_data, _headers):
        self.vod_id = vod_id

        self._basic_data = _basic_vod_data

        self._headers = _headers

        self.vod_comments = list()  # the cleaned comments
        self.raw_comments = dict()  # the comments in still raw form (JSON)

        # request base url for requesting VOD comment data
        self.url = base_url.format(self.vod_id)

        # a flag we set if the first request response contains an empty "comments" list value
        self._no_first_comments_response = False

    def __repr__(self):
        return "<VODChat vod_id={0.vod_id!r} vod_comments={0.vod_comments!r} url={0.url!r}>".format(self)

    @property
    def comments(self) -> list:
        return self.vod_comments

    @property
    def raw(self) -> dict:
        return self.raw_comments

    def _extract_comments(self) -> Generator:
        """ Gets the raw comments from the VOD. 'raw comments', because all the other 'junk' the request response gives
            us, has yet to be properly cleaned and only the relevant information extracted.

            For this cleaning and processing, see the class method :meth:`get_comments()`.

            :return: Generator: yields the request responses .json()
        """

        counter = 1
        _next = ""  # for our first request, we don't have a _next cursor, so we simply use an empty string
        while True:

            # make new request with the _next cursor, so we can get the next comments payload
            _request_response = requests.get(url=self.url, headers=self._headers, params={"cursor": _next})
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
        Cleans the raw_comments. Here we go through the JSON and extract only the needed comment data.

        Meaning: user name, when it was posted, and the body/text of the chat comment.

        If the raw data is wanted (JSON),
        simply call the class instance attribute `raw_comments` or its property `raw`.

        :return: the extracted comments from the raw data - these are VODCleanedComment instances (tuples)
                 with additional property attributes (name, timestamp, message)
        """

        _raw_comments = self._extract_comments()  # Generator with the raw comments (batch for batch)

        # time when the livestream happened as a datetime.datetime object
        _vod_datetime = get_strptime(datetime_string=self._basic_data.created_at)

        for comment_dict in _raw_comments:  # for each dict (i.e. yield) we have in our generator
            if self._no_first_comments_response:  # if True, no comment data is available
                self.vod_comments = None
                return self.comments
            for comment_data_list_of_dicts in comment_dict["comments"]:  # list of dicts in the overall comment_dict

                created_at = comment_data_list_of_dicts["created_at"]
                commenter = comment_data_list_of_dicts["commenter"]["display_name"]  # or "name" key value
                message = comment_data_list_of_dicts["message"]["body"]

                # get the time the comment has been posted at
                # added in v0.2.0

                # time when the comment has been posted as a datetime.datetime object
                _comment_datetime = get_strptime(datetime_string=created_at)

                # subtract the the two datetime objects and
                # now we have the exact time the comment was posted in the chat
                posted_at = (_comment_datetime - _vod_datetime).__str__()[:7]  # only get the hours:minutes:seconds

                # we now have the needed comment data, which we store in a tuple VODSimpleComment,
                # which is itself stored in the 'vod_comments' class instance variable, which holds all the comments
                comment_data = VODSimpleComment(timestamp=created_at, posted_at=posted_at, name=commenter, message=message)
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

            # added in v0.2.0
            c_file.write("{:<30} {:<10} {:<30} {}\n".format("Created at", "Posted at", "User", "Message"))

            if self.vod_comments:  # if there are comments
                for created_at, posted_at, commenter, message in self.vod_comments:
                    c_file.write("{:<30} {:<10} {:<30} {}\n".format(created_at, posted_at, commenter, message))
            elif self.vod_comments is None:  # if we set vod_comments to None during extraction (no comments available)
                c_file.write("No comments available for this VOD.")
            else:  # if to_file() has been called before comments have been tried to be extracted from the VOD
                c_file.write("No comments have yet been extracted. Try `vodchat.get_comments()` first.")

            # additional data which might be of interest
            date_of_stream, channel_id = self._basic_data.created_at[:10], self._basic_data.channel_id
            name, views, followers, broadcaster_type = (self._basic_data.channel_name,
                                                        self._basic_data.channel_views,
                                                        self._basic_data.channel_followers,
                                                        self._basic_data.channel_type)
            amt_of_comments = len(self.vod_comments) if self.vod_comments else 0

            # now we add some additional data at the end of the .txt file
            # (i.e. VOD ID, date of stream, streamer name, etc.)
            c_file.write("\n\n\n\n"
                         "Date of Stream: {date} - {title} ({game})\n"
                         "\tStream length: {length} hours\n"
                         "Streamer: {name}\n"
                         "\tChannel ID: {channel_id}\n"
                         "\tChannel views: {views}\n"
                         "\tFollowers: {followers}\n"
                         "\tBroadcaster type: {broadcaster_type}\n"
                         "VOD ID: {vod}\n"
                         "Amount of comments: {amount}\n"
                         .format(date=date_of_stream,
                                 title=self._basic_data.title,
                                 game=self._basic_data.game,
                                 length=self._basic_data.vod_length,
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
