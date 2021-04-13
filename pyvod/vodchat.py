from os import getenv
import json

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

    def __init__(self, vod_id: str):  # , raw_comments=None):
        if not vod_id:
            raise ValueError("'vod_id' required.")
        self.vod_id = str(vod_id)  # cast it so string, just to be safe
        self.cleaned_comments = None
        self.raw_comments = dict()  # if raw_comments is None else raw_comments

        self.url = base_url.format(self.vod_id)

        # first and last comment of the VOD
        # contains both the user name and the timestamp (when the chat comment was sent)
        self.first_comment = tuple()
        self.last_comment = tuple()

    def get_vod_chat_comments(self):
        return self.cleaned_comments

    def clean_comments(self, provided_raw_comments: dict = None, save_as_json: bool = True) -> list:
        """ Cleans the raw_comments provided. Here we go through the dictionary and extract only the comment data.

            If no raw_comments have been provided, we use the class 'self.raw_comments' instead.

            Meaning: user name, when it was posted, and the body/text of the chat comment.
        """

        if not provided_raw_comments:  # if no raw comments have been provided, using the class instance raw_comments
            provided_raw_comments = self.raw_comments
        # print(provided_raw_comments)

        # only get the 'comments' keys/values out of the raw data, only those are of interest here
        # needed_comment_data = [{"comments": raw_comments[batch]["comments"] for batch in raw_comments.keys()}]
        self.cleaned_comments = [provided_raw_comments[batch]["comments"] for batch in provided_raw_comments.keys()]

        # create a .txt file to dump the comment data into
        # we don't care if we overwrite existing files
        with open(f"VOD_{self.vod_id}_CHAT.txt", "w", encoding="utf-8") as file:
            for comment_list in self.cleaned_comments:  # for each list of comments
                for comment_data_dict in comment_list:  # for each dictionary in the comment_list

                    created_at = comment_data_dict["created_at"]
                    commenter = comment_data_dict["commenter"]["display_name"]  # or we take the "name" key value
                    message = comment_data_dict["message"]["body"]

                    file.write("{:<30} {:<30} {}\n".format(created_at, commenter, message))

        # additionally save the raw comment JSON data we extracted from the Twitch API
        # we also don't care here if we overwrite existing files as well
        if save_as_json:
            json.dump(obj=provided_raw_comments, fp=open(f"VOD_{self.vod_id}_RAW.json", "w"), indent=4)

        return self.cleaned_comments

    def get_raw_chat_comments_from_vod(self) -> dict:
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

            # print(_json)
            # print(_next)
            # print()

            # add the next/new batch of comments to the raw_comments, which we can later clean
            self.raw_comments[f"Batch {counter}"] = _json

            if _next == 0:  # if there are no more chat comments to fetch, we are done
                break

            counter += 1

        return self.raw_comments


if __name__ == "__main__":
    # import sys
    import argparse

    parser = argparse.ArgumentParser(description="Get the chat comments from a VOD!")
    parser.add_argument("-vod", type=str, help="the VOD ID (Video ID) from the VOD")
    args = parser.parse_args()

    vod_id = args.vod
    if not vod_id:
        raise RuntimeError("Please rerun and specify a VOD ID via 'vodchat.py -vod VOD_ID'.")

    vodchat = VODChat(vod_id=vod_id)

    # get the raw comments and clean them, we don't care here about the return values
    vodchat.get_raw_chat_comments_from_vod()
    vodchat.clean_comments(save_as_json=True)
