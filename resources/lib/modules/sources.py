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
                #Check if the link is in the DB
                file_link = cache.get_link(media_type, imdb, season, episode)
                data_got = False

                #Try to get this link from the links pool
                if file_link is None:
                    if streamdbApi != '' and len(streamdbApi) > 0:
                        get_link  = 'https://streamdb.homebrewgr.info/index.php?action=get-link&api_key=%s&imdb=%s&se=%s&ep=%s' % (streamdbApi, imdb, season, episode)

                        try:
                            response  = urlopen(get_link)
                            data_json = json.loads(response.read())
                            
                            if 'status' not in data_json or data_json["status"] != "OK" or 'link' not in data_json:
                                raise Exception()

                            file_link = data_json["link"]

                            try:
                                file_link = urllib.parse.unquote_plus(file_link)
                            except:
                                file_link = urllib.unquote(file_link)

                            cache.add_link(file_link, media_type, imdb, season, episode)
                        except:
                            file_link = None
                
                #Try to get the link from coverapi 
                if file_link is None:
                    data = cache.get_coverapi_data(imdb, media_type)

                    if media_type == 'movie':
                        
                        if not 'html5' in data:
                            raise Exception()
                        
                        file_link = cache.get_link(media_type, imdb, season, episode)

                        if file_link == None:

                            file = data['html5']
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
                else:
                    data_got = True

                file_link = file_link.replace('https://', 'http://')

                try:
                    upd_url = self.upd_link % (imdb)
                    
                    if noIp:
                        upd_url  += '&noip=true'

                    urlopen(upd_url)
                except:
                    pass

                if not data_got and streamdbApi != '' and len(streamdbApi) > 0:
                    add_link  = 'https://streamdb.homebrewgr.info/index.php?action=add-link&imdb=%s&se=%s&ep=%s' % (imdb, season, episode)
                    try:
                        add_link  += '&link=%s' % (urllib.parse.quote_plus(file_link))
                        urlopen(add_link)
                    except:
                        add_link  += '&link=%s' % (urllib.quote(file_link))
                        urlopen(add_link)
                control.sleep(100)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok('Error', 'Error getting file URL. Please try again later.')
                pass
        
        try:
            from resources.lib.modules.player import player
            player().run(title, year, season, episode, imdb, tmdb, tvdb, file_link, meta)
        except:
            log_utils.log('play', 1)
            pass