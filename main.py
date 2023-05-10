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


def do_musicbrainz():
    musicbrainzngs.set_useragent('python-musicplayer-flask', '0.1', '*****@*****.**')
    # test = musicbrainzngs.search_artists(query='Pearl Jam')
    # print(test)

    #  '83b9cbe7-9857-49e2-ab8e-b57b01038103'


    _offset = 0
    _release_count = 1
    while _offset + 1 <= _release_count:
        test = musicbrainzngs.search_releases(query='Vitalogy', offset=_offset)
        _release_count = test.get('release-count')

        for release in test.get('release-list'):
            if release.get('title') == 'Vitalogy':
                #  more decisions
                #  - release.status == 'Official'
                #  - release.date == db.strReleaseDate
                #  - release.medium-list.format == CD
                #  - release.medium-list.track-count == db.query
                #  - release.country == 'US/DE'

                _found = False
                for artist in release.get('artist-credit'):
                    try:
                        if artist.get('artist').get('id') == '83b9cbe7-9857-49e2-ab8e-b57b01038103':
                          _found = True
                    except:
                        pass

                if _found:
                    print(release.get('id'))
            elif 'Vitalogy' not in release.get('title'):
                break

        _offset += 25


    #  '4816047b-5a40-462a-81e7-2f6eb6687fda'

if __name__ == '__main__':
    # do_fanart()
    do_musicbrainz()
