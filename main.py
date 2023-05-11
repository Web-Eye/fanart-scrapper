import os
from fanart.core import Request
import fanart
from fanart.music import Artist
import musicbrainzngs


def do_fanart():
    # request = Request(
    #     apikey=os.getenv('FANARTTV_API_KEY'),
    #     id='83b9cbe7-9857-49e2-ab8e-b57b01038103',
    #     ws=fanart.WS.MUSIC,
    #     type=fanart.TYPE.ALL,
    #     sort=fanart.SORT.POPULAR,
    #     limit=fanart.LIMIT.ALL,
    # )
    # print(request.response())

    os.environ.setdefault('FANART_APIKEY', os.getenv('FANARTTV_API_KEY'))

    artist = Artist.get(id='83b9cbe7-9857-49e2-ab8e-b57b01038103')
    for album in artist.albums:
        print(album.mbid)
        if album.mbid == '4816047b-5a40-462a-81e7-2f6eb6687fda':
            for cover in album.covers:
                print(cover.url)


def getMusicBrainzAlbumId(artist_id=None, album=None, format=None, track_count=None, release_date=None):
    test = musicbrainzngs.search_releases(arid=artist_id, release=album, format=format, date=release_date, tracks=track_count)

    for release in test.get('release-list'):
        if release.get('title') == album:
            return release.get('id')

def getMusicBrainzArtistId(artist):
    result = musicbrainzngs.search_artists(artist=artist, limit=100)
    if result:
        for a in result['artist-list']:
            if a['name'] == artist:
                return a['id']



if __name__ == '__main__':
    musicbrainzngs.set_useragent('python-musicplayer-flask', '0.1', '*****@*****.**')
    # do_fanart()
    # print(getMusicBrainzArtistId('Pearl Jam'))
    # print(getMusicBrainzAlbumId(artist_id='83b9cbe7-9857-49e2-ab8e-b57b01038103', album='Vitalogy', format='CD', track_count=14))

