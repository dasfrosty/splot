import json
import os

import click
from dotenv import load_dotenv

from .client import SpotifyApiClient
from .util import print_stderr

load_dotenv()


def oauth_token():
    return os.environ["OAUTH_TOKEN"]


client = SpotifyApiClient(oauth_token())


@click.group()
def cli():
    pass


@cli.command()
def current_user():
    current_users_profile = client.get_current_users_profile()
    print(json.dumps(current_users_profile, indent=2))


@cli.command()
def my_playlists():
    playlists = client.get_current_users_playlists()
    print_stderr(len(playlists["items"]))
    print(json.dumps(playlists, indent=2))


if __name__ == "__main__":
    cli()
