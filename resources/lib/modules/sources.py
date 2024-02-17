# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import datetime
import random

import simplejson as json
import six
import urllib
from six.moves import urllib_parse, urllib_request
from kodi_six import xbmc, xbmcgui

try:
    #from infotagger.listitem import ListItemInfoTag
    from resources.lib.modules.listitem import ListItemInfoTag
except:
    pass

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cache
from resources.lib.modules import log_utils

try:
    from six.moves import urllib_request
    urlopen = urllib_request.urlopen
except ImportError:
    import requests
    urlopen = requests.Session()

kodi_version = control.getKodiVersion()
streamdbApi = control.setting('streamdb.api')
noIp = control.setting('dontsendip')

class sources:
    def __init__(self):
        control.moderator()
        self.upd_link = 'https://streamdb.homebrewgr.info/index.php?action=update-views&imdb=%s'

    def errorForSources(self):
        control.infoDialog('Error : No Stream Available.', sound=False, icon='INFO')

    def play(self, title, year, media_type, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select, fileurl):
        
        if media_type == 'yt':
            from resources.lib.modules import trailer
            trailer.source().get(title, fileurl, 0, 0, 0, 0, 0)
            return
        else:
            try:
                root = None
                filename    = imdb + '.xml'
                
                if not cache.file_exists(filename, 'coverapi') and not cache.file_time(filename, 'coverapi', True):
                    cache.get_coverapi_data(imdb, 'movie')

                if cache.file_exists(filename, 'coverapi') and cache.file_time(filename, 'coverapi', True):
                    root = cache.open_xml(filename, 'coverapi')

                if (root is None):
                    raise Exception()
                                    
                if (media_type == 'movie'):
                    try:
                        file_link = root.find('movie').findtext('link')
                    except:
                        pass
                
                elif (media_type == 'tv'):
                    
                    if fileurl == None:
                        raise Exception()
                    
                    file_link = fileurl

                try:
                    upd_url = self.upd_link % (imdb)
                    
                    if noIp:
                        upd_url  += '&noip=true'

                    urlopen(upd_url)
                    control.sleep(100)
                except:
                    pass
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok('Error', 'Error getting file URL. Please try again later.')
                pass
        
        try:
            from resources.lib.modules.player import player
            file_link = file_link.replace('https://', 'http://')
            player().run(title, year, season, episode, imdb, tmdb, tvdb, file_link, meta)
        except:
            log_utils.log('play', 1)
            pass