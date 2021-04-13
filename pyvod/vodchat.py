from os import getenv
import json
from typing import Generator

import requests

import dotenv

# with trying to use it at the inbuilt Terminal here in PyCharm (and prob otherwise) these imports here are failing
# but if we simply use pyinstaller and make it an .exe, then we should be gucci anyway (can be hingeklatscht in GitHub
# as part of a release) - i.e. either use it manually or use it as a Python package/module
# from pyvod.exceptions import TwitchApiException
# from .exceptions import TwitchApiException

# https://dev.twitch.tv/docs/v5
base_url = "https://api.twitch.tv/v5/videos/{}/comments?limit=10000"  # videos/979245105/ for example

# required headers for the API requests
dotenv.load_dotenv()  # no path speficication necessary, if .env file is simply called ".env", otherwise path needed
headers = {"client-id": getenv("client-id"), "accept": "application/vnd.twitchtv.v5+json"}


# TODO: - possibly think about yielding each extracted batch of comments and processing them one after another, instead
#           of waiting for all the requests to finish and then starting with the processing process (i.e. writing, etc.)
#           with this, we don't theoretically need to "clean" the batches of requests as we do now, but simply process
#           them and we gucci
#           we can, with this approach, still store all the requests (i.e. the raw data) as we do now and then
#           afterwards dump it into a additional .json file
#       - write the extracted "clean" data for each comment into a new separate list (or better yet dictionary, 1...X)
#           and return this as the 'cleaned_comments' class instance attribute
#           this 1. makes more sense, 2. we then don't need to do any other extraction really from this data, if we want
#           to use it at some point somewhere else, etc.


class TwitchApiException(Exception):
    """ An exception for when the Twitch API response fails / does not respond with status code 200. """
    pass


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
            raise ValueError("'vod_id' required.")
        self.vod_id = str(vod_id)  # cast it so string, just to be safe
        self.cleaned_comments = list()  # None
        self.raw_comments = dict()  # None

        self.url = base_url.format(self.vod_id)

        # first and last comment of the VOD
        # contains both the user name and the timestamp (when the chat comment was sent)
        self.first_comment = None  # tuple()  # None
        self.last_comment = None  # tuple()  # None

    @staticmethod
    def _get_channel(channel_id: str) -> tuple[str, int, int, str]:
        """ Get the channel for the specified channel ID. Also fetches additional data, such as the amount of
            followers of the channel, the name of the channel, the amount of views and if the broadcaster type.
        """

        channel_url = "https://api.twitch.tv/v5/channels/{channel_id}".format(channel_id=channel_id)
        response = requests.get(url=channel_url, headers=headers).json()
        print(response)

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

    def get_first_comment(self) -> tuple[str, str, str]:
        # return self.cleaned_comments[0] if self.cleaned_comments else None  # return first comment data
        # or
        return self.first_comment

    def get_last_comment(self) -> tuple[str, str, str]:
        # return self.cleaned_comments[-1] if self.cleaned_comments else None  # return last comment data
        # or
        return self.last_comment

    def clean_and_process_comments(self, save_as_json: bool = True) -> list[tuple[str, str, str]]:
        """ Cleans the raw_comments provided. Here we go through the dictionary and extract only the comment data.

            If no raw_comments have been provided, we use the class 'self.raw_comments' instead.

            Meaning: user name, when it was posted, and the body/text of the chat comment.
        """

        _raw_comments = self.get_raw_chat_comments_from_vod()

        # create a .txt file to dump the comment data into
        # we don't care if we overwrite existing files
        with open(f"VOD_{self.vod_id}_CHAT.txt", "w", encoding="utf-8") as file:
            for comment_dict in _raw_comments:  # for each dict (i.e. yield) we have in our generator
                for comment_data_list_of_dicts in comment_dict["comments"]:  # list of dicts in the overall comment_dict

                    created_at = comment_data_list_of_dicts["created_at"]
                    commenter = comment_data_list_of_dicts["commenter"]["display_name"]  # or "name" key value
                    message = comment_data_list_of_dicts["message"]["body"]

                    file.write("{:<30} {:<30} {}\n".format(created_at, commenter, message))

                    # we now have the needed comment data, which we store in a tuple which is itself stored in the
                    # 'cleaned_comments' class instance variable
                    needed_comment_data = (created_at, commenter, message)
                    self.cleaned_comments.append(needed_comment_data)

            # set the first and last comment
            self.first_comment = self.cleaned_comments[0]
            self.last_comment = self.cleaned_comments[-1]

            # additional data which might be of interest
            channel_id = comment_data_list_of_dicts["channel_id"]
            name, views, followers, broadcaster_type = self._get_channel(channel_id=channel_id)
            # TODO: not using it anymore, because file is overwriting with seek, gotta do it differently maybe
            amt_of_comments = len(self.cleaned_comments)

            # now we add some additional data into the top of the .txt file (i.e. first/last comment, VOD ID,
            # date of stream, streamer name, etc.
            # go back to the beginning, overwrites shizzle and all, don't wanna bother "fixing" this shit
            # file.seek(0)
            file.write("\n\n\n\n"
                       "Date of Stream: {date}\n"  # TODO: get actual date of stream
                       "Streamer: {name}\n"
                       "\tChannel ID: {channel_id}\n"
                       "\tChannel views: {views}\n"
                       "\tFollowers: {followers}\n"
                       "\tBroadcaster type: {broadcaster_type}\n"
                       "VOD ID: {vod}\n"
                       "Amount of comments: {amount}\n"
                       "First comment: {first}\n"
                       "Last comment: {last}"  # \n\n"
                       .format(date="Now",
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

        # additionally save the raw comment JSON data we extracted from the Twitch API
        # we also don't care here if we overwrite existing files as well
        if save_as_json:
            json.dump(obj=self.raw_comments, fp=open(f"VOD_{self.vod_id}_RAW.json", "w"), indent=4)

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


if __name__ == "__main__":
    # import sys
    # import argparse
    #
    # parser = argparse.ArgumentParser(description="Get the chat comments from a VOD!")
    # parser.add_argument("-vod", type=str, help="the VOD ID (Video ID) from the VOD")
    # args = parser.parse_args()
    #
    # vod_id = args.vod
    # if not vod_id:
    #     raise RuntimeError("Please rerun and specify a VOD ID via 'vodchat.py -vod VOD_ID'.")

    _vod_id = "979245105"
    vodchat = VODChat(vod_id=_vod_id)

    first = vodchat.get_first_comment()
    last = vodchat.get_last_comment()
    print(first)
    print(last)

    # get the raw comments and clean them, we don't care here about the return values
    # vodchat.get_raw_chat_comments_from_vod()
    clean = vodchat.clean_and_process_comments(save_as_json=True)
    first = vodchat.get_first_comment()
    last = vodchat.get_last_comment()
    print(first)
    print(last)

    print(len(clean))
