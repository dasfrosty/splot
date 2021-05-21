import json
from datetime import datetime
from pprint import pprint

import click
from dotenv import load_dotenv

from .db import splot_db
from .spotify_api_client import spotify_api_client
from .util import print_stderr

load_dotenv()

DATE_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"

client = spotify_api_client()
db = splot_db()


@click.group()
def cli():
    pass


@cli.command()
def create_indexes():
    click.echo("Creating indexes...", err=True)
    db.create_indexes()
    click.echo("Done.", err=True)


@cli.command()
def current_user():
    current_users_profile = client.get_current_users_profile()
    print(json.dumps(current_users_profile, indent=2))


@cli.command()
@click.argument("playlist-id")
def dump_tracks(playlist_id):
    tracks = client.get_playlist_tracks(playlist_id)
    print_stderr(len(tracks["items"]))
    print(json.dumps(tracks, indent=2))


@cli.command()
def dump_playlists():
    playlists = client.get_current_users_playlists()
    print_stderr(len(playlists["items"]))
    print(json.dumps(playlists, indent=2))


def _load_playlist_tracks(playlist):
    playlist_tracks = client.get_playlist_tracks(playlist["id"])

    tracks = []
    playlist_added_at = None
    for playlist_track in playlist_tracks["items"]:
        # pprint(playlist_track)
        # print(
        #     f'{playlist_track["track"]["artists"][0]["name"]} - {playlist_track["track"]["name"]} - {playlist_track["added_at"]}'
        # )
        added_at = datetime.strptime(playlist_track["added_at"], DATE_FORMAT_STRING)
        if playlist_added_at is None or added_at < playlist_added_at:
            playlist_added_at = added_at

        try:
            assert playlist_track["track"]["type"] == "track"
        except:
            print("Unexpected playlist track type")
            pprint(playlist_track)
        else:
            tracks.append(
                {
                    "id": playlist_track["track"]["id"],
                    "name": playlist_track["track"]["name"],
                    "artist": playlist_track["track"]["artists"][0]["name"],
                    "added_at": datetime.strptime(
                        playlist_track["added_at"], DATE_FORMAT_STRING
                    ),
                }
            )

    playlist["added_at"] = playlist_added_at
    playlist["tracks"]["tracks"] = tracks
    try:
        del playlist["tracks"]["items"]
        del playlist["tracks"]["limit"]
        del playlist["tracks"]["next"]
        del playlist["tracks"]["offset"]
        del playlist["tracks"]["previous"]
    except KeyError:
        pass


@cli.command()
def sync_first_playlist():
    playlists = client._get_current_users_playlists(10, 0)
    playlist = playlists["items"][0]
    _load_playlist_tracks(playlist)
    db.upsert_playlist(playlist)


@cli.command()
@click.argument("playlist-id")
def sync_playlist(playlist_id):
    playlist = client.get_playlist(playlist_id)
    _load_playlist_tracks(playlist)
    db.upsert_playlist(playlist)


@cli.command()
def sync_playlists():
    playlists = client.get_current_users_playlists()
    for playlist in playlists["items"]:
        if playlist["owner"]["id"] == "pottyspice":
            _load_playlist_tracks(playlist)
            db.upsert_playlist(playlist)
        else:
            print(f"skip syncing playlist {playlist['name']}")


if __name__ == "__main__":
    cli()
