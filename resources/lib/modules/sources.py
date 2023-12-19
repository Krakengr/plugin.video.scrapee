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
                data = None

                #Check if the link is in the DB
                file_link = cache.get_link(media_type, imdb, season, episode)
                
                #Try to get this link from the links pool
                if file_link is None:
                    data = cache.get_coverapi_data(imdb, media_type)

                #Got the data. Try to find the link(s).
                if file_link is None and data is not None:
                    if media_type == 'movie':
                        
                        if not 'html5' in data:
                            raise Exception()
                        
                        try:
                            file = data['html5']
                        except:
                            file = data
                            
                        z = re.search(r"file:"'(.*?)'",", file)

                        if (z is None):
                            raise Exception()
                            
                        file_link = z.group(1)
                        file_link = file_link.strip('\"')
                        cache.add_link(file_link, media_type, imdb, season, episode)

                    elif media_type == 'tv':
                        
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