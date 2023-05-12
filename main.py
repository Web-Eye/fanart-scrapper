import json
import os
from fanart.core import Request
import fanart
from fanart.music import Artist
import musicbrainzngs

from libs.core.databaseHelper import databaseHelper


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



    artist = Artist.get(id='83b9cbe7-9857-49e2-ab8e-b57b01038103')
    for album in artist.albums:
        print(album.mbid)
        if album.mbid == '4816047b-5a40-462a-81e7-2f6eb6687fda':
            for cover in album.covers:
                print(cover.url)


def getMusicBrainzAlbumId(artist_id=None, album=None, format=None, track_count=None, release_date=None, comment=None):
    result = musicbrainzngs.search_releases(arid=artist_id, release=album, format=format, date=release_date,
                                            tracks=track_count, comment=comment)

    for release in result.get('release-list'):
        if release.get('title') == album:
            return release.get('id')


def getMusicBrainzArtistId(artist):
    result = musicbrainzngs.search_artists(artist=artist, limit=100)
    if result:
        for a in result['artist-list']:
            if a['name'] == artist:
                return a['id']


def do_artists(config):
    con = databaseHelper.getConnection(config)
    cursor = databaseHelper.executeReader(con, 'SELECT idArtist, strArtist FROM artist '
                                               '    WHERE strMusicBrainzArtistID IS NULL')

    rows = cursor.fetchall()
    for row in rows:
        mb_artistId = getMusicBrainzArtistId(row[1])
        databaseHelper.executeNonQuery(con, 'UPDATE artist SET strMusicBrainzArtistID = ? WHERE idArtist = ?',
                                       (mb_artistId, row[0], ))


def do_albums(config):
    con = databaseHelper.getConnection(config)
    cursor = databaseHelper.executeReader(con, 'SELECT artist.strMusicBrainzArtistId, album.idAlbum, album.strAlbum, '
                                               '       album.strReleaseDate, '
                                               '       ('
                                               '            SELECT COUNT(*) FROM song WHERE album.idAlbum = song.idAlbum'
                                               '       ) AS songCount'
                                               '   FROM album_artist  '
                                               '   LEFT JOIN artist ON album_artist.idArtist = artist.idArtist '
                                               '   LEFT JOIN album ON album_artist.idAlbum = album.idAlbum '
                                               'WHERE album.strMusicBrainzAlbumID IS NULL AND '
                                               '      NOT artist.strMusicBrainzArtistId IS NULL '
                                               'ORDER BY strSortName')

    # print(getMusicBrainzAlbumId(artist_id='83b9cbe7-9857-49e2-ab8e-b57b01038103', album='Ten', comment='Legacy Edition', format='CD',
    #                             track_count=28, release_date='2009-03-24'))

    rows = cursor.fetchall()
    for row in rows:
        artist_id = row[0]
        album = row[2]
        comment = None
        if 'Legacy Edition' in album:
            comment = 'Legacy Edition'
            album = album.replace('Legacy Edition', '').lstrip().rstrip()
        print(row)
        print(f'album: {album}; comment: {comment}')


def main():
    musicbrainzngs.set_useragent('python-musicplayer-flask', '0.1', '*****@*****.**')
    os.environ.setdefault('FANART_APIKEY', os.getenv('FANARTTV_API_KEY'))
    config = json.loads(os.getenv('DATABASE_CONFIG'))

    # do_artists(config)
    do_albums(config)

    # do_fanart()
    # print(getMusicBrainzArtistId('Pearl Jam'))
    # print(getMusicBrainzAlbumId(artist_id='83b9cbe7-9857-49e2-ab8e-b57b01038103', album='Ten', comment='Legacy Edition', format='CD',
    #                             track_count=28, release_date='2009-03-24'))

    # print(getMusicBrainzAlbumId(artist_id='7527f6c2-d762-4b88-b5e2-9244f1e34c46', album='B-Sides & Rarities', comment=None,
    #                             format='CD',
    #                             track_count=15, release_date='2005'))


if __name__ == '__main__':
    main()





