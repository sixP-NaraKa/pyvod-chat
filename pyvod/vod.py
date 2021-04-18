from .vodchat import VODChat


class VOD:
    def __init__(self, vod_id):
        self.vod_id = vod_id

    def get_vodchat(self) -> VODChat:
        vod_chat = VODChat(vod_id=self.vod_id)

        return vod_chat
