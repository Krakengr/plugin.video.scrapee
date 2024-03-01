# -*- coding: utf-8 -*-

import re
import os
import time
from os.path import exists

import six
from ast import literal_eval as evaluate
import xml.etree.ElementTree as ET
import simplejson as json
from kodi_six import xbmc, xbmcgui
import xbmcaddon
from resources.lib.modules import control
from resources.lib.modules import log_utils

try:
    from sqlite3 import dbapi2 as db, Error
except ImportError:
    from pysqlite2 import dbapi2 as db, Error

try:
    from six.moves import urllib_request, urllib_parse
    urlopen = urllib_request.urlopen
    datapost = urllib_request.Request
except ImportError:
    import requests
    urlopen = requests.Session()
    datapost = requests.post


dialog = xbmcgui.Dialog()
cache_table = 'cache'
kodi_version = control.getKodiVersion()
home = xbmcaddon.Addon().getAddonInfo('path')
streamdbApi = control.setting('streamdb.api')
dbCacheTime = int(control.setting('cache.duration'))
cache_time = 3600 #This value can't be changed
cache_xml_time = 86400 if dbCacheTime < 1800 else dbCacheTime

def _delete_record(media_type, imdb, season = 0, episode = 0):
    sql_delete = "DELETE FROM links WHERE imdb = '%s'" % imdb
    if media_type == 'tv':
        sql_delete += " AND season = %s AND episode = %s" % (season, episode)
    dbcon = db.connect(control.cacheFile)
    dbcur = dbcon.cursor()
    try:
        dbcur.execute(sql_delete)
        dbcon.commit()
    except Error as e:
        xbmc.log('sql_match error : ' + str(e), xbmc.LOGINFO)
        pass

def add_link(link, media_type, imdb, season = 0, episode = 0):
    now = int( time.time() )
    control.makeFile(control.dataPath)
    dbcon = db.connect(control.cacheFile)
    dbcur = dbcon.cursor()
    _delete_record(media_type, imdb, season, episode)
    
    try:
        sql_insert = "INSERT INTO links VALUES ('%s', '%s', '%s', '%s', '%s', %s)" % (link, media_type, imdb, season, episode, now)
        dbcur.execute(sql_insert)
        dbcon.commit()
    except Error as e:
        #e
        pass
    
def get_link(media_type, imdb, season = 0, episode = 0):
    try:
        now = int( time.time() )
        time_added = (now - cache_time)
        
        sql_select = "SELECT url FROM links WHERE imdb = '%s'" % imdb
        sql_delete = "DELETE FROM links WHERE imdb = '%s'" % imdb
        
        if media_type == 'tv':
            sql_select += " AND season = '%s' AND episode = '%s'" % (season, episode)
            sql_delete += " AND season = '%s' AND episode = '%s'" % (season, episode)

        sql_select += " AND added > '%s'" % (time_added)

        control.makeFile(control.dataPath)
        dbcon = db.connect(control.cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS links (""url TEXT, ""type TEXT, ""imdb TEXT, ""season TEXT, ""episode TEXT, ""added INTEGER,  ""UNIQUE(imdb, season, episode)"");")
        dbcur.execute(sql_select)
        match = dbcur.fetchone()
        if match:
            link = match[0]
            return link
        else:
            #Delete the link
            dbcur.execute(sql_delete)
            return None
    except:
         return None

def get_cache_file(name, url):
    
    filename    = name + '.json'

    if file_exists(filename) and file_time(filename):
        data_json = open_cache(filename)
        
    else:
        try:
            response    = urlopen(url)
            
            data_json   = json.loads(response.read().decode('utf-8'))

        except:
            #dialog.ok('Error', 'Error getting data. Please try again later.')
            return None
        
        write_cache(filename, data_json)
    
    return data_json

def get_coverapi_data(imdb, type = 'movie'):
    
    filename    = imdb + '.xml'
    file_link   = None
    tree        = None
    data_json   = None

    if file_exists(filename, 'coverapi') and file_time(filename, 'coverapi', True):
        tree = open_xml(filename, 'coverapi')

    else:
        d = None
        list = None
        get =   'https://coverapi.store/embed/' + imdb +'/'
        
        #Delete the cache file if exists
        delete_cache(filename, 'coverapi')

        #Get the link(s) from coverapi
        if six.PY2 and data_json is None:
            from resources.lib.modules import scraper as cl
            scraper = cl.create_scraper()
            d = scraper.get(get).text
            #d = scraper.get(get).content

        if six.PY3 and data_json is None:
            
            #Cloudscraper works only on PY3
            if control.condVisibility('System.HasAddon(script.module.cloudscraper)'):
                from resources.lib.modules import cloudscraper as cl
                d = cl.make_request(get)
            
            else:
                from resources.lib.modules import scraper as cl
                scraper = cl.create_scraper()
                d = scraper.get(get).text

        if (d is None):
            z = re.search(r"We think.*a robot", d)

            if (z is None):
                dialog.ok('Error', 'Error getting data from coverapi.store. Please try again later.')
            
            else:
                dialog.ok('Error', 'You are temporarily IP banned from coverapi.store. Please try again later.')

            return

        z = re.search(r"news_id:.+'(.*?)'", d)
            
        if z is None:
            dialog.ok('Error', 'Error getting file id. Please try again later.')
            return
            
        now         = int( time.time() )
        news_id     = z.group(1)
        
        #Create XML Root for cache file
        root = ET.Element("catalog")

        if (type == 'movie'):

            if six.PY2:
                from resources.lib.modules import client

                link =   'https://coverapi.store/embed/' + imdb +'/'
                post_link = 'https://coverapi.store/engine/ajax/controller.php'
                headers = {'User-Agent': client.UserAgent, 'Referer': link}
                ihtml = client.request(post_link, post={'mod': 'players', 'news_id': str(news_id)}, headers=headers, XHR=True)

                if ihtml:
                    list = ihtml
            
            elif six.PY3:
                if control.condVisibility('System.HasAddon(script.module.cloudscraper)'):
                    list = cl.post_request(news_id)
                else:
                    from resources.lib.modules import client

                    link =   'https://coverapi.store/embed/' + imdb +'/'
                    post_link = 'https://coverapi.store/engine/ajax/controller.php'
                    headers = {'User-Agent': client.UserAgent, 'Referer': link}
                    ihtml = client.request(post_link, post={'mod': 'players', 'news_id': str(news_id)}, headers=headers, XHR=True)

                    if ihtml:
                        list = ihtml
            
            if (list is None):
                dialog.ok('Error', 'Error getting file link(s). Please try again later.')
                return
                
            data_json   = json.loads(list)

            if 'html5' in data_json:

                try:
                    file = data_json['html5']
                except:
                    file = data_json

                z = re.search(r"file:"'(.*?)'",", file)
                t = re.search(r"title:"'(.*?)'",", file)

                if (z is not None):
                    file_link = z.group(1)
                    file_link = file_link.strip('\"')

                    mo = ET.Element("movie") 
                    root.append (mo) 
                    tl = ET.SubElement(mo, "title")
                        
                    if (t is not None):
                        file_title = t.group(1)
                        file_title = file_title.strip('\"')
                        tl.text = file_title
                    else:
                        tl.text = "Movie"
                        
                    ml = ET.SubElement(mo, "link") 
                    ml.text = file_link
        #TV
        else:
            play_url    = 'https://coverapi.store/uploads/playlists/' + str(news_id) + '.txt?v=' + str(now)
                
            list        = urlopen(play_url)
            data_json   = json.loads(list.read())
                
            if 'playlist' in data_json:
                i = 0
                s = 0
                had_seasons = False

                #TV Shows with seasons
                for _item in data_json['playlist']:

                    if 'playlist' in _item:
                        had_seasons = True

                        season_name = _item['comment']
                        se = re.search(r'\b\d{1,2}', season_name)
                        s += 1

                        if (se is None):
                            seas = i
                        else:
                            seas = int(se.group(0))
                            
                        ses = ET.Element("season") 
                        root.append (ses) 
                        st = ET.SubElement(ses, "title")
                        st.text = season_name
                        sn = ET.SubElement(ses, "number")
                        sn.text = str(seas)

                        ep = ET.Element("episodes") 
                        ses.append (ep)
                            
                        for _index in _item['playlist']:
                            epp = ET.Element("episode") 
                            ep.append(epp)
                                
                            i += 1
                            episode_name    = _index['comment']
                            episode_url     = _index['file']
                            
                            e = re.search(r'\b\d{1,3}', _index['comment'])
                            if (e is None):
                                episode = i
                            else:
                                episode = e.group(0)

                            ept = ET.SubElement(epp, "title") 
                            ept.text = episode_name
                            epn = ET.SubElement(epp, "number") 
                            epn.text = str(episode)
                            epl = ET.SubElement(epp, "link") 
                            epl.text = episode_url

                #Do the dame for TV Shows with no seasons
                #We will add the season number for browsing
                if not had_seasons:
                    ses = ET.Element("season") 
                    root.append (ses)
                    st = ET.SubElement(ses, "title")
                    st.text = 'Season 1'
                    sn = ET.SubElement(ses, "number")
                    sn.text = str(1)
                        
                    ep = ET.Element("episodes") 
                    ses.append (ep)

                    for _item in data_json['playlist']:
                            
                        if 'playlist' not in _item:
                            epp = ET.Element("episode") 
                            ep.append(epp)

                            i += 1
                            episode_name    = _item['comment']
                            episode_url     = _item['file']
                            e = re.search(r'\b\d{1,3}', episode_name)
                            if (e is None):
                                episode = i
                            else:
                                episode = e.group(0)

                            ept = ET.SubElement(epp, "title") 
                            ept.text = episode_name
                            epn = ET.SubElement(epp, "number") 
                            epn.text = str(episode)
                            epl = ET.SubElement(epp, "link") 
                            epl.text = episode_url

        if data_json is None:
            dialog.ok('Error', 'Error getting data. Please try again later.')
            return
            
        tree = ET.ElementTree(root)
        write_xml(filename, tree, 'coverapi')

    return tree

def get_coverapi_file_link(imdb, season = '', episode = '', media_type = 'movie'):
    data = get_coverapi_data(imdb, media_type)

    file_link = None
    
    if media_type == 'movie':

        if not 'html5' in data:
            pass
                
        file_link = get_link(media_type, imdb, season, episode)

        if file_link == None:

            file = data['html5']
            z = re.search(r"file:"'(.*?)'",", file)
                    
            if (z is None):
                pass
                    
            file_link = z.group(1)
            file_link = file_link.strip('\"')
    
    return file_link

def file_exists(name, folder = ''):
    file_folder = 'resources/cache/'

    if ( folder != ''):
        file_folder += folder + '/'

    file_folder += name

    file_path = os.path.join(home, file_folder )

    if exists(file_path):
        return True
    else:
        return False
    
def file_time(name, folder = '', xml = False):
    file_folder = 'resources/cache/'

    if ( folder != ''):
        file_folder += folder + '/'

    file_folder += name

    file_path = os.path.join(home, file_folder)

    if not os.path.exists(file_path):
        return False
    
    file_time = cache_xml_time if xml else cache_time
    
    now = int( time.time() )

    if os.path.getmtime(file_path) > (now - file_time):
        return True
    else:
        return False

# Write XML File
def write_xml(name, tree, folder = ''):
    file_folder = 'resources/cache/'

    if ( folder != ''):
        file_folder += folder + '/'

    file_folder += name

    file_path = os.path.join(home, file_folder)

    if os.path.exists(file_path):
        os.remove(file_path)
    
    with open (file_path, "wb") as files : 
        tree.write(files)
        
def open_xml(name, folder = ''):
    file_folder = 'resources/cache/'

    if ( folder != ''):
        file_folder += folder + '/'

    file_folder += name

    file_path = os.path.join(home, file_folder)

    if not os.path.exists(file_path):
        return None

    return ET.parse(file_path).getroot()

def open_cache(name, folder = ''):
    file_folder = 'resources/cache/'

    if ( folder != ''):
        file_folder += folder + '/'

    file_folder += name

    file_path = os.path.join(home, file_folder)

    if not os.path.exists(file_path):
        return None
    
    return json.load(open(file_path))

def write_cache(name, data, folder = ''):
    file_folder = 'resources/cache/'

    if ( folder != ''):
        file_folder += folder + '/'

    file_folder += name

    file_path = os.path.join(home, file_folder)

    if os.path.exists(file_path):
        os.remove(file_path)
    
    with open(file_path, 'w') as f:
        json.dump(data, f)

def delete_cache(name, folder = ''):
    file_folder = 'resources/cache/'

    if ( folder != ''):
        file_folder += folder + '/'

    file_folder += name

    file_path = os.path.join(home, file_folder)

    if os.path.exists(file_path):
        os.remove(file_path)

def _is_cache_valid(cached_time, cache_timeout):
    now = int(time.time())
    diff = now - cached_time
    return (cache_timeout * cache_time) > diff

def cache_clear_search(select):
    try:
        cursor = _get_connection_cursor_search()
        if select == 'all':
            table = ['movies', 'tvshow', 'people', 'yt', 'keywords', 'companies', 'collections']
        elif not isinstance(select, list):
            table = [select]
        for t in table:
            try:
                cursor.execute("DROP TABLE IF EXISTS %s" % t)
                cursor.execute("VACUUM")
                cursor.commit()
            except:
                pass
    except:
        pass

def _get_connection_search():
    control.makeFile(control.dataPath)
    conn = db.connect(control.searchFile)
    conn.row_factory = _dict_factory
    return conn

def _get_connection_bookmarks():
    control.makeFile(control.dataPath)
    conn = db.connect(control.bookmarksFile)
    conn.row_factory = _dict_factory
    return conn

def _get_connection_history():
    control.makeFile(control.dataPath)
    conn = db.connect(control.historyFile)
    conn.row_factory = _dict_factory
    return conn

def _get_connection_links():
    control.makeFile(control.dataPath)
    conn = db.connect(control.cacheFile)
    conn.row_factory = _dict_factory
    return conn

def _get_connection_favorites():
    control.makeFile(control.dataPath)
    conn = db.connect(control.favoritesFile)
    conn.row_factory = _dict_factory
    return conn

def _get_connection_likes():
    control.makeFile(control.dataPath)
    conn = db.connect(control.likesFile)
    conn.row_factory = _dict_factory
    return conn

def _get_connection_cursor_search():
    conn = _get_connection_search()
    return conn.cursor()

def _get_connection_cursor_bookmarks():
    conn = _get_connection_bookmarks()
    return conn.cursor()

def _get_connection_cursor_links():
    conn = _get_connection_links()
    return conn.cursor()

def _get_connection_cursor_history():
    conn = _get_connection_history()
    return conn.cursor()

def _get_connection_cursor_favorites():
    conn = _get_connection_favorites()
    return conn.cursor()

def _get_connection_cursor_likes():
    conn = _get_connection_likes()
    return conn.cursor()

def _generate_md5(*args):
    md5_hash = hashlib.md5()
    [md5_hash.update(six.ensure_binary(arg, errors='replace')) for arg in args]
    return str(md5_hash.hexdigest())


def _get_function_name(function_instance):
    return re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', repr(function_instance))


def _hash_function(function_instance, *args):
    return _get_function_name(function_instance) + _generate_md5(args)


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def cache_clear_all():
    cache_clear()
    cache_clear_providers()
    cache_clear_links()

def cache_clear_links():
    try:
        cursor = _get_connection_cursor_links()
        cursor.execute("DROP TABLE IF EXISTS %s" % 'links')
        cursor.execute("VACUUM")
        cursor.commit()
    except:
        pass

def clean_history(site=True):
    try:
        cursor = _get_connection_cursor_bookmarks()
        cursor.execute("DROP TABLE IF EXISTS %s" % 'bookmarks')
        cursor.execute("VACUUM")
        cursor.commit()
    except:
        pass

    try:
        cursor = _get_connection_cursor_history()

        table = ['movie', 'tvshow']
        for t in table:
            try:
                cursor.execute("DROP TABLE IF EXISTS %s" % t)
                cursor.execute("VACUUM")
                cursor.commit()
            except:
                pass

        cursor.execute("DROP TABLE IF EXISTS %s" % 'bookmarks')
        cursor.execute("VACUUM")
        cursor.commit()
    except:
        pass
    
    if site and streamdbApi != '' and len(streamdbApi) > 0:
        updlink  = 'https://streamdb.homebrewgr.info/index.php?action=remove-history&api_key=%s' % (streamdbApi)
        try:
            urlopen(updlink)
        except:
            xbmc.log('Something went wrong (history link)', xbmc.LOGINFO)
    
def clean_favorites(site=True):
    try:
        cursor = _get_connection_cursor_favorites()
        table = ['movie', 'tvshow']
        for t in table:
            try:
                cursor.execute("DROP TABLE IF EXISTS %s" % t)
                cursor.execute("VACUUM")
                cursor.commit()
            except:
                pass
    except:
        pass
    
    if site and streamdbApi != '' and len(streamdbApi) > 0:
        updlink  = 'https://streamdb.homebrewgr.info/index.php?action=remove-favorites&api_key=%s' % (streamdbApi)
        try:
            urlopen(updlink)
        except:
            xbmc.log('Something went wrong (favorites link)', xbmc.LOGINFO)

def clean_likes(site=True):
    try:
        cursor = _get_connection_cursor_likes()
        table = ['movie', 'tvshow']
        for t in table:
            try:
                cursor.execute("DROP TABLE IF EXISTS %s" % t)
                cursor.execute("VACUUM")
                cursor.commit()
            except:
                pass
    except:
        pass

    if site and streamdbApi != '' and len(streamdbApi) > 0:
        updlink  = 'https://streamdb.homebrewgr.info/index.php?action=remove-likes&api_key=%s' % (streamdbApi)
        try:
            urlopen(updlink)
        except:
            xbmc.log('Something went wrong (likes link)', xbmc.LOGINFO)

def cache_clear_providers():
    file_folder = 'resources/cache/coverapi/'
    file_path = os.path.join(home, file_folder)
    filelist = [ f for f in os.listdir(file_path) if f.endswith(".xml") ]

    for f in filelist:
        os.remove(os.path.join(file_path, f))

def cache_clear():
    file_folder = 'resources/cache/'

    file_path = os.path.join(home, file_folder)

    filelist = [ f for f in os.listdir(file_path) if f.endswith(".json") ]

    for f in filelist:
        os.remove(os.path.join(file_path, f))

def clean_settings():
    current_user_settings = []
    removed_settings = []
    active_settings = []
    def _make_content(dict_object):
        if kodi_version >= 18:
            content = '<settings version="2">'
            for item in dict_object:
                if item['id'] in active_settings:
                    if 'default' in item and 'value' in item:
                        content += '\n    <setting id="%s" default="%s">%s</setting>' % (item['id'], item['default'], item['value'])
                    elif 'default' in item:
                        content += '\n    <setting id="%s" default="%s"></setting>' % (item['id'], item['default'])
                    elif 'value' in item:
                        content += '\n    <setting id="%s">%s</setting>' % (item['id'], item['value'])
                    else:
                        content += '\n    <setting id="%s"></setting>'
                else:
                    removed_settings.append(item)
        else:
            content = '<settings>'
            for item in dict_object:
                if item['id'] in active_settings:
                    if 'value' in item:
                        content += '\n    <setting id="%s" value="%s" />' % (item['id'], item['value'])
                    else:
                        content += '\n    <setting id="%s" value="" />' % item['id']
                else:
                    removed_settings.append(item)
        content += '\n</settings>'
        return content
    try:
        root = ET.parse(control.settingsPath).getroot()
        for item in root.findall('./category/setting'):
            setting_id = item.get('id')
            if setting_id:
                active_settings.append(setting_id)
        root = ET.parse(control.settingsFile).getroot()
        for item in root:
            dict_item = {}
            setting_id = item.get('id')
            setting_default = item.get('default')
            if kodi_version >= 18:
                setting_value = item.text
            else:
                setting_value = item.get('value')
            dict_item['id'] = setting_id
            if setting_value:
                dict_item['value'] = setting_value
            if setting_default:
                dict_item['default'] = setting_default
            current_user_settings.append(dict_item)
        new_content = _make_content(current_user_settings)
        nfo_file = control.openFile(control.settingsFile, 'w')
        nfo_file.write(new_content)
        nfo_file.close()

        if os.path.exists(control.syncFile):
            os.remove(control.syncFile)
            
        control.infoDialog('Clean Settings: %s Old Settings Removed' % (str(len(removed_settings))))
    except:
        log_utils.log('clean_settings', 1)
        control.infoDialog('Clean Settings: Error Cleaning Settings')
        return