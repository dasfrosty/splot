import json

import click
from dotenv import load_dotenv

from .client import spotify_api_client
from .db import splot_db
from .util import print_stderr

load_dotenv()


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
def dump_playlists():
    playlists = client.get_current_users_playlists()
    print_stderr(len(playlists["items"]))
    print(json.dumps(playlists, indent=2))


@cli.command()
def sync_playlists():
    playlists = client._get_current_users_playlists(1, 0)
    playlist = playlists["items"][0]
    db.upsert_playlist(playlist)


if __name__ == "__main__":
    cli()
