import json
import os
from fanart.core import Request
import fanart
from fanart.music import Artist
from fanart import errors
import musicbrainzngs
from difflib import SequenceMatcher

from libs.core.databaseHelper import databaseHelper


def do_fanart(config):
    con = databaseHelper.getConnection(config)
    cursor = databaseHelper.executeReader(con, 'SELECT art_id, artist.strMusicBrainzArtistID, '
                                               '       album.strReleaseGroupMBID, album.strMusicBrainzAlbumID  '
                                               '   FROM art '
                                               '   LEFT JOIN album ON art.media_type = ? AND '
                                               '                      art.media_id = album.idAlbum    '
                                               '   LEFT JOIN album_artist ON album.idAlbum = album_artist.idAlbum'
                                               '   LEFT JOIN artist ON album_artist.idArtist = artist.idArtist'
                                               ''
                                               '   WHERE art.url NOT LIKE ? AND '
                                               '         NOT artist.strMusicBrainzArtistID IS NULL AND '
                                               '         NOT strReleaseGroupMBID IS NULL NOT album.strAlbum LIKE ? AND '
                                               '         NOT album.strAlbum LIKE ? AND NOT album.strAlbum LIKE ? AND '
                                               '         NOT album.strAlbum LIKE ;',
                                          ('album', 'http%', '%(Legacy Edition)%', '%(Remastered)%',
                                           '%(Deluxe Edition)%', '%(10th Anniversary Edition)%', ))

    rows = cursor.fetchall()
    for row in rows:
        try:
            artist = Artist.get(id=row[1])
            for album in artist.albums:
                if album.mbid == row[2]:
                    if len(album.covers) > 0:
                        print(album.covers[0].url)
        except fanart.errors.ResponseFanartError:
            pass


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
    # do_albums(config)
    do_fanart(config)

    # do_fanart()
    # print(getMusicBrainzArtistId('Pearl Jam'))
    # print(getMusicBrainzAlbumId(artist_id='83b9cbe7-9857-49e2-ab8e-b57b01038103', album='Ten', comment='Legacy Edition', format='CD',
    #                             track_count=28, release_date='2009-03-24'))

    # print(getMusicBrainzAlbumId(artist_id='7527f6c2-d762-4b88-b5e2-9244f1e34c46', album='B-Sides & Rarities', comment=None,
    #                             format='CD',
    #                             track_count=15, release_date='2005'))


if __name__ == '__main__':
    main()





