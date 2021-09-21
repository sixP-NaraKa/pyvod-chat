# pyvod-chat

![GitHub release (latest by date)](https://img.shields.io/github/v/release/sixp-naraka/pyvod-chat) ![PyPI](https://img.shields.io/pypi/v/pyvod-chat) ![PyPI - Downloads](https://img.shields.io/pypi/dd/pyvod-chat)
[![Downloads](https://pepy.tech/badge/pyvod-chat)](https://pepy.tech/project/pyvod-chat)

 Get the stream chat for a given Twitch VOD.
 
 pyvod can be used within your own programs via `pip install pyvod-chat`. 
 See [Usages](https://github.com/sixP-NaraKa/pyvod-chat#usage) for how to use it.
 
 pyvod can additionally be used as a `CLI` (command line interface) script (cmd/terminal).
 See [Usages](https://github.com/sixP-NaraKa/pyvod-chat#usage) for more information.
 
 
 See the [documentation section](https://github.com/sixP-NaraKa/pyvod-chat#documentation) for more information on the available methods.
 
 ## Requirements
 Also see [requirements.txt](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/requirements.txt).
 - Python 3.6+ required (tested on 3.6+)
 - [requests](https://github.com/psf/requests) >= 2.20.0
 - [python-dotenv](https://github.com/theskumar/python-dotenv) >= 0.10.0
 
 If you want to run pyvod from a command line interface, you can install the required packages
 via `pip install -r requirements.txt`.
 
### Optional
- an optional `.env` file containing your own Twitch.tv Client-ID insde the root directory of your project
(or if used via the CLI inside the `pyvod-chat` directory).

    Add the env-variable inside the .env file like so: `twitch-client-id="CLIENT_ID"`

A 'Client-ID' (public) is ***NOT*** the same as a 'Client-Secret', the latter which is not used here.

***Note***: if you don't specify a Client-ID, a **default Client-ID will be used**.
 
 ## Installation (PyPI)
 
 Available on [PyPI](https://pypi.org/project/pyvod-chat/).
 
 `pip install pyvod-chat`
 
 ## Usage
 
 **Note**: many comments == taking quite a while. With some barebone testing, **around 130.000 comments can take up to roughly 12-ish minutes** (around 2400 requests in total, 200-ish per minute).
 
 This is a result of how the Twitch API (v5) is providing the comments (each request comes with a `_next` param
 which its value HAS to be used in the next request to fetch the correct next comments),
 the more comments there are in the VOD, the more requests we have to make, which in turn takes more time.
 
 Currently trying multithreading/multiprocessing out, to see if it is possible to keep the "state" steady and speeding things up.
 
 
 ### 1. within your own program
 
 ```python
import pyvod  # or -> from pyvod import VOD

vod_id = "111111111"
vod = pyvod.VOD(vod_id=vod_id)  # VOD instance, the main entry point

vodchat = vod.get_vodchat()  # get a VODChat instance, contains the VOD chat

# fetches the comments from the VOD
# this returns a list containing VODSimpleComment (NamedTuple) objects,
# which only contain the 'name', 'timestamp', when the message has been posted and
# the 'message' content of a comment
comments = vodchat.get_comments()

# if the raw comment data (JSON) is needed, simply fetch them like so
# and process the JSON as you need it
raw_comments = vodchat.raw

# since VODSimpleComment objects are NamedTuples
# (can do anything a normal tuple does),
# there are 2 distinct ways to extract their data from the comments list

# 1. by calling the class attributes
for comment in comments:
    name = comment.name
    timestamp = comment.timestamp
    posted_at = comment.posted_at
    message = comment.message

# 2. via simple tuple unpacking
for timestamp, posted_at, name, message in comments:
    # process comment data
    print(timestamp, posted_at, name, message)

# if you want to access the VODChat comments again at a later date,
# but do not want to fetch them again from the API,
# simply use the property attribute like so
comments = vodchat.comments

# if you want to save the extracted comments and the raw JSON, simply do:
vodchat.to_file(dirpath="OPTIONAL\PATH\HERE", save_json=True)  # defaults to the current working directory via `os.getcwd()`
 ```

### 2. as a CLI tool in a terminal/cmd

Download the available GitHub folder by clicking on "Code" in the top right (or simply clone the repository).

Open your terminal and navigate to the root directory of: `pyvod-chat`

```commandline
cd pyvod-chat
python -m pyvod --help
```
`-h [--help]` shows you the usage and the optional -d [-dir] parameter allows you to specify your own output directory.
This defaults to the current working directory, i.e. wherever you saved the program: `..\..\pyvod-chat`

A full command line could be structured like so:
```commandline
python -m pyvod -v 979245105 -d C:\Users\MyUser\Documents\Scripts
```


## Documentation
See the documentation here on GitHub: [documentation page](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_documentation.md).

## Changelog
See the changelog here on GitHub: [changelog page](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_changelog.md).

## License
MIT License. See [LICENSE](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/LICENSE).

## Task list
- [ ] Potentially implement multithreading/multiprocessing for the comment fetch requests

- [ ] Make documentation available via [readthedocs](https://readthedocs.org/).

- [ ] Future features like filtering and sorting the comments by user, message (contains X word, etc.) and more
