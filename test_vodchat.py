# from pyvod import VODChat
import pyvod

# vod id (video ID)
vod = "979245105"  # 979245105

# create instance of VODChat with the VOD ID
vodchat = pyvod.VODChat(vod_id=vod)

# get the raw comments from the VOD
raw_comments = vodchat.get_raw_chat_comments_from_vod()
print(raw_comments.keys())
keys = list(raw_comments.keys())  # cast .keys() to list, so we can use it below
assert keys[0] == "Batch 1", "No key with 'Batch 1' found."
# will have to see if in a VOD with no comments, we still have such "Batches" (should have), but still look at such
# a request, at least see if we can reproduce such a request, we there are no comments for the duration of the Batch
# etc. pp.

vodchat.get_comments()
