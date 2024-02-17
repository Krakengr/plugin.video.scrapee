# -*- coding: utf-8 -*-

import simplejson as json

from resources.lib.modules import control
from resources.lib.modules import cache
from kodi_six import xbmc, xbmcplugin, xbmcgui

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

try:
    from six.moves import urllib_request
    urlopen = urllib_request.urlopen
except ImportError:
    import requests
    urlopen = requests.Session()

streamdbApi = control.setting('streamdb.api')
lang = 'en' if control.setting('info.language') == 'English' else 'el'

def syncldb(type = 'movie'):
    
    if streamdbApi == '' or len(streamdbApi) == 0:
        return
    
    data_link = 'https://streamdb.homebrewgr.info/index.php?action=get-user-data&api_key=%s&lang=%s&type=%s' % (streamdbApi, lang, type)

    try:
        data_json = cache.get_cache_file('user_data', data_link)
    except:
        return

    if not 'status' in data_json or data_json["status"] != "OK" or not 'data' in data_json:
        return

    data = data_json['data']

    if type == 'tv':
        type = 'tvshow'

    if 'likes' in data:
        items = data['likes']

        for item in items:
            addLike(json.dumps(item), type, True)

def addLike(meta, content, upd = False):
    xbmc.log('meta: ' + str(meta), xbmc.LOGINFO)
    xbmc.log('content: ' + str(content), xbmc.LOGINFO)
    try:
        item = dict()
        meta = json.loads(meta)
        
        try:
            id = meta['imdb_id'] if 'imdb_id' in meta else meta['imdb']
        except:
            id = meta['tmdb']
        
        if 'title' in meta:
            title = item['title'] = meta['title']
        if 'tvshowtitle' in meta:
            title = item['title'] = meta['tvshowtitle']
        if 'year' in meta:
            item['year'] = meta['year']
        if 'mediatype' in meta:
            item['mediatype'] = meta['mediatype']
        if 'description' in meta:
            item['description'] = meta['description']
        if 'poster' in meta:
            item['poster'] = meta['poster']
        elif 'poster_path' in meta:
            item['poster'] = meta['poster_path']
        if 'fanart' in meta:
            item['fanart'] = meta['fanart']
        elif 'backdrop_path' in meta:
            item['fanart'] = meta['backdrop_path']
        if 'link' in meta:
            item['link'] = meta['link']
        if 'imdb' in meta or 'imdb_id' in meta:
            item['imdb'] = meta['imdb_id'] if 'imdb_id' in meta else meta['imdb']

            if not upd:
                if streamdbApi != '':
                    try:
                        upd_link = 'https://streamdb.homebrewgr.info/index.php?action=add-user-likes&imdb=%s&api_key=%s' % (item['imdb'], streamdbApi)
                        urlopen(upd_link)
                    except:
                        pass

                control.sleep(100)
        
        if 'tmdb' in meta:
            item['tmdb'] = meta['tmdb']
        if 'tvdb' in meta:
            item['tvdb'] = meta['tvdb']
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.likesFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s (""id TEXT, ""items TEXT, ""UNIQUE(id)"");" % content)
        dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (content, id))
        dbcur.execute("INSERT INTO %s Values (?, ?)" % content, (id, repr(item)))
        dbcon.commit()

        if not upd:
            control.refresh()
            control.infoDialog('Like Added', heading=title, icon=item['poster'])
    except:
        return


def deleteLike(meta, content):
    try:
        meta = json.loads(meta)
        if 'title' in meta:
            title = meta['title']
        if 'tvshowtitle' in meta:
            title = meta['tvshowtitle']
        if 'poster' in meta:
            poster = meta['poster']
        else:
            poster = control.addonThumb()
        try:
            dbcon = database.connect(control.likesFile)
            dbcur = dbcon.cursor()
            try:
                dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (content, meta['imdb']))
            except:
                pass
            try:
                dbcur.execute("DELETE FROM %s WHERE id = '%s'" % (content, meta['tmdb']))
            except:
                pass
            dbcon.commit()

            if streamdbApi != '':
                try:
                    upd_link = 'https://streamdb.homebrewgr.info/index.php?action=remove-user-likes&imdb=%s&api_key=%s' % (meta['imdb'], streamdbApi)
                    urlopen(upd_link)
                except:
                    pass

                control.sleep(100)
        except:
            pass
        control.refresh()
        control.infoDialog('Like Removed', heading=title, icon=poster)
    except:
        return


def getLikes(content):
    try:
        dbcon = database.connect(control.likesFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM %s" % content)
        items = dbcur.fetchall() 
    except:
        items = []
    return items


