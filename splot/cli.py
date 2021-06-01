import json
import time
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
db.create_indexes()


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
    current_users_profile = client.get_current_users_profile()
    current_user_id = current_users_profile["id"]
    current_user_display = current_users_profile["display_name"]
    playlists = client.get_current_users_playlists()
    idx = 0
    for playlist in playlists["items"]:
        if playlist["owner"]["id"] == current_user_id:
            _load_playlist_tracks(playlist)
        playlist["idx"] = idx
        playlist["current_user"] = current_user_display
        db.upsert_playlist(playlist)
        idx += 1


@cli.command()
@click.argument("playlist-name")
def find_playlist_by_name(playlist_name):
    playlist = client.find_playlist_by_name(playlist_name)
    if playlist:
        print(f'Playlist found: {playlist["name"]} - {playlist["id"]}')
    else:
        print("Playlist not found!")


@cli.command()
@click.argument("playlist-id")
def clone_playlist(playlist_id):
    current_users_profile = client.get_current_users_profile()
    current_user_id = current_users_profile["id"]
    playlist = client.get_playlist(playlist_id)

    # make sure we're not cloning our own playlist by accident
    assert current_user_id != playlist["owner"]["id"]

    # make sure it's not a playlist that was already cloned
    assert not playlist["name"].startswith(">>>")

    playlist_tracks = client.get_playlist_tracks(playlist["id"])

    # make sure playlist doesn't already exist
    # existing_playlist = None
    existing_playlist = client.find_playlist_by_name(playlist["name"])
    if existing_playlist:
        print(f'Error: Playlist with name "{playlist["name"]}" already exists!')
        return
        # created_playlist = existing_playlist
    else:
        # create playlist and add tracks
        print(f"Creating playlist: {playlist['name']}")
        created_playlist = client.create_playlist(current_user_id, playlist["name"])

    try:
        print(created_playlist["id"])
        print(created_playlist["name"])
    except Exception:
        pprint(created_playlist)
        raise

    for idx, track in enumerate(playlist_tracks["items"]):
        time.sleep(3)
        print(
            f'   ==> {(idx + 1):03d} - {track["track"]["artists"][0]["name"]} - {track["track"]["name"]} - {track["added_at"]}'
        )

        try:
            client.add_playlist_track(created_playlist["id"], track["track"]["id"])
        except Exception:
            pprint(track)
            raise


@cli.command()
@click.argument("playlist-id")
@click.argument("track-id")
def add_track_to_playlist(playlist_id, track_id):
    print(f"{playlist_id} {track_id}")
    client.add_playlist_track(playlist_id, track_id)


if __name__ == "__main__":
    cli()
