import requests


# https://dev.twitch.tv/docs/v5
base_url = "https://api.twitch.tv/v5/videos/{}/comments"  # videos/979245105/ for example

# required headers for the API requests
headers = {"client-id": "ENTER ID HERE", "accept": "application/vnd.twitchtv.v5+json"}


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

    @property
    def vod_chat_comments(self):
        return self.cleaned_comments

    @staticmethod
    def clean_comments(raw_comments: dict):
        """ Cleans the raw_comments provided. Here we go through the dictionary and extract only the comment data.

            Meaning: user name, when it was posted, and the body/text of the chat comment.
        """
        return NotImplementedError

    def get_raw_chat_comments_from_vod(self):
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
            _next = _json.get("_next", 0)  # get the key, if not found default to 0

            print(_json)
            print(_next)
            print()

            # add the next/new batch of comments to the raw_comments, which we can later clean
            self.raw_comments[f"Batch {counter}"] = _json

            if _next == 0:  # if there are no more chat comments to fetch, we are done
                break

            counter += 1

        return self.raw_comments
