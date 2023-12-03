# -*- coding: utf-8 -*-

import re
import os
from os.path import exists
import time
import json
from kodi_six import xbmc, xbmcgui
import xbmcaddon
from resources.lib.modules import cloudscraper as cl
from six.moves import urllib_request

urlopen = urllib_request.urlopen

#21600 = 6hrs; default 3600 = 1 hour
cache_time = 21600

def get_json_data(name, url):
    filename    = name + '.json'
    xbmc.log('get_json_data: ' + url, xbmc.LOGINFO)
    xbmc.log('get_json_data: ' + filename, xbmc.LOGINFO)
    if file_exists(filename) and file_time(filename):
        data_json = open_cache(filename)
    else:
        try:
            response    = urlopen(url) 
            data_json   = json.loads(response.read())

        except:
            pass
        
        write_cache(filename, data_json)
    
    return data_json

def get_cover_data(imdb):
    filename    = imdb + '.json'

    if file_exists(filename) and file_time(filename):
        xbmc.log('file found and data loaded from: ' + filename, xbmc.LOGINFO)
        data_json = open_cache(filename)
    else:
        xbmc.log('file not found: ' + filename, xbmc.LOGINFO)
        get =   'https://coverapi.store/embed/' + imdb +'/'
        d = cl.make_request(get)
        z = re.search(r"news_id:.+'(.*?)'", d)
        
        if (z is None):
            xbmc.log('news_id not found for: ' + get, xbmc.LOGINFO)
            dialog = xbmcgui.Dialog()
            dialog.ok('Error', 'Error getting playlist info. Please try again later.')
            pass
        
        now         = int( time.time() )
        news_id     = z.group(1)
        play_url    = 'https://coverapi.store/uploads/playlists/' + str(news_id) + '.txt?v=' + str(now)
        list        = cl.make_request(play_url)
        data_json   = json.loads(list.read())
        write_cache(filename, data_json)
    
    return data_json

def file_exists(name):
    home = xbmcaddon.Addon().getAddonInfo('path')
    file_path = os.path.join(home, 'resources/cache/' + name)

    if exists(file_path):
        return True
    else:
        return False

def file_time(name):
    home = xbmcaddon.Addon().getAddonInfo('path')
    file_path = os.path.join(home, 'resources/cache/' + name)

    if not os.path.exists(file_path):
        return False
    
    now = int( time.time() )

    if os.path.getmtime(file_path) > (now - cache_time):
        return True
    else:
        return False

def open_cache(name):
    home = xbmcaddon.Addon().getAddonInfo('path')
    file_path = os.path.join(home, 'resources/cache/' + name)

    if not os.path.exists(file_path):
        xbmc.log('Cache file not found: ' + file_path, xbmc.LOGINFO)
        return False
    
    return json.load(open(file_path))

def write_cache(name, data):
    home = xbmcaddon.Addon().getAddonInfo('path')
    file_path = os.path.join(home, 'resources/cache/' + name)

    if os.path.exists(file_path):
        os.remove(file_path)
    
    with open(file_path, 'w') as f:
        json.dump(data, f)