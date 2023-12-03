# -*- coding: utf-8 -*-

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

from kodi_six import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
from resources.lib.modules import control
from resources.lib.modules import cache

streamdbApi = control.setting('streamdb.api')
lang = 'en' if control.setting('info.language') == 'English' else 'el'

try:
    from six.moves import urllib_request
    urlopen = urllib_request.urlopen
except ImportError:
    import requests
    urlopen = requests.Session()

def syncdb(type = 'movie'):
    
    if streamdbApi == '' or len(streamdbApi) == 0:
        return
    
    data_link = 'https://streamdb.homebrewgr.info/index.php?action=get-user-data&api_key=%s&lang=%s&type=%s' % (streamdbApi, lang, type)
    
    try:
        data_json = cache.get_cache_file('user_data_' + type, data_link)
    except:
        return
    
    if not 'status' in data_json or data_json["status"] != "OK" or not 'data' in data_json:
        return

    data = data_json['data']
    
    if 'bookmarks' in data:
        items = data['bookmarks']

        for item in items:
            updt(item['time_in_seconds'], type, item['imdb_id'], item['season'], item['episode'])


def updt(current_time, media_type, imdb, season='', episode=''):
    try:
        _playcount = 0
        overlay = 6
        timeInSeconds = str(current_time)
        sql_select = "SELECT * FROM bookmarks WHERE imdb = '%s'" % imdb
        if media_type == 'tv':
            sql_select += " AND season = '%s' AND episode = '%s'" % (season, episode)
        sql_update = "UPDATE bookmarks SET timeInSeconds = '%s' WHERE imdb = '%s'" % (timeInSeconds, imdb)
        if media_type == 'tv':
            sql_update += " AND season = '%s' AND episode = '%s'" % (season, episode)
        if media_type == 'movie':
            sql_insert = "INSERT INTO bookmarks Values ('%s', '%s', '%s', '', '', '%s', '%s')" % (timeInSeconds, media_type, imdb, _playcount, overlay)
        elif media_type == 'tv':
            sql_insert = "INSERT INTO bookmarks Values ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (timeInSeconds, media_type, imdb, season, episode, _playcount, overlay)
                  
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.bookmarksFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS bookmarks (""timeInSeconds TEXT, ""type TEXT, ""imdb TEXT, ""season TEXT, ""episode TEXT, ""playcount INTEGER, ""overlay INTEGER, ""UNIQUE(imdb, season, episode)"");")
        dbcur.execute(sql_select)
        match = dbcur.fetchone()

        if match:
            dbcur.execute(sql_update)
        else:
            dbcur.execute(sql_insert)
        dbcon.commit()
    except:
        pass

def _indicators():
    control.makeFile(control.dataPath)
    dbcon = database.connect(control.bookmarksFile)
    dbcur = dbcon.cursor()
    dbcur.execute("SELECT * FROM bookmarks WHERE overlay = 7")
    match = dbcur.fetchall()
    if match:
        return [i[2] for i in match]
    dbcon.commit()


def _get_watched(media_type, imdb, season, episode):
    sql_select = "SELECT * FROM bookmarks WHERE imdb = '%s' AND overlay = 7" % imdb
    if media_type == 'episode':
        sql_select += " AND season = '%s' AND episode = '%s'" % (season, episode)
    control.makeFile(control.dataPath)
    dbcon = database.connect(control.bookmarksFile)
    dbcur = dbcon.cursor()
    dbcur.execute(sql_select)
    match = dbcur.fetchone()
    if match:
        return 7
    else:
        return 6
    dbcon.commit()


def _update_watched(media_type, new_value, imdb, season, episode):
    sql_update = "UPDATE bookmarks SET overlay = %s WHERE imdb = '%s'" % (new_value, imdb)
    if media_type == 'episode':
        sql_update += " AND season = '%s' AND episode = '%s'" % (season, episode)
    dbcon = database.connect(control.bookmarksFile)
    dbcur = dbcon.cursor()
    dbcur.execute(sql_update)
    dbcon.commit()


def _delete_record(media_type, imdb, season, episode):
    sql_delete = "DELETE FROM bookmarks WHERE imdb = '%s'" % imdb
    if media_type == 'episode':
        sql_delete += " AND season = '%s' AND episode = '%s'" % (season, episode)
    dbcon = database.connect(control.bookmarksFile)
    dbcur = dbcon.cursor()
    dbcur.execute(sql_delete)
    dbcon.commit()


def get(media_type, imdb, season, episode):
    try:
        sql_select = "SELECT * FROM bookmarks WHERE imdb = '%s'" % imdb
        if media_type == 'episode':
            sql_select += " AND season = '%s' AND episode = '%s'" % (season, episode)
        
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.bookmarksFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS bookmarks (""timeInSeconds TEXT, ""type TEXT, ""imdb TEXT, ""season TEXT, ""episode TEXT, ""playcount INTEGER, ""overlay INTEGER, ""UNIQUE(imdb, season, episode)"");")
        dbcur.execute(sql_select)
        match = dbcur.fetchone()
        if match:
            offset = match[0]
            return float(offset)
        else:
            return 0
    except:
         return 0

def reset(current_time, total_time, media_type, imdb, season='', episode=''):
    try:
        _playcount = 0
        overlay = 6
        timeInSeconds = str(current_time)
        ok = int(current_time) > 120 and (current_time / total_time) < .92
        watched = (current_time / total_time) >= .92
        sql_select = "SELECT * FROM bookmarks WHERE imdb = '%s'" % imdb
        if media_type == 'episode':
            sql_select += " AND season = '%s' AND episode = '%s'" % (season, episode)
        sql_update = "UPDATE bookmarks SET timeInSeconds = '%s' WHERE imdb = '%s'" % (timeInSeconds, imdb)
        if media_type == 'episode':
            sql_update += " AND season = '%s' AND episode = '%s'" % (season, episode)
        if media_type == 'movie':
            sql_update_watched = "UPDATE bookmarks SET timeInSeconds = '0', playcount = %s, overlay = %s WHERE imdb = '%s'" % ('%s', '%s', imdb)
        elif media_type == 'episode':
            sql_update_watched = "UPDATE bookmarks SET timeInSeconds = '0', playcount = %s, overlay = %s WHERE imdb = '%s' AND season = '%s' AND episode = '%s'" % ('%s', '%s', imdb, season, episode)
        if media_type == 'movie':
            sql_insert = "INSERT INTO bookmarks Values ('%s', '%s', '%s', '', '', '%s', '%s')" % (timeInSeconds, media_type, imdb, _playcount, overlay)
        elif media_type == 'episode':
            sql_insert = "INSERT INTO bookmarks Values ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (timeInSeconds, media_type, imdb, season, episode, _playcount, overlay)
        if media_type == 'movie':
            sql_insert_watched = "INSERT INTO bookmarks Values ('%s', '%s', '%s', '', '', '%s', '%s')" % (timeInSeconds, media_type, imdb, '%s', '%s')
        elif media_type == 'episode':
            sql_insert_watched = "INSERT INTO bookmarks Values ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (timeInSeconds, media_type, imdb, season, episode, '%s', '%s')
                    
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.bookmarksFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS bookmarks (""timeInSeconds TEXT, ""type TEXT, ""imdb TEXT, ""season TEXT, ""episode TEXT, ""playcount INTEGER, ""overlay INTEGER, ""UNIQUE(imdb, season, episode)"");")
        dbcur.execute(sql_select)
        match = dbcur.fetchone()

        if streamdbApi != '':
            update_url  = 'https://streamdb.homebrewgr.info/index.php?action=update-bookmark&api_key=%s&imdb=%s&time=%s&se=%s&ep=%s' % (streamdbApi, imdb, timeInSeconds, season, episode)
            try:
                urlopen(update_url)
            except:
                pass

        if match:
            if ok:
                dbcur.execute(sql_update)
            elif watched:
                _playcount = match[5] + 1
                overlay = 7
                dbcur.execute(sql_update_watched % (_playcount, overlay))
        else:
            if ok:
                dbcur.execute(sql_insert)
            elif watched:
                _playcount = 1
                overlay = 7
                dbcur.execute(sql_insert_watched % (_playcount, overlay))
        dbcon.commit()
    except:
        pass


