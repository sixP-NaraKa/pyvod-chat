"""
pyvod-chat - a simple tool to download a past Twitch.tv broadcasts (VOD) chat comments!

Available on GitHub (+ documentation): https://github.com/sixP-NaraKa/pyvod-chat
"""


from typing import NamedTuple


class VODSimpleComment(NamedTuple):
    """ This class represents a simple ("cleaned") comment.

        Each VODSimpleComment instance consists of:

        - the `timestamp` of the message

        - the `posted_at` time (when in the VOD the comment has been posted)
            -> added in v0.2.0

        - the `name` of the user who wrote the message

        - the `message` body

        These attributes can be simply called via class instance `comment.attribute`
    """

    timestamp: str
    posted_at: str
    name: str
    message: str

    def __repr__(self):
        return "<VODComment timestamp={0.timestamp!r} posted_at={0.posted_at!r} name={0.name!r} message={0.message!r}>".format(self)
