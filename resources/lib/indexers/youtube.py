# -*- coding: utf-8 -*-

import re
import os
import sys
import datetime

import simplejson as json
import six
from six.moves import range, urllib_parse, urllib_request
from kodi_six import xbmc, xbmcplugin, xbmcgui

try:
    #from infotagger.listitem import ListItemInfoTag
    from resources.lib.modules.listitem import ListItemInfoTag
except:
    pass

try:
    urlopen = urllib_request.urlopen
except ImportError:
    import requests
    urlopen = requests.Session()

from resources.lib.indexers import navigator

from resources.lib.modules import bookmarks
from resources.lib.modules import cache
from resources.lib.modules import client_utils
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import favorites
from resources.lib.modules import history
from resources.lib.modules import views

#from resources.lib.modules import log_utils

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

params      = dict(urllib_parse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()
action      = 'ytube'
sysaddon    = sys.argv[0]
genre       = params.get('genre')
geturl      = params.get('url')
page        = params.get('page')
control.moderator()
kodi_version = control.getKodiVersion()

class ytube:
    def __init__(self):
        self.list = []
        self.datetime = datetime.datetime.utcnow()
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.year_date = (self.datetime - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        self.month_date = (self.datetime - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.lang = 'en' if control.setting('info.language') == 'English' else 'el'
        self.items_per_page = str(control.setting('items.per.page')) or '20'
        self.curr_page = page if page is not None else 1
        self.curr_url = '%s?action=ytube&url=%s' % (sysaddon, geturl)

        if not genre is None:
            self.curr_url += '&genre=%s' % (genre)

        self.curr_url += '&page=%s' % (self.curr_page)

        self.main_link = 'https://streamdb.homebrewgr.info/index.php?action=yt&lang=' + self.lang + '&items=' + self.items_per_page
        self.genres_link = 'https://streamdb.homebrewgr.info/index.php?action=yt-genres'
        self.by_genre_link = self.main_link + '&cat=%s&page=' + str(self.curr_page)
        self.search_link = self.main_link + '&do=search&title=%s&page=' + str(self.curr_page)
        self.popular_link = self.main_link + '&do=popular&page=' + str(self.curr_page)
        self.latest_link = self.main_link + '&do=latest&page=' + str(self.curr_page)
        self.main_link += '&page=' + str(self.curr_page)
        self.youtube_plugin_url = 'plugin://plugin.video.youtube/play/?video_id='
        self.youtube_url = 'https://www.youtube.com/watch?v='

    def get(self, url):
        if url == None:
            pass
        elif url == 'most_popular':
            self.getPopular()
            self.movieDirectory(self.list)
            return self.list
        elif url == 'latest':
            self.getLatest()
            self.movieDirectory(self.list)
            return self.list
        elif url == 'genres':
            self.getGenres()
            return self.list
        elif url == 'by_genre':
            self.getByGenre()
            self.movieDirectory(self.list)
            return self.list
        elif url == 'favorites':
            self.favorites()
            return self.list
        elif url == 'history':
            self.history()
            return self.list
    
    def search_term_menu(self, select):
        navigator.navigator().addDirectoryItem('New Search...', 'yt_searchterm&select=%s' % select, 'search.png', 'DefaultMovies.png')
        dbcon = database.connect(control.searchFile)
        dbcur = dbcon.cursor()
        try:
            dbcur.executescript("CREATE TABLE IF NOT EXISTS %s (ID Integer PRIMARY KEY AUTOINCREMENT, term);" % select)
        except:
            pass
        dbcur.execute("SELECT * FROM %s ORDER BY ID DESC" % select)
        delete_option = False
        for (id, term) in dbcur.fetchall():
            delete_option = True
            navigator.navigator().addDirectoryItem(term.title(), 'yt_searchterm&select=%s&name=%s' % (select, term), 'search.png', 'DefaultMovies.png')
        dbcur.close()
        if delete_option:
            navigator.navigator().addDirectoryItem('Clear Search History', 'clear_search_cache&select=%s' % select, 'tools.png', 'DefaultAddonProgram.png')
        navigator.navigator().endDirectory(cached=False)

    def search_term(self, select, q=None):
        control.idle()
        if (q == None or q == ''):
            k = control.keyboard('', 'Search') ; k.doModal()
            q = k.getText() if k.isConfirmed() else None
        if (q == None or q == ''):
            return
        q = q.lower()
        dbcon = database.connect(control.searchFile)
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM %s WHERE term = ?" % select, (q,))
        dbcur.execute("INSERT INTO %s VALUES (?, ?)" % select, (None, q))
        dbcon.commit()
        dbcur.close()
        url = self.search_link % urllib_parse.quote_plus(q)
        self.getBySearch(url)
        self.movieDirectory(self.list)
    
    def getBySearch(self, url):
        try:
            response    = urlopen(url)
            data_json   = json.loads(response.read())
            
            
            if data_json["status"] != "OK":
                raise Exception()
            
            self.buildMovieArr(data_json, True)
        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def history(self):
        try:
            items = history.getHistory('movie')
            items = [(i[0].encode('utf-8'), eval(i[1].encode('utf-8'))) for i in items]
            self.list = [i[1] for i in items]
            for k, i in items:
                if not 'year' in i:
                    i['year'] = '0'
                
                if not 'name' in i:
                    i['name'] = '%s (%s)' % (i['title'], i['year'])
                
                try:
                    #i['title'] = i['title'].encode('utf-8')
                    i['title'] = client_utils.replaceHTMLCodes(i['title'])
                except:
                    pass
               
                try:
                    #i['name'] = i['name'].encode('utf-8')
                    i['name'] = client_utils.replaceHTMLCodes(i['name'])
                except:
                    pass
                
                if not 'duration' in i:
                    i['duration'] = '0'
                if not 'imdb' in i:
                    i['imdb'] = '0'
                if not 'tmdb' in i:
                    i['tmdb'] = '0'
                if not 'tvdb' in i:
                    i['tvdb'] = '0'
                if not 'poster' in i:
                    i['poster'] = '0'
                if not 'poster_path' in i:
                    i['poster_path'] = i['poster']
                if not 'backdrop_path' in i:
                    i['backdrop_path'] = i['poster']
                if not 'banner' in i:
                    i['banner'] = i['poster']
                if not 'fanart' in i:
                    i['fanart'] = i['poster']
                if not 'originaltitle' in i:
                    i['originaltitle'] = i['name']

            self.list = sorted(self.list, key=lambda k: k['title'])
            
            self.movieDirectory(self.list)
        except:
            #log_utils.log('favorites', 1)
            return
        
    def favorites(self):
        try:
            items = favorites.getFavorites('movie')
            items = [(i[0].encode('utf-8'), eval(i[1].encode('utf-8'))) for i in items]
            self.list = [i[1] for i in items]
            
            for k, i in items:
                if not 'year' in i:
                    i['year'] = '0'
                
                if not 'name' in i:
                    i['name'] = '%s (%s)' % (i['title'], i['year'])
                
                try:
                    #i['title'] = i['title'].encode('utf-8')
                    i['title'] = client_utils.replaceHTMLCodes(i['title'])
                except:
                    pass
               
                try:
                    #i['name'] = i['name'].encode('utf-8')
                    i['name'] = client_utils.replaceHTMLCodes(i['name'])
                except:
                    pass
                
                if not 'duration' in i:
                    i['duration'] = '0'
                if not 'imdb' in i:
                    i['imdb'] = '0'
                if not 'tmdb' in i:
                    i['tmdb'] = '0'
                if not 'tvdb' in i:
                    i['tvdb'] = '0'
                if not 'poster' in i:
                    i['poster'] = '0'
                if not 'poster_path' in i:
                    i['poster_path'] = i['poster']
                if not 'backdrop_path' in i:
                    i['backdrop_path'] = i['poster']
                if not 'banner' in i:
                    i['banner'] = i['poster']
                if not 'fanart' in i:
                    i['fanart'] = i['poster']
                if not 'originaltitle' in i:
                    i['originaltitle'] = i['name']

            self.list = sorted(self.list, key=lambda k: k['title'])
            
            self.movieDirectory(self.list)
        except:
            #log_utils.log('favorites', 1)
            return
    
    def getByGenre(self):
        try:
            url         = self.by_genre_link % (genre)
            xbmc.log('Action: ' + url, xbmc.LOGINFO)
            name        = 'yt_by_playlist-' + str(genre) + '_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            self.buildMovieArr(data_json)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def getGenres(self):
        try:
            url         = self.genres_link
            name        = 'yt_playlists'
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            items = data_json['data']

            for item in items:
                #label = '%s (%s)' % (item['name'], item['items'])
                #num = item['items']
                id = str(item['id'])
                name  = str(item['name'])
               
                self.list.append({'name': name, 'url': 'by_genre', 'genre': id, 'image': 'genres.png', 'action': 'movies'})

            self.addDirectory(self.list)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
            
    def getLatest(self):
        try:
            url         = self.latest_link
            name        = 'latest_yt_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            self.buildMovieArr(data_json)
        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass
        return self.list
    
    def getPopular(self):
        try:
            url         = self.popular_link
            name        = 'popular_yt_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)
            if data_json["status"] != "OK":
                raise Exception()
                
            self.buildMovieArr(data_json)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def buildMovieArr(self, data, search = False):
        items           = data['data']
        
        total_pages     = int(data["total_pages"])
        curr_page       = int(data["page"])

        if search:
            has_next        = False
            has_prev        = False
            prev            = None
            next_page       = None
        else:
            has_next        = True if total_pages > curr_page else False
            has_prev        = True if curr_page > 2 else False
            prev            = self.curr_url + 'page=%s' % (str(1)) if (curr_page == 1) else self.curr_url + 'page=%s' % (str(curr_page - 1))
            next_page       = '%s&page=%s' % (self.curr_url.split('&page=', 1)[0], str(curr_page + 1))
        
        for item in items:
            title = item['title']
            title = client_utils.replaceHTMLCodes(title)
            originaltitle = item['title']
            originaltitle = client_utils.replaceHTMLCodes(originaltitle)
            description = item['description']
            description = client_utils.replaceHTMLCodes(description)
            
            id              = item['id']
            url             = item['url']
            video_id        = item['video_id']
            plugin_url      = self.youtube_plugin_url + str(video_id)
            yt_url          = self.youtube_url + str(video_id)
            cast            = None
            genres          = None
            poster_path     = item['poster_path']
            backdrop_path   = item['backdrop_path']
            
            self.list.append({'id': id, 'title': title, 'originaltitle': originaltitle, 'description': description, 'backdrop_path': backdrop_path, 'poster_path': poster_path, 'url': url, 'plugin_url': plugin_url, 'yt_url': yt_url, 'video_id': video_id, 'cast': cast, 'genres': genres, 'prev': prev, 'next': next_page, 'has_next': has_next, 'has_prev': has_prev})

    def movieDirectory(self, items):
        if items == None or len(items) == 0:
            control.idle()
        
        sysaddon = sys.argv[0]
        syshandle = int(sys.argv[1])
        #indicators = playcount.getMovieIndicators()
        playbackMenu = 'Auto Play'
        isPlayable  = False
        nextMenu = '[I]Next Page[/I]'
        watchedMenu = 'Mark as Watched'
        unwatchedMenu = 'Mark as Unwatched'
        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()
        addonFanart = control.addonFanart()
       
        try:
            favitems = favorites.getFavorites('yt')
            favitems = [i[0] for i in favitems]
        except:
            pass
        
        for i in items:
            try:
                label = '%s' % (i['title'])
                video_id = i['video_id']
                systitle = urllib_parse.quote_plus(label)
                meta = dict((k,v) for k, v in six.iteritems(i) if not v == '0')
                meta.update({'mediatype': 'movie'})

                if not 'runtime' in i:
                    meta.update({'duration': '120'})
                elif i['runtime'] == '0':
                    meta.update({'duration': '120'})
                else:
                    meta.update({'duration': i['runtime']})
                
                try:
                    meta.update({'duration': str(int(meta['duration']) * 60)})
                except:
                    pass
                
                poster = i['poster_path']
                descr = i['description'] if 'description' in i else ''
                #genres = i['genres'] if 'genres' in i else ''
                meta.update({'poster': i['poster_path']})
                
                sysmeta = urllib_parse.quote_plus(json.dumps(meta))
                url = '%s?action=play&type=yt&title=%s&tmdb=%s&meta=%s&t=%s&fileurl=%s' % (sysaddon, systitle, video_id, sysmeta, self.systime, i['video_id'])
                sysurl = urllib_parse.quote_plus(url)
                path = '%s?action=play&type=yt&title=%s&tmdb=%s' % (sysaddon, systitle, video_id)
                cm = []
                #cm.append(('Find Similar', 'Container.Update(%s?action=movies&url=%s)' % (sysaddon, self.related_link % imdb)))
                #cm.append(('Queue Item', 'RunPlugin(%s?action=queue_item)' % sysaddon))
                #cm.append(('Add to Library', 'RunPlugin(%s?action=movie_to_library&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s)' % (sysaddon, sysname, systitle, year, imdb, tmdb)))
                
                if action == 'movieFavorites':
                    cm.append(('Remove from MyFavorites', 'RunPlugin(%s?action=deleteFavorite&meta=%s&content=movie)' % (sysaddon, sysmeta)))
                else:
                    if not video_id in favitems:
                        cm.append(('Add to MyFavorites', 'RunPlugin(%s?action=addFavorite&meta=%s&content=movie)' % (sysaddon, sysmeta)))
                    else:
                        cm.append(('Remove from MyFavorites', 'RunPlugin(%s?action=deleteFavorite&meta=%s&content=movie)' % (sysaddon, sysmeta)))

                if kodi_version < 17:
                    cm.append(('Information', 'Action(Info)'))

                try:
                    item = control.item(label=label, offscreen=True)
                except:
                    item = control.item(label=label)
                
                meta.update({'plot': descr})
                
                #if (genres != ''):
                #    meta.update({'genre': genres})

                art = {}
                art.update({'icon': poster, 'thumb': poster, 'poster': poster})
                fanart = i['backdrop_path']
                art.update({'banner': poster})
                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setProperty('IsPlayable', 'true')
                offset = bookmarks.get('yt', video_id, '0', '0')
                if float(offset) > 120:
                    percentPlayed = int(float(offset) / float(meta['duration']) * 100)
                    item.setProperty('resumetime', str(offset))
                    item.setProperty('percentplayed', str(percentPlayed))
                
                if kodi_version >= 20:
                    info_tag = ListItemInfoTag(item, 'video')

                if kodi_version >= 20:
                    info_tag.set_info(control.metadataClean(meta))
                else:
                    try:
                        item.setInfo(type='Video', infoLabels=control.metadataClean(meta))
                    except:
                        pass

                video_streaminfo = {'codec': 'h264'}
        
                if kodi_version >= 20:
                    info_tag.add_stream_info('video', video_streaminfo)
                else:
                    item.addStreamInfo('video', video_streaminfo)
                
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            except:
                #log_utils.log('movieDirectory', 1)
                pass
        try:
            has_next = items[0]['has_next']
            if not has_next:
                raise Exception()
            icon = control.addonNext()
            url = items[0]['next']
            try:
                item = control.item(label=nextMenu, offscreen=True)
            except:
                item = control.item(label=nextMenu)
            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon, 'fanart': icon})
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass
        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)
        control.sleep(1000)
        views.setView('movies', {'skin.aeon.nox.silvo' : 50, 'skin.estuary': 55, 'skin.confluence': 500}) #View 50 List #View 501 LowList


    def addDirectory(self, items, queue=False):
        if items == None or len(items) == 0:
            control.idle()
            #sys.exit()
        sysaddon = sys.argv[0]
        syshandle = int(sys.argv[1])
        addonFanart = control.addonFanart()
        addonThumb = control.addonThumb()
        artPath = control.artPath()
        for i in items:
            try:
                name = i['name']
                if i['image'].startswith('http'):
                    thumb = i['image']
                elif not artPath == None:
                    thumb = os.path.join(artPath, i['image'])
                else:
                    thumb = addonThumb
                url = '%s?action=%s' % (sysaddon, action)
                try:
                    url += '&url=%s' % urllib_parse.quote_plus(i['url'])
                except:
                    pass

                if 'pid' in i:
                    url += '&pid=%s' % str(i['pid'])

                if 'year' in i:
                    url += '&year=%s' % urllib_parse.quote_plus(i['year'])

                if 'genre' in i:
                    url += '&genre=%s' % urllib_parse.quote_plus(i['genre'])

                xbmc.log('Action genre: ' + url, xbmc.LOGINFO)

                cm = []
                cm.append(('Clean Tools Widget', 'RunPlugin(%s?action=cleantools_widget)' % sysaddon))
                if queue == True:
                    cm.append(('Queue Item', 'RunPlugin(%s?action=queue_item)' % sysaddon))
                try:
                    item = control.item(label=name, offscreen=True)
                except:
                    item = control.item(label=name)
                poster = i['poster'] if 'poster' in i and not (i['poster'] == '0' or i['poster'] == None) else thumb
                fanart = i['fanart'] if 'fanart' in i and not (i['fanart'] == '0' or i['fanart'] == None) else addonFanart
                item.setArt({'icon': thumb, 'thumb': poster, 'fanart': fanart})
                item.addContextMenuItems(cm)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                #log_utils.log('addDirectory', 1)
                pass
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)


