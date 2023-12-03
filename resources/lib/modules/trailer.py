# -*- coding: utf-8 -*-

import re
import sys
import random

import six
from six.moves.urllib_parse import quote_plus

from resources.lib.modules import client
from resources.lib.modules import client_utils
from resources.lib.modules import control
import simplejson as json
from kodi_six import xbmc, xbmcgui

try:
    #from infotagger.listitem import ListItemInfoTag
    from resources.lib.modules.listitem import ListItemInfoTag
except:
    pass

try:
    from six.moves import urllib_request
    urlopen = urllib_request.urlopen
except ImportError:
    import requests
    urlopen = requests.Session()

kodi_version = control.getKodiVersion()

class source:
    def __init__(self):
        self.content = control.infoLabel('Container.Content')
        self.lang = 'en' if control.setting('info.language') == 'English' else 'el'
        self.youtube_keys = ['AIzaSyCGfYB9l1K7E2H5jKrl5xk0MHTHtODBego', 'AIzaSyBnZOwDu5u5IjQ5xs5P04gR7oRXK-xfVRE']
        if control.condVisibility('System.HasAddon(plugin.video.youtube)'):
            self.youtube_key = control.addon('plugin.video.youtube').getSetting('youtube.api.key') or ''
        else:
            self.youtube_key = ''
        if not self.youtube_key:
            self.youtube_key = control.setting('youtube.api') or ''
        if not self.youtube_key:
            self.youtube_key = random.choice(self.youtube_keys)
        self.youtube_link = 'https://youtube.com'
        self.youtube_watch_link = self.youtube_link + '/watch?v='
        #self.youtube_plugin_url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s'
        self.youtube_plugin_url = 'plugin://plugin.video.youtube/play/?video_id='
        self.youtube_lang_link = '' if self.lang == 'en' else '&relevanceLanguage=%s' % self.lang
        self.youtube_search_link = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=10&q=%s&key=%s%s' % ('%s', '%s', self.youtube_lang_link)

    def youtube_trailers(self, name='', url='', tmdb='', imdb='', season='', episode=''):
        trailer_list = []
        try:
            if self.content not in ['tvshows', 'seasons', 'episodes']:
                name += ' %s' % control.infoLabel('ListItem.Year')
            elif self.content in ['seasons', 'episodes']:
                if season and episode:
                    name += ' %sx%02d' % (season, int(episode))
                elif season:
                    name += ' season %01d' % int(season)
            if self.content != 'episodes':
                name += ' trailer'
            query = quote_plus(name)
            url = self.youtube_search_link % (query, self.youtube_key)
            result = client.scrapePage(url, timeout='30').json()
            if (not result) or ('error' in result):
                url = self.youtube_search_link % (query, self.youtube_keys[0])
                result = client.scrapePage(url, timeout='30').json()
            if (not result) or ('error' in result):
                url = self.youtube_search_link % (query, self.youtube_keys[1])
                result = client.scrapePage(url, timeout='30').json()
            if (not result) or ('error' in result):
                return trailer_list
            results = result['items']
            if not results:
                return trailer_list
            for i in results:
                trailer_list.append({'source': 'YouTube', 'title': i.get('snippet', {}).get('title', ''), 'url': i.get('id', {}).get('videoId', ''), 'type': 'Trailer'})
            return trailer_list
        except:
            #log_utils.log('youtube_trailers', 1)
            return trailer_list


    def get(self, name='', url='', tmdb='', imdb='', season='', episode='', windowedtrailer=0):
        try:
            list = []
            if url != '' :
                uri = self.youtube_plugin_url + url
                list.append({'source': 'YouTube', 'title': name, 'url': uri, 'type': 'Video'})
            
                try:
                    upd_link  = 'https://streamdb.homebrewgr.info/index.php?action=update-yt-views&vid=%s' % (url)
                    xbmc.log('Action: ' + upd_link, xbmc.LOGINFO)
                    urlopen(upd_link)
                except:
                    pass
                control.idle()
                return self.item_play(list[0], windowedtrailer)
            else:
                try:
                    link = 'https://streamdb.homebrewgr.info/index.php?action=get-trailer&imdb=%s' % (imdb)
                    response  = urlopen(link)
                    data_json = json.loads(response.read())
                    
                    if 'status' not in data_json or data_json["status"] != "OK" or 'data' not in data_json:
                        raise Exception()

                    for item in data_json['data']:
                        if item['type'] != 'Trailer':
                            continue
                        yturl = self.youtube_plugin_url + item["video_id"]
                        list.append({'source': 'YouTube', 'title': item['name'], 'url': yturl, 'type': item["type"]})

                    control.idle()

                    return self.item_play(list[0], windowedtrailer)
                except:
                    dialog = xbmcgui.Dialog()
                    dialog.ok('Error', 'Error getting trailer URL. Please try again later.')
        except:
            #log_utils.log('get', 1)
            return

    def item_play(self, result, windowedtrailer):
        try:
            control.idle()
            if not result:
                return control.infoDialog('No trailer found')
            title = result.get('title', '')
            if not title:
                title = control.infoLabel('ListItem.Title')
            url = result.get('url', '')
            if not url:
                return control.infoDialog('No trailer url found')
            item = control.item(label=title, path=url)
            item.setProperty('IsPlayable', 'true')
            if kodi_version >= 20:
                info_tag = ListItemInfoTag(item, 'video')
                info_tag.set_info({'title': title})
            else:
                item.setInfo(type='video', infoLabels={'title': title})
            control.resolve(handle=int(sys.argv[1]), succeeded=True, listitem=item)
            if windowedtrailer == 1:
                control.sleep(1000)
                while control.player.isPlayingVideo():
                    control.sleep(1000)
                control.execute('Dialog.Close(%s, true)' % control.getCurrentDialogId)
        except:
            #log_utils.log('item_play', 1)
            return
    
    def select_items(self, results):
        try:
            if not results:
                return
            if self.trailer_specials == 'true':
                results = [i for i in results if i.get('type') == 'Trailer'] + [i for i in results if i.get('type') != 'Trailer']
            else:
                results = [i for i in results if i.get('type') == 'Trailer']
            if self.trailer_mode == '1':
                items = ['%s | %s (%s)' % (i.get('source', ''), i.get('title', ''), i.get('type', 'N/A')) for i in results]
                select = control.selectDialog(items, 'Trailers')
                if select == -1:
                    return 'canceled'
                return results[select]
            items = [i.get('url') for i in results]
            for vid_id in items:
                url = self.worker(vid_id)
                if url:
                    return url
            return
        except:
            #log_utils.log('select_items', 1)
            return

    def worker(self, url):
        try:
            if not url:
                raise Exception()
            url = url.replace('http://', 'https://')
            url = url.replace('www.youtube.com', 'youtube.com')
            if url.startswith(self.youtube_link):
                url = self.resolve(url)
                if not url:
                    raise Exception()
            elif not url.startswith('http'):
                url = self.youtube_watch_link + url
                url = self.resolve(url)
                if not url:
                    raise Exception()
            return url
        except:
            #log_utils.log('worker', 1)
            return


    def resolve(self, url):
        try:
            id = url.split('?v=')[-1].split('/')[-1].split('?')[0].split('&')[0]
            url = self.youtube_watch_link + id
            result = client.scrapePage(url, timeout='30').text
            message = client_utils.parseDOM(result, 'div', attrs={'id': 'unavailable-submessage'})
            message = ''.join(message)
            alert = client_utils.parseDOM(result, 'div', attrs={'id': 'watch7-notification-area'})
            if len(alert) > 0:
                raise Exception()
            if re.search('[a-zA-Z]', message):
                raise Exception()
            url = self.youtube_plugin_url + id
            return url
        except:
            #log_utils.log('resolve', 1)
            return


