from typing import NamedTuple


class VODCleanedComment(NamedTuple):
    """ This class represents a simple cleaned comment.

        Each VODCleanedComment instance consists of:

        - the `timestamp` of the message

        - the `name` of the user who wrote the message

        - the `message` body

        These attributes can be simply called via class instance `comment.attribute`
    """

    timestamp: str
    name: str
    message: str

    def __repr__(self):
        return "<VODComment timestamp={0.timestamp!r} name={0.name!r} message={0.message!r}>".format(self)
