import os
import sys
import pathlib

from .vodchat import VODChat
from .utils import validate_path


class VOD:
    def __init__(self, vod_id):
        self.vod_id = vod_id

    def get_vodchat(self) -> VODChat:
        vod_chat = VODChat(vod_id=self.vod_id)

        return vod_chat


#################################################################################################################
# Only run the following piece of code if the script is run directly, i.e. in a CLI environment (cmd/terminal). |
#################################################################################################################
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Get the chat comments from a VOD!")
    parser.add_argument("-vod", type=str, help="the VOD ID (Video ID) from the VOD")
    parser.add_argument("-dir", type=str, default=None, help="the directory path where the output is to be saved\n"
                                                             "If not provided, defaults to the directory "
                                                             "in which the script is located")
    args = parser.parse_args()

    _vod_id = args.vod
    if not _vod_id:
        print("Please rerun and specify a VOD ID via 'vodchat.py -vod VOD_ID'.")
        sys.exit(-1)

    fp = args.dir
    fp = validate_path(provided_path=fp) if fp else pathlib.Path(os.getcwd())

    # get a VOD
    vod = VOD(vod_id=_vod_id)
    print("Getting VOD comments for VOD '{}'...".format(_vod_id))
    print("Writing the output into the following directory: {}".format(fp))

    # get the VODChat associated with the VOD
    vodchat = vod.get_vodchat()

    # get the comments associated with the VODChat (returns an empty list if none found)
    comments = vodchat.get_comments()

    # get the raw comments in JSON format
    # - should only be called after .get_comments(), as the .get_comments() method is responsible for the calling of the
    # request logic
    # if called before, a empty dict() will be returned
    # if there are no comments available, the request response in JSON format will be returned
    raw_comments = vodchat.raw  # or vodchat.raw_comments

    # write the output to the file(s)
    # - should only be called after .get_comments(), otherwise no comments are there to write
    vodchat.to_file()

    amt_comments = len(comments)
    print("Comments extracted: ", amt_comments)
    if amt_comments:  # > 0:
        print("See the following files in the mentioned directory: ")
        print("- VOD_{}_CHAT.txt for the extracted comments (and additional channel information)."
              "\n- VOD_{}_RAW.json for the raw data.".format(_vod_id, _vod_id))
    else:
        print("No comments for this VOD available. Specify a different VOD ID.")
