"""
pyvod-chat - a simple tool to download a past Twitch.tv broadcasts (VOD) chat comments!

Available on GitHub (+ documentation): https://github.com/sixP-NaraKa/pyvod-chat
"""


from .vodchat import VODChat


class VOD:
    """ Represents a Twitch.tv VOD (video-on-demand).

        The main entry point, is solely responsible for getting the VODChat via `get_videochat()`.

        :param vod_id: the VOD ID to fetch the information for
    """

    def __init__(self, vod_id):
        self.vod_id = str(vod_id)

    def get_vodchat(self) -> VODChat:
        vod_chat = VODChat(vod_id=self.vod_id)

        return vod_chat
