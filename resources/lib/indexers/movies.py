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
from resources.lib.modules import likes
from resources.lib.modules import playcount
from resources.lib.modules import views

#from resources.lib.modules import log_utils

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

params      = dict(urllib_parse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()
action      = 'movies'
sysaddon    = sys.argv[0]
year        = params.get('year')
genre       = params.get('genre')
geturl      = params.get('url')
page        = params.get('page')
pid         = params.get('pid')

control.moderator()
kodi_version = control.getKodiVersion()

class movies:
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
        self.curr_url = '%s?action=movies&url=%s' % (sysaddon, geturl)
        self.related_url = '%s?action=movies&url=related&imdb=%s' % (sysaddon, 0)

        if not year is None:
            self.curr_url += '&year=%s' % (year)
        
        if not genre is None:
            self.curr_url += '&genre=%s' % (genre)

        self.curr_url += '&page=%s' % (self.curr_page)

        self.main_link = 'https://streamdb.homebrewgr.info/index.php?type=movie&lang=' + self.lang + '&items=' + self.items_per_page
        self.info_link = 'https://streamdb.homebrewgr.info/index.php?action=get_movie&id=%s'
        
        self.popular_link = self.main_link + '&action=popular-movies&page=' + str(self.curr_page)
        self.most_voted_link = self.main_link + '&action=most-voted-movies&page=' + str(self.curr_page)
        self.highly_rating_link = self.main_link + '&action=highly-rating-movies&page=' + str(self.curr_page)
        self.latest_link = self.main_link + '&action=latest-movies&page=' + str(self.curr_page)
        self.years_link = self.main_link + '&action=movie-years'
        self.genres_link = self.main_link + '&action=movie-genres'
        self.related_link = self.main_link + '&action=related-movies&id=%s'
        self.by_year_link = self.main_link + '&action=get-movies&year=%s&page=' + str(self.curr_page)
        self.by_genre_link = self.main_link + '&action=get-movies&cat=%s&page=' + str(self.curr_page)
        self.search_link = self.main_link + '&action=search&title=%s&page=' + str(self.curr_page)
        self.search_people_link = self.main_link + '&action=search&people=%s&page=' + str(self.curr_page)
        self.search_person_link = self.main_link + '&action=get-movies&pid=%s&page=' + str(self.curr_page)

    def get(self, url):
        if url == None:
            pass
        elif url == 'most_popular':
            self.getPopular()
            self.movieDirectory(self.list)
            return self.list
        elif url == 'latest_movies':
            self.getLatest()
            self.movieDirectory(self.list)
            return self.list
        elif url == 'highly_rating':
            self.getByRating()
            self.movieDirectory(self.list)
            return self.list
        elif url == 'most_voted':
            self.getByVotes()
            self.movieDirectory(self.list)
            return self.list
        elif url == 'movies_years':
            self.getByYears()
            return self.list
        elif url == 'movies_genres':
            self.getByGenres()
            return self.list
        elif url == 'movies_by_year':
            self.getByYear()
            self.movieDirectory(self.list)
        elif url == 'movies_by_person':
            self.getByPerson()
            self.movieDirectory(self.list)
            return self.list
        elif url == 'movies_by_genre':
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
        navigator.navigator().addDirectoryItem('New Search...', 'movies_searchterm&select=%s' % select, 'search.png', 'DefaultMovies.png')
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
            navigator.navigator().addDirectoryItem(term.title(), 'movies_searchterm&select=%s&name=%s' % (select, term), 'search.png', 'DefaultMovies.png')
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
        if select == 'movies':
            url = self.search_link % urllib_parse.quote_plus(q)
            self.getBySearch(url)
            self.movieDirectory(self.list)
        elif select == 'people':
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
                self.list.append({'name': item["name"], 'url': 'movies_by_person', 'pid': item["id"], 'image': item["image_path"]})
        except:
            #log_utils.log('imdb_person_list', 1)
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
    
    def getBySearch(self, url):
        try:
            response    = urlopen(url) 
            data_json   = json.loads(response.read())
            
            if data_json["status"] != "OK":
                raise Exception()
            
            self.buildMovieArr(data_json["data"], True)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def history(self):
        try:
            items = history.getHistory('movie')
            items = [(i[0].encode('utf-8'), eval(i[1].encode('utf-8'))) for i in items]
            self.list = [i[1] for i in items]
            xbmc.log('self.list: ' + str(self.list), xbmc.LOGINFO)
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
    
    def getByYear(self):
        try:
            url         = self.by_year_link % (year)
            name        = 'movies_by_year-' + str(year) + '_page-' + str(self.curr_page)
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
            name        = 'movies_by_genre-' + str(genre) + '_page-' + str(self.curr_page)
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            self.buildMovieArr(data_json)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def getByGenres(self):
        try:
            url         = self.genres_link
            name        = 'movies_genres'
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            items = data_json['data']

            for item in items:
                #label = '%s (%s)' % (item['name'], item['items'])
                #num = item['items']
                id = str(item['id'])
                name  = str(item['name'])
               
                self.list.append({'name': name, 'url': 'movies_by_genre', 'genre': id, 'image': 'genres.png', 'action': 'movies'})

            self.addDirectory(self.list)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list

    def getByYears(self):
        try:
            url         = self.years_link
            name        = 'movies_years'
            data_json   = cache.get_cache_file(str(name), url)
                
            if data_json["status"] != "OK":
                raise Exception()
                
            items = data_json['data']

            for item in items:
                #label = '%s (%s)' % (item['name'], item['items'])
                #num = item['items']
                year = str(item['name'])
               
                self.list.append({'name': year, 'url': 'movies_by_year', 'year': year, 'image': 'years.png', 'action': 'movies'})

            self.addDirectory(self.list)

        except:
            control.dialog.ok('Error', 'Error getting data. Please try again later.')
            pass

        return self.list
    
    def getByVotes(self):
        try:
            url         = self.most_voted_link
            name        = 'movies_by_votes_page-' + str(self.curr_page)
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
            name        = 'movies_by_rates_page-' + str(self.curr_page)
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
            name        = 'latest_movies_page-' + str(self.curr_page)
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
            name        = 'popular_movies_page-' + str(self.curr_page)
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

        # if geturl == 'movies_by_year':
        #    next += '&year=%s' % (str(year))
        
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
            
            self.list.append({'id': id, 'title': title, 'originaltitle': originaltitle, 'description': description, 'backdrop_path': backdrop_path, 'poster_path': poster_path, 'year': year, 'runtime': runtime, 'cast': cast, 'genres': genres, 'status': status, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'prev': prev, 'next': next_page, 'has_next': has_next, 'has_prev': has_prev})

    def movieDirectory(self, items):
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
       
        try:
            favitems = favorites.getFavorites('movie')
            favitems = [i[0] for i in favitems]
        except:
            pass

        try:
            likeitems = likes.getLikes('movie')
            likeitems = [i[0] for i in likeitems]
        except:
            pass
        
        for i in items:
            try:
                if 'channel' in i:
                    label = '%s (%s) (%s)' % (i['title'], i['year'], i['channel'])
                else:
                    if (geturl != 'movies_by_year'):
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
                
                sysname = urllib_parse.quote_plus('%s (%s)' % (title, year))
                systitle = urllib_parse.quote_plus(title)
                meta = dict((k,v) for k, v in six.iteritems(i) if not v == '0')
                meta.update({'mediatype': 'movie'})
                meta.update({'code': tmdb, 'imdbnumber': imdb, 'imdb_id': imdb, 'tmdb_id': tmdb})
                meta.update({'trailer': '%s?action=trailer&name=%s&tmdb=%s&imdb=%s' % (sysaddon, systitle, tmdb, imdb)})
                
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
                url = '%s?action=play&type=movie&title=%s&year=%s&imdb=%s&tmdb=%s&meta=%s&t=%s' % (sysaddon, systitle, year, imdb, tmdb, sysmeta, self.systime)
                sysurl = urllib_parse.quote_plus(url)
                path = '%s?action=play&title=%s&year=%s&imdb=%s&tmdb=%s' % (sysaddon, systitle, year, imdb, tmdb)
                cm = []
                #cm.append(('Find Similar', 'Container.Update(%s?action=movies&url=%s)' % (sysaddon, self.related_link % imdb)))
                #cm.append(('Queue Item', 'RunPlugin(%s?action=queue_item)' % sysaddon))
                #cm.append(('Add to Library', 'RunPlugin(%s?action=movie_to_library&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s)' % (sysaddon, sysname, systitle, year, imdb, tmdb)))
                
                if action == 'movieFavorites':
                    cm.append(('Remove from MyFavorites', 'RunPlugin(%s?action=deleteFavorite&meta=%s&content=movie)' % (sysaddon, sysmeta)))
                else:
                    if not imdb in favitems:
                        cm.append(('Add to MyFavorites', 'RunPlugin(%s?action=addFavorite&meta=%s&content=movie)' % (sysaddon, sysmeta)))
                    else:
                        cm.append(('Remove from MyFavorites', 'RunPlugin(%s?action=deleteFavorite&meta=%s&content=movie)' % (sysaddon, sysmeta)))

                if action == 'movieLikes':
                    cm.append(('Remove My Like', 'RunPlugin(%s?action=deleteLike&meta=%s&content=movie)' % (sysaddon, sysmeta)))
                else:
                    if not imdb in likeitems:
                        cm.append(('Like this Movie', 'RunPlugin(%s?action=addlike&meta=%s&content=movie)' % (sysaddon, sysmeta)))
                    else:
                        cm.append(('Unlike this Movie', 'RunPlugin(%s?action=deletelike&meta=%s&content=movie)' % (sysaddon, sysmeta)))

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
                offset = bookmarks.get('movie', imdb, '0', '0')
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
                url = '%s?action=%s' % (sysaddon, i['action'])
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


