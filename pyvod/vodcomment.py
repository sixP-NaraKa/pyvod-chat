

class VODCleanedComment(tuple):
    """ This class represents a simple cleaned comment.

        Each VODCleanedComment instance contains of:

        - the `timestamp` of the message

        - the `name` of the user who wrote the message

        - the `message` body

        These attributes can be simply called via class instance `comment.attribute`
    """

    @property
    def timestamp(self):
        return self.__getitem__(0)

    @property
    def name(self):
        return self.__getitem__(1)

    @property
    def message(self):
        return self.__getitem__(2)
