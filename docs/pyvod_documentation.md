# Documentation

This documentation page shows the available library functions with which you can interact with.

The documentation is structured as follows:

| class     | purpose   |
   ---      |   ---     |
|  **[VOD](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_documentation.md#class-vod)** | main entry point |
| **[VODChat](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_documentation.md#class-vodchat)** | handles the fetching of chat comments and additional output saving (to .txt and .json) |
| **[VODSimpleComment](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_documentation.md#class-vodsimplecommentnamedtuple)** | represents a simple chat comment |

### Requirements
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

A 'Client-ID' (public) is NOT the same as a 'Client-Secret', the latter is not used here.

***Note***: if you don't specify a Client-ID, a **default Client-ID will be used**.

## **class `VOD`**

Represents a Twitch.tv VOD (video-on-demand).

The main entry point, is  responsible for getting the [VODChat](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_documentation.md#class-vodchat) via `get_videochat()`.

This class also has additional information about the VOD itself and its associated channel.

##### Parameters:
- `vod_id`: 
    
    the VOD ID to fetch the information for

##### Additional Class Attributes:

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
                

### available methods

- `def get_vodchat() -> VODChat:`
    
    Returns a [VODChat](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_documentation.md#class-vodchat) instance.


## **class `VODChat`**

A class which represents the VOD stream chat. We store here both the 'raw comment' data (i.e. the JSON)
`raw_comments` and the 'cleaned comments' `vod_comments`.

There should be no need to create a instance of this class manually.

##### Parameters:
- `vod_id`: 
    
    the VOD ID to fetch the information for
    
- `_basic_vod_data`: 
    
    a namedtuple (passed from VOD) which contains additional information associated
with the given VOD and its channel owner

- `_headers`:
    
    the required request headers to authenticate with the Twitch API
    
    
##### Additional Class Attributes:

- `vod_comments`:

    the VOD comments contain the name, message and timestamp of a comment (class VODSimpleComment)

- `raw_comments`:

    the raw comments in JSON

- `url`:

    the base url for the VOD requests


### available methods

- `def comments() -> list:`
    
    property attribute of `vod_comments`. Returns the vod_comments.

- `def raw() -> dict:`
    
    property attribute of `raw_comments`. Returns the raw_comments.
    
    
- `def get_comments() -> list:`
    
    "cleans" the raw_comments. Meaning: timestamp, user name, when the message has been posted in the chat and the body/text of the chat comment.
    Returns the comments. Each comment is a **[VODSimpleComment](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_documentation.md#class-vodsimplecommentnamedtuple)** object.

    If the raw data is wanted (JSON),
    simply call the class instance attribute `raw_comments` or its property `raw`.
    
    
- `def to_file(dirpath: Union[pathlib.Path, str] = None, save_json: bool = True) -> None:`

    Saves the cleaned vod comment data in a plain `.txt` file.
    The raw JSON data can additionally be saved in a separate `.json` file, if `save_json` is set (default behavior).

    Only a valid directory path pointing to a folder is allowed.
    
    Arguments:

    - `dirpath`:
    
        the path pointing to a directory in which the file(s) are to be saved.
        Defaults to the current working directory as returned by `os.getcwd()`
        
        Can *either* be directly a pathlib.Path object or a str.
        
    - `save_json`:
    
        whether or not a separate .json file containing the raw JSON data should be created

    Raises: `from .exceptions`
    - `DirectoryDoesNotExistError` | `DirectoryIsAFileError`: 
    
        if either the `dirpath` does not exist, or the path points to a file


## **class `VODSimpleComment(NamedTuple)`**

This class represents a simple ("cleaned") comment.

Each VODSimpleComment instance consists of:

- the `timestamp` of the message

- the `posted_at` time (when in the VOD the comment has been posted)
            
            -> added in v0.2.0

- the `name` of the user who wrote the message

- the `message` body

This class inherits from [NamedTuple](https://docs.python.org/3/library/collections.html#collections.namedtuple),
and its attributes can therefore be simply called via `comment.attribute`.

Like so:
```python

for comment in vod_comments:
    print(comment.timestamp)
    print(comment.posted_at)
    print(comment.name)
    print(comment.message)
```
