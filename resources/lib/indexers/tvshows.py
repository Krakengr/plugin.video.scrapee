# -*- coding: utf-8 -*-

import re
import os
import sys
import datetime
import urllib
import simplejson as json
import six
from six.moves import range, urllib_parse, zip, urllib_request
from kodi_six import xbmc, xbmcplugin, xbmcgui

#from urllib.parse import quote, quote_plus, parse_qsl, urlparse, urlsplit, urlencode
try:
    #from infotagger.listitem import ListItemInfoTag
    from resources.lib.modules.listitem import ListItemInfoTag
except:
    pass

urlopen = urllib_request.urlopen

from resources.lib.indexers import navigator

from resources.lib.modules import bookmarks
from resources.lib.modules import cache
from resources.lib.modules import client_utils
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import history
from resources.lib.modules import favorites
from resources.lib.modules import playcount
from resources.lib.modules import views

#from resources.lib.modules import log_utils

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

params      = dict(urllib_parse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()
action      = 'tv'
sysaddon    = sys.argv[0]
year        = params.get('year')
netw        = params.get('netw')
genre       = params.get('genre')
geturl      = params.get('url')
page        = params.get('page')
pid         = params.get('pid')

control.moderator()
kodi_version = control.getKodiVersion()

class tvshows:
    def __init__(self):
        self.list = []
        self.datetime = datetime.datetime.utcnow()
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.year_date = (self.datetime - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        self.month_date = (self.datetime - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.addon_caching = control.setting('addon.caching') or 'true'
        self.shownoyear = control.setting('show.noyear') or 'false'
        self.unairedcolor = control.setting('unaired.color')
        if self.unairedcolor == '':
            self.unairedcolor = 'darkred'
        self.lang = 'en' if control.setting('info.language') == 'English' else 'el'
        self.items_per_page = str(control.setting('items.per.page')) or '20'
        self.curr_page = page if page is not None else 1
        self.curr_url = '%s?action=tv&url=%s' % (sysaddon, geturl)
        self.related_url = '%s?action=tv&url=related&imdb=%s' % (sysaddon, 0)

        if not year is None:
            self.curr_url += '&year=%s' % (year)
        
        if not genre is None:
            self.curr_url += '&genre=%s' % (genre)
        
        if not netw is None:
            self.curr_url += '&netw=%s' % (netw)

        self.curr_url += '&page=%s' % (self.curr_page)

        self.settingFanart = control.setting('fanart') or 'false'
        self.hq_artwork = control.setting('hq.artwork') or 'false'
        self.main_link = 'https://streamdb.homebrewgr.info/index.php?type=tv&lang=' + self.lang + '&items=' + self.items_per_page
        self.info_link = 'https://streamdb.homebrewgr.info/index.php?action=get-tv-show&id=%s'
        self.info_art_source = control.setting('info.art.source') or '0'
        self.original_artwork = control.setting('original.artwork') or 'false'

        self.popular_link = self.main_link + '&action=popular-tv-shows&page=' + str(self.curr_page)
        self.most_voted_link = self.main_link + '&action=most-voted-tv-shows&page=' + str(self.curr_page)
        self.highly_rating_link = self.main_link + '&action=highly-rating-tv-shows&page=' + str(self.curr_page)
        self.latest_link = self.main_link + '&action=latest-tv-shows&page=' + str(self.curr_page)
        self.years_link = self.main_link + '&action=tv-years'
        self.genres_link = self.main_link + '&action=tv-genres'
        self.networks_link = self.main_link + '&action=tv-networks'
        self.related_link = self.main_link + '&action=related-tv-shows&id=%s'
        self.by_year_link = self.main_link + '&action=get-tv-shows&year=%s&page=' + str(self.curr_page)
        self.by_genre_link = self.main_link + '&action=get-tv-shows&cat=%s&page=' + str(self.curr_page)
        self.by_netw_link = self.main_link + '&action=get-tv-shows&netw=%s&page=' + str(self.curr_page)
        self.search_link = self.main_link + '&action=search&title=%s&page=' + str(self.curr_page)
        self.search_people_link = self.main_link + '&action=search&people=%s&page=' + str(self.curr_page)
        self.search_person_link = self.main_link + '&action=get-tv-shows&pid=%s&page=' + str(self.curr_page)

    def get(self, url):
        if url == None:
            pass
        elif url == 'most_popular':
            self.getPopular()
            self.tvshowDirectory(self.list)
            return self.list
        elif url == 'latest_tv_shows':
            self.getLatest()
            self.tvshowDirectory(self.list)
            return self.list
        elif url == 'highly_rating':
            self.getByRating()
            self.tvshowDirectory(self.list)
            return self.list
        elif url == 'most_voted':
            self.getByVotes()
            self.tvshowDirectory(self.list)
            return self.list
        elif url == 'tv_years':
            self.getByYears()
            return self.list
        elif url == 'tv_genres':
            self.getByGenres()
            return self.list
        elif url == 'tv_by_person':
            self.getByPerson()
            self.tvshowDirectory(self.list)
        elif url == 'tv_networks':
            self.getByNetworks()
            return self.list
        elif url == 'tv_shows_by_network':
            self.getByNetwork()
            self.tvshowDirectory(self.list)
            return self.list
        elif url == 'tv_shows_by_year':
            self.getByYear()
            self.tvshowDirectory(self.list)
            return self.list
        elif url == 'tv_shows_by_genre':
            self.getByGenre()
            self.tvshowDirectory(self.list)
            return self.list
        elif url == 'favorites':
            self.favorites()
            return self.list
        elif url == 'history':
            self.history()
            return self.list
    
    def history(self):
        try:
            items = history.getHistory('tv')
            
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
                if not 'description' in i:
                    i['description'] = i['name']
                if not 'backdrop_path' in i:
                    i['backdrop_path'] = i['poster']
                if not 'banner' in i:
                    i['banner'] = i['poster']
                if not 'fanart' in i:
                    i['fanart'] = i['poster']
                if not 'originaltitle' in i:
                    i['originaltitle'] = i['name']

            self.list = sorted(self.list, key=lambda k: k['title'])
            
            self.tvshowDirectory(self.list)
        except:
            #log_utils.log('favorites', 1)
            return
        
    def favorites(self):
        try:
            items = favorites.getFavorites('tvshow')
            
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
                if not 'description' in i:
                    i['description'] = i['name']
                if not 'backdrop_path' in i:
                    i['backdrop_path'] = i['poster']
                if not 'banner' in i:
                    i['banner'] = i['poster']
                if not 'fanart' in i:
                    i['fanart'] = i['poster']
                if not 'originaltitle' in i:
                    i['originaltitle'] = i['name']

            self.list = sorted(self.list, key=lambda k: k['title'])
            
            self.tvshowDirectory(self.list)
        except:
            #log_utils.log('favorites', 1)
            return
    
    def search_term_menu(self, select):
        navigator.navigator().addDirectoryItem('New Search...', 'tv_searchterm&select=%s' % select, 'search.png', 'DefaultMovies.png')
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
            navigator.navigator().addDirectoryItem(term.title(), 'tv_searchterm&select=%s&name=%s' % (select, term), 'search.png', 'DefaultMovies.png')
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
        
        if select == 'shows':
            url = self.search_link % urllib_parse.quote_plus(q)
            self.getBySearch(url)
            self.tvshowDirectory(self.list)
        elif select == 'people':
            url = self.search_people_link % urllib_parse.quote_plus(q)
            self.search_persons(url)
        elif select == 'networks':
            url = self.search_people_link % urllib_parse.quote_plus(q)
            self.search_persons(url)

    def search_persons(self, url):
        self.list = self.search_person_list(url)
        for i in range(0, len(self.list)):
            self.list[i].update({'action': 'movies'})
        self.addDirectory(self.list)
        return self.list
    
    def search_person_list(self, url):
        try:
            result = client.scrapePage(url, timeout='30').text
            data_json = json.loads(result)
            if 'status' not in data_json or data_json["status"] != "OK" or 'data' not in data_json:
                raise Exception()
            for item in data_json["data"]["data"]:
                self.list.append({'name': item["name"], 'url': 'tv_by_person', 'pid': item["id"], 'image': item["image_path"]})
        except:
            #log_utils.log('imdb_person_list', 1)
            pass
        return self.list
    
    def getByNetwork(self):
        try:
            url         = self.by_netw_link % (netw)
            name        = 'tv_by_netw-' + str(netw) + '_lang-' + self.lang + '_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)

            if data_json["status"] != "OK":
                raise Exception()

            self.buildMovieArr(data_json)
            
        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass
        
        return self.list
    
    def getByYear(self):
        try:
            url         = self.by_year_link % (year)
            name        = 'tv_by_year-' + str(year) + '_lang-' + self.lang + '_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            self.buildMovieArr(data_json)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass
        
        return self.list
    
    def getByGenre(self):
        try:
            url         = self.by_genre_link % (genre)
            name        = 'tv_by_genre-' + str(genre) + '_lang-' + self.lang + '_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            self.buildMovieArr(data_json)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def getByNetworks(self):
        try:
            url         = self.networks_link
            name        = 'tv_networks'
            data_json   = cache.get_cache_file(str(name), url)
            
            if data_json["status"] != "OK":
                raise Exception()
                
            items = data_json['data']

            for item in items:
                id = str(item['id'])
                name  = str(item['name'])

                if 'items' in item:
                    name  += ' [COLOR red][' + str(item['items']) + ' items][/COLOR]'
                
                self.list.append({'name': name, 'url': 'tv_shows_by_network', 'netw': id, 'image': 'genres.png', 'action': action})

            self.addDirectory(self.list)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list

    def getByGenres(self):
        try:
            url         = self.genres_link
            name        = 'tv_genres'
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            items = data_json['data']

            for item in items:
                #label = '%s (%s)' % (item['name'], item['items'])
                #num = item['items']
                id = str(item['id'])
                name  = str(item['name'])

                if 'items' in item:
                    name  += ' [COLOR red][' + str(item['items']) + ' items][/COLOR]'
               
                self.list.append({'name': name, 'url': 'tv_shows_by_genre', 'genre': id, 'image': 'genres.png', 'action': action})

            self.addDirectory(self.list)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list

    def getByYears(self):
        try:
            url         = self.years_link
            name        = 'tv_years'
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            items = data_json['data']

            for item in items:

                year = str(item['name'])

                #if 'items' in item:
                    #year  += ' [COLOR red][' + str(item['items']) + ' items][/COLOR]'
               
                self.list.append({'name': year, 'url': 'tv_shows_by_year', 'year': year, 'image': 'years.png', 'action': action})

            self.addDirectory(self.list)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def getByVotes(self):
        try:
            url         = self.most_voted_link
            name        = 'tv_by_votes_lang-' + self.lang + '_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            self.buildMovieArr(data_json)
        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass
        return self.list
    
    def getByRating(self):
        try:
            url         = self.highly_rating_link
            name        = 'tv_by_rates_lang-' + self.lang + '_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            self.buildMovieArr(data_json)
        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass
        return self.list
    
    def getLatest(self):
        try:
            url         = self.latest_link
            name        = 'latest_tv_lang-' + self.lang + '_page-' + str(self.curr_page)
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
            name        = 'popular_tv_lang-' + self.lang + '_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            self.buildMovieArr(data_json)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def getBySearch(self, url):
        try:
            response    = urlopen(url)
            data_json   = json.loads(response.read())
            
            if data_json["status"] != "OK":
                raise Exception()
            self.buildMovieArr(data_json["data"])

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def getByPerson(self):
        
        try:
            url         = self.search_person_link % (pid)

            response    = urlopen(url) 
            data_json   = json.loads(response.read())
            if data_json["status"] != "OK":
                raise Exception()
            
            self.buildMovieArr(data_json)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def buildMovieArr(self, data):
        if data['data'] == None or len(data['data']) == 0:
            control.idle()

        items           = data['data']
        total_pages     = int(data["total_pages"])
        curr_page       = int(data["page"])
        has_next        = True if total_pages > curr_page else False
        has_prev        = True if curr_page > 2 else False
        prev            = self.curr_url + 'page=%s' % (str(1)) if (curr_page == 1) else self.curr_url + 'page=%s' % (str(curr_page - 1))
        next            = '%s&page=%s' % (self.curr_url.split('&page=', 1)[0], str(curr_page + 1))
        
        for item in items:
            title = item['title']
            title = client_utils.replaceHTMLCodes(title)
            originaltitle = item['original_title']
            originaltitle = client_utils.replaceHTMLCodes(originaltitle)
            description = item['description']
            description = client_utils.replaceHTMLCodes(description)
            
            if not originaltitle:
                originaltitle = title
            
            id              = item['id']
            year            = item['year']
            cast            = item['cast']
            genres          = item['genres']
            status          = item['status']
            imdb            = item['imdb_id']
            runtime         = item['runtime']
            tmdb            = item['themoviedb_id']
            poster_path     = item['poster_path']
            backdrop_path   = item['backdrop_path']
            
            self.list.append({'id': id, 'title': title, 'originaltitle': originaltitle, 'description': description, 'backdrop_path': backdrop_path, 'poster_path': poster_path, 'year': year, 'duration': runtime, 'cast': cast, 'genres': genres, 'status': status, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'prev': prev, 'next': next, 'has_next': has_next, 'has_prev': has_prev})

    def tvshowDirectory(self, items):
        if items == None or len(items) == 0:
            control.idle()

        sysaddon = sys.argv[0]
        syshandle = int(sys.argv[1])
        indicators = playcount.getMovieIndicators()
        playbackMenu = 'Auto Play'
        isPlayable  = False
        nextMenu = '[I]Next Page[/I]'
        watchedMenu = 'Mark as Watched'
        unwatchedMenu = 'Mark as Unwatched'
        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()
        addonFanart = control.addonFanart()
        flatten = control.setting('flatten.tvshows') or 'false'
        
        #cm - menus
        findSimilar = 'Find Similar'
        playRandom = 'Random'
        queueMenu = 'Queue Item'
        addToLibrary = 'Add to MyFavorites'
        infoMenu = 'Info'
        try:
            favitems = favorites.getFavorites('tvshow')
            favitems = [i[0] for i in favitems]
        except:
            pass
        
        for i in items:
            try:
                if 'channel' in i:
                    label = '%s (%s) (%s)' % (i['title'], i['year'], i['channel'])
                else:
                    if (geturl != 'tv_shows_by_year'):
                        label = '%s (%s)' % (i['title'], i['year'])
                    else:
                        label = '%s' % (i['title'])

                imdb, tmdb, title, year = i['imdb'], i['tmdb'], i['originaltitle'], i['year']
                
                try:
                    premiered = i['year']
                    if premiered == '0' or (int(re.sub('[^0-9]', '', premiered)) > int(re.sub('[^0-9]', '', str(self.today_date)))):
                        label = '[COLOR %s][I]%s[/I][/COLOR]' % (self.unairedcolor, label)
                except:
                    pass
                
                descr = i['description']
                sysname = urllib_parse.quote_plus('%s (%s)' % (title, year))
                systitle = urllib_parse.quote_plus(title)
                poster = i['poster_path']
                seasons_meta = {'year': year, 'title': title, 'poster': poster, 'fanart': poster, 'descr': descr, 'banner': poster, 'clearlogo': poster, 'clearart': poster, 'landscape': 'landscape', 'mediatype': 'tv', 'code': tmdb, 'imdbnumber': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': 0, 'tvshowtitle': i['title']}
                
                sysmeta = urllib_parse.quote_plus(json.dumps(seasons_meta))
                
                meta = dict((k,v) for k, v in i.items() if not v == '0')
                meta.update({'code': tmdb, 'imdbnumber': imdb, 'imdb_id': imdb, 'tmdb_id': tmdb, 'tvdb_id': 0})
                meta.update({'mediatype': 'tvshow'})
                meta.update({'tvshowtitle': i['title']})
                
                trailer_url = urllib_parse.quote(i['trailer']) if 'trailer' in i else '0'
                search_name = systitle
                
                if trailer_url == '0':
                    meta.update({'trailer': '%s?action=trailer&name=%s&imdb=%s&tmdb=%s' % (sysaddon, search_name, imdb, tmdb)})
                else:
                    meta.update({'trailer': '%s?action=trailer&name=%s&url=%s&imdb=%s&tmdb=%s' % (sysaddon, search_name, trailer_url, imdb, tmdb)})
                
                if not 'duration' in meta: meta.update({'duration': '45'})
                elif meta['duration'] == '0': meta.update({'duration': '45'})
                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                genres = i['genres'] if 'genres' in i else ''
                
                if 'castwiththumb' in i and not i['castwiththumb'] == '0': meta.pop('cast', '0')
                
                try:
                    overlay = int(playcount.getTVShowOverlay(indicators, tmdb))
                    if overlay == 7: meta.update({'playcount': 1, 'overlay': 7})
                    else: meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass

                meta.update({'poster': i['poster_path']})
                meta.update({'plot': descr})
                cm = []
                
                #cm.append((findSimilar, 'Container.Update(%s?action=tvshows&url=%s)' % (sysaddon, urllib.parse.quote_plus(self.related_link % tmdb))))
                
                #cm.append((playRandom, 'RunPlugin(%s?action=random&rtype=season&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s)' % (
                #            sysaddon, urllib.parse.quote_plus(systitle), urllib.parse.quote_plus(year), urllib.parse.quote_plus(imdb), urllib.parse.#quote_plus(tmdb)))
                #            )
                
                #cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

                cm.append((watchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tmdb=%s&query=7)' % (sysaddon, systitle, imdb, tmdb)))

                #cm.append((unwatchedMenu, 'RunPlugin(%s?action=tvPlaycount&name=%s&imdb=%s&tmdb=%s&query=6)' % (sysaddon, systitle, imdb, tmdb)))

                #cm.append((addToLibrary, 'RunPlugin(%s?action=tvshowToLibrary&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s)' % (sysaddon, systitle, year, imdb, tmdb)))
                
                if action == 'movieFavorites':
                    cm.append(('Remove from MyFavorites', 'RunPlugin(%s?action=deleteFavorite&meta=%s&content=tvshow)' % (sysaddon, sysmeta)))
                else:
                    if not imdb in favitems:
                        cm.append(('Add to MyFavorites', 'RunPlugin(%s?action=addFavorite&meta=%s&content=tvshow)' % (sysaddon, sysmeta)))
                    else:
                        cm.append(('Remove from MyFavorites', 'RunPlugin(%s?action=deleteFavorite&meta=%s&content=tvshow)' % (sysaddon, sysmeta)))
                
                try: item = control.item(label=label, offscreen=True)
                except: item = control.item(label=label)
                
                art = {}

                art.update({'icon': poster, 'thumb': poster, 'poster': poster, 'tvshow.poster': poster, 'season.poster': poster, 'banner': poster, 'landscape': poster})
                
                art.update({'fanart': poster})
                
                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})
                
                castwiththumb = False
                if castwiththumb and not castwiththumb == '0':
                   item.setCast(castwiththumb)
                
                item.setProperty('imdb_id', imdb)
                item.setProperty('tmdb_id', str(tmdb))
                
                if kodi_version < 20:
                    try: 
                        item.setUniqueIDs({'imdb': imdb, 'tmdb': str(tmdb)})
                    except:
                        pass
                
                item.setArt(art)
                item.addContextMenuItems(cm)

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
                
                if flatten == 'true':
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&fanart=%s&duration=%s&meta=%s' % (sysaddon, systitle, year, imdb, tmdb, poster, i['duration'], sysmeta)
                else:
                    url = '%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&meta=%s' % (sysaddon, systitle, year, imdb, tmdb, sysmeta)
                
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                #log_utils.log('tvshowDirectory', 1)
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
        control.content(syshandle, 'tvshows')
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

                if 'year' in i:
                    url += '&year=%s' % urllib_parse.quote_plus(i['year'])

                if 'genre' in i:
                    url += '&genre=%s' % urllib_parse.quote_plus(i['genre'])

                if 'netw' in i:
                    url += '&netw=%s' % urllib_parse.quote_plus(i['netw'])
                
                if 'pid' in i:
                    url += '&pid=%s' % str(i['pid'])

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


