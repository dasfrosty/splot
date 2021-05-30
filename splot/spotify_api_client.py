import os

import requests

from .util import print_stderr


class SpotifyApiClient:
    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token

    def _headers(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth_token}",
        }

    def get_current_users_profile(self):
        endpoint = "https://api.spotify.com/v1/me"

        r = requests.get(endpoint, headers=self._headers())
        r.raise_for_status()
        return r.json()

    def _get_playlist_tracks(self, playlist_id, limit: int, offset: int):
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}"
        r = requests.get(endpoint, headers=self._headers())
        r.raise_for_status()
        return r.json()

    def get_playlist_tracks(self, playlist_id):
        limit = 100
        offset = 0
        items = []

        while True:
            page = self._get_playlist_tracks(playlist_id, limit, offset)
            items += page["items"]
            offset += limit
            print_stderr(".", end="", flush=True)
            if page["next"] is None:
                print_stderr()
                page["items"] = items
                return page

    def get_playlist(self, playlist_id):
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        r = requests.get(endpoint, headers=self._headers())
        r.raise_for_status()
        return r.json()

    def _get_current_users_playlists(self, limit: int, offset: int):
        endpoint = (
            f"https://api.spotify.com/v1/me/playlists?limit={limit}&offset={offset}"
        )
        r = requests.get(endpoint, headers=self._headers())
        r.raise_for_status()
        return r.json()

    def get_current_users_playlists(self):
        limit = 50
        offset = 0
        items = []

        while True:
            page = self._get_current_users_playlists(limit, offset)
            items += page["items"]
            offset += limit
            print_stderr(".", end="", flush=True)
            if page["next"] is None:
                print_stderr()
                page["items"] = items
                return page

    def find_playlist_by_name(self, playlist_name):
        playlists = self.get_current_users_playlists()
        for playlist in playlists["items"]:
            if playlist["name"] == playlist_name:
                return playlist
        return None

    def create_playlist(self, user_id: str, playlist_name: str):
        endpoint = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        body = {"name": playlist_name}
        r = requests.post(endpoint, headers=self._headers(), json=body)
        r.raise_for_status()
        return r.json()

    def add_playlist_track(self, playlist_id: str, track_id: str):
        endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        body = {"uris": [f"spotify:track:{track_id}"]}
        r = requests.post(endpoint, headers=self._headers(), json=body)
        r.raise_for_status()
        return r.json()


def spotify_api_client():
    oauth_token = os.environ["SPLOT_OAUTH_TOKEN"]
    return SpotifyApiClient(oauth_token)
