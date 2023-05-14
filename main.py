import json
import os
from fanart.core import Request
import fanart
from fanart.music import Artist
import musicbrainzngs
from difflib import SequenceMatcher

from libs.core.databaseHelper import databaseHelper


def do_fanart():
    # request = Request(
    #     apikey=os.getenv('FANARTTV_API_KEY'),
    #     id='467a5697-30e7-34b8-9813-d07e6af9c653',
    #     ws=fanart.WS.MUSIC,
    #     type=fanart.TYPE.ALL,
    #     sort=fanart.SORT.POPULAR,
    #     limit=fanart.LIMIT.ALL,
    # )
    # print(request.response())



    artist = Artist.get(id='2386cd66-e923-4e8e-bf14-2eebe2e9b973')
    for album in artist.albums:
        # print(album.mbid)
        if album.mbid == '467a5697-30e7-34b8-9813-d07e6af9c653':
            for cover in album.covers:
                print(cover.url)


def doReleaseMatch(release, artist_id, album, track_count):
    if release['medium-track-count'] == track_count:

        artists = release['artist-credit']
        for a in artists:
            try:
                if a['artist']['id'] == artist_id:
                    if SequenceMatcher(None, release.get('title').lower(), album.lower()).ratio() > 0.9:
                        return True
            except:
                pass

    return False


def getMusicBrainzAlbumId(artist_id=None, album=None, format=None, track_count=None, release_date=None, comment=None):
    result = musicbrainzngs.search_releases(arid=artist_id, release=album, format=format, date=release_date,
                                            tracks=track_count, comment=comment)

    for release in result.get('release-list'):
        if doReleaseMatch(release, artist_id, album, track_count):
            return release.get('id'), release['release-group']['id']

    return None, None


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


def validate_AlbumName(name):
    comment = None
    if '(Legacy Edition)' in name:
        comment = 'Legacy Edition'
        name = name.replace('(Legacy Edition)', '')
    elif '(Remastered)' in name:
        comment = 'Remastered'
        name = name.replace('(Remastered)', '')
    elif '(Deluxe Edition)' in name:
        comment = 'Deluxe Edition'
        name = name.replace('(Deluxe Edition)', '')
    elif '(10th Anniversary Edition)' in name:
        comment = '10th Anniversary Edition'
        name = name.replace('(10th Anniversary Edition)', '')
    elif '(OST)' in name:
        name = name.replace('(OST)', '')
    elif '(Soundtrack)' in name:
        name = name.replace('(Soundtrack)', '')
    elif '(unofficial Fanta 4 Album)' in name:
        name = name.replace('(unofficial Fanta 4 Album)', '')
    elif '(Maxi)' in name:
        name = name.replace('(Maxi)', '')

    return name.lstrip().rstrip(), comment


def do_albums(config):
    con = databaseHelper.getConnection(config)
    cursor = databaseHelper.executeReader(con, 'SELECT artist.strMusicBrainzArtistId, album.idAlbum, album.strAlbum, '
                                               '       album.strReleaseDate, '
                                               '       ('
                                               '          SELECT COUNT(*) FROM song WHERE album.idAlbum = song.idAlbum'
                                               '       ) AS songCount'
                                               '   FROM album_artist  '
                                               '   LEFT JOIN artist ON album_artist.idArtist = artist.idArtist '
                                               '   LEFT JOIN album ON album_artist.idAlbum = album.idAlbum '
                                               'WHERE album.strMusicBrainzAlbumID IS NULL AND '
                                               '      NOT artist.strMusicBrainzArtistId IS NULL '
                                               'ORDER BY IFNULL(strSortName, artist.strArtist);')

    rows = cursor.fetchall()
    for row in rows:
        artist_id = row[0]
        album_id = row[1]
        album = row[2]
        songCount = row[4]
        album, comment = validate_AlbumName(album)
        album_MBID, release_group_MBID = getMusicBrainzAlbumId(artist_id=artist_id, album=album, comment=comment,
                                                               format='CD', track_count=songCount, release_date=row[3])

        databaseHelper.executeNonQuery(con, 'UPDATE album SET strMusicBrainzAlbumId = ?, strReleaseGroupMBID = ? '
                                            '   WHERE idAlbum = ?', (album_MBID, release_group_MBID, album_id, ))


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





