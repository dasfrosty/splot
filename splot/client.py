from click import echo


class SpotifyApiClient:
    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token
        echo(f"{self.oauth_token=}")
