"""
pyvod-chat - a simple tool to download a past Twitch.tv broadcasts (VOD) chat comments!

Available on GitHub (+ documentation): https://github.com/sixP-NaraKa/pyvod-chat
"""


import os
from collections import namedtuple

import requests
import dotenv

from .vodchat import VODChat
from .exceptions import TwitchApiException


# check for a .env file and get the "twitch-client-id" which we need to identify the application for use with the API
# this is NOT the same as the Client-Secret, which we do not need here
# if there is no such Client-ID or it is empty, we use a default Client-ID
dotenv.load_dotenv()
_client_id = os.getenv("twitch-client-id")
_client_id = _client_id if _client_id else "r52h1i1phlvyxs0sdi3ooam1b3w62g"

# needed request headers
_headers = {"client-id": _client_id, "accept": "application/vnd.twitchtv.v5+json"}

# additional API url
vod_url = "https://api.twitch.tv/v5/videos/{vod_id}"


class VOD:
    """ Represents a Twitch.tv VOD (video-on-demand).

        The main entry point, responsible for getting the VODChat via `get_videochat()`
        as well as some basic information about the VOD itself and the channel the VOD belongs to (see below).

        Additional Class Attributes
        -----

        The following are class attributes which contain basic information about the VOD and its associated channel.

        - `vod_title`:
                the title of the VOD
        - `vod_length`:
                the length of the VOD in hours
        - `vod_date`:
                the date when the broadcast has been streamed
        - `vod_views`:
                the total amount of VOD views
        - `channel`:
                the name of the channel associated with the VOD
        - `channel_id`:
                the channel ID
        - `channel_views`:
                total channel views
        - `channel_followers`:
                total channel followers
        - `channel_broadcaster_type`:
                whether the channel is partnered or a affiliate

        :param vod_id: the VOD ID to fetch the information for
    """

    def __init__(self, vod_id):
        self.vod_id = str(vod_id)

        self._basic_data = self._get_basic_data()

        self.vod_title = self._basic_data.title
        self.vod_length = self._basic_data.vod_length
        self.vod_date = self._basic_data.created_at
        self.vod_game = self._basic_data.game
        self.vod_views = self._basic_data.views
        self.channel = self._basic_data.channel_name
        self.channel_id = self._basic_data.channel_id
        self.channel_views = self._basic_data.channel_views
        self.channel_followers = self._basic_data.channel_followers
        self.channel_broadcaster_type = self._basic_data.channel_type

    def __repr__(self):
        return "<VOD vod_title={0.vod_title!r} vod_length={0.vod_length!r} vod_date={0.vod_date!r} " \
               "vod_game={0.vod_game!r} vod_views={0.vod_views!r} " \
               "channel={0.channel!r} channel_id={0.channel_id!r} channel_views={0.channel_views!r} " \
               "channel_followers={0.channel_followers!r} channel_broadcaster_type={0.channel_broadcaster_type!r}>"\
            .format(self)

    def _get_basic_data(self) -> namedtuple:
        """ Gets some basic information in regards to the VOD and the channel associated with the VOD.

            :return: the basic data as a `namedtuple`
        """

        response = requests.get(url=vod_url.format(vod_id=self.vod_id), headers=_headers)
        response_body = response.json()

        if response.status_code != 200:
            msg_from_twitch = response_body["message"]
            raise TwitchApiException(
                "Twitch API responded with '{1}' (status code {0}). Expected 200 (OK)."
                .format(response.status_code, msg_from_twitch)
            )

        BasicData = namedtuple("BasicData", "title views created_at game vod_length "
                                            "channel_name channel_id channel_date "
                                            "channel_views channel_followers channel_type"
                               )
        data = BasicData(
            response_body["title"],                      # VOD title
            response_body["views"],                      # VOD views
            response_body["created_at"],            # VOD stream date
            response_body["game"],                       # what game has been streamed
            response_body["length"],                     # VOD length in seconds (seconds / 3600 = hours)
            response_body["channel"]["display_name"],    # channel name (streamer name)
            response_body["channel"]["_id"],             # channel ID
            response_body["channel"]["created_at"],      # channel creation date
            response_body["channel"]["views"],           # total channel views
            response_body["channel"]["followers"],       # total channel followers
            response_body["channel"]["broadcaster_type"]  # broadcaster type (i.e. partner or affiliate, etc.)
        )
        data = data._replace(vod_length=round(float(data.vod_length) / 3600, 2))

        return data

    def get_vodchat(self) -> VODChat:
        """ Gets the VODChat associated with the `vod_id`.

            :return: the VODChat
        """
        vod_chat = VODChat(vod_id=self.vod_id, _basic_vod_data=self._basic_data, _headers=_headers)

        return vod_chat
