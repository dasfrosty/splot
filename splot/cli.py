import os

import click
from dotenv import load_dotenv
from .client import SpotifyApiClient

load_dotenv()


def oauth_token():
    return os.environ["OAUTH_TOKEN"]


client = SpotifyApiClient(oauth_token())


@click.group()
def cli():
    pass


@cli.command()
def export_playlists():
    pass


if __name__ == "__main__":
    cli()
