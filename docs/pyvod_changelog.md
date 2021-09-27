# Changelog

Changes are listed here. The latest version is currently v0.2.0.

## v0.2.1 (27.09.2021)

- added a fix for the mentioned `strptime error` in issue #3.
- README formatting

## v0.2.0 (21.05.2021)

- added additional comment information `posted_at`:
    - when the comment has been posted in the chat, in relation to the VOD/stream length
    - `hours:minutes:seconds` format
    
    You can access it like the other
    **[VODSimpleComment](https://github.com/sixP-NaraKa/pyvod-chat/blob/main/docs/pyvod_documentation.md#class-vodsimplecommentnamedtuple)**
    attributes:
        
```python
for comment in vod_comments:
    # print(comment.timestamp)
    print(comment.posted_at)
    # print(comment.name)
    # print(comment.message)
```

## v0.1.0 (20.04.2021)

- initial release
