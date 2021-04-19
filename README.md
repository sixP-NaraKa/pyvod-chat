# pyvod-chat
 Get the stream chat for a given Twitch VOD.
 
 pyvod can be used within your own programs via `pip install pyvod-chat`. 
 See [Usages](https://github.com/sixP-NaraKa/pyvod-chat#usage) for how to use it.
 
 pyvod can additionally be used as a `CLI` (command line interface) script (cmd/terminal).
 See [Usages](https://github.com/sixP-NaraKa/pyvod-chat#usage) for more information.
 
 
 See the [documentation section](https://github.com/sixP-NaraKa/pyvod-chat#documentation) for more information on the available methods.
 
 ## Requirements
 Also see [requirements.txt](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/requirements.txt).
 - Python 3.5+ required (only tested on 3.5+)
 - [requests](https://github.com/psf/requests) >= 2.20.0
 - [python-dotenv](https://github.com/theskumar/python-dotenv) >= 0.10.0
 
 If you want to run pyvod from a command line interface, you can install the required packages
 via `pip install -r requirements.txt`.
 
 ## Installation (PyPI)
 
 Available on PyPI.
 
 `pip install pyvod-chat`
 
 ## Usage
 
 ### 1. within your own program
 
 ```python
import pyvod  # or -> from pyvod import VOD

vod_id = "111111111"
vod = pyvod.VOD(vod_id=vod_id)  # VOD instance, the main entry point

vodchat = vod.get_vodchat()  # get a VODChat instance, contains the VOD chat

# fetches the comments from the VOD
# this returns a list containing VODCleanedComment (tuples) objects,
# which only contain the 'name', 'timestamp' and 'message' of a comment
comments = vodchat.get_comments()

# if the raw comment data (JSON) is needed, simply fetch them like so
# and process the JSON as you need it
raw_comments = vodchat.raw

# since VODCleandedComment objects are tuples,
# there are 2 distinct ways to extract their data from the comments list

# 1. by calling the class property attributes
for comment in comments:
    name = comment.name
    timestamp = comment.timestamp
    message = comment.message

# 2. via simple tuple unpacking
for timestamp, name, message in comments:
    # process comment data
    print(timestamp, name, message)

# if you want to access the VODChat comments again at a later date,
# but do not want to fetch them again,
# simply use the property attribute like so
comments = vodchat.comments
 ```

### 2. as a CLI tool in a terminal/cmd

Download the available GitHub folder by clicking on "Code" in the top right (or simply clone the repository).

Open your terminal and navigate to the root directory: `pyvod-chat`
# TODO: continue

INSERT PICTURE, OR GIF, HERE (new "resources/images/" folder, and link the GitHub url path here)

## Documentation
See the documentation here on GitHub: [documentation page](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_documentation.md).

## Changelog
See the changelog here on GitHub: [changelog page](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_changelog.md).

## License
MIT License. See [LICENSE](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/LICENSE).
