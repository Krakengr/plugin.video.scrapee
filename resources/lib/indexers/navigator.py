# -*- coding: utf-8 -*-

import os
import sys

from resources.lib.modules import control
from resources.lib.modules import log_utils
from kodi_six import xbmc

try:
    from resources.lib.modules.listitem import ListItemInfoTag
except:
    pass

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
control.moderator()
streamdbApi = control.setting('streamdb.api')
lang = 'en' if control.setting('info.language') == 'English' else 'el'
kodi_version = control.getKodiVersion()

class navigator:
    def root(self):
        self.addDirectoryItem('Movies', 'movies_menu', 'movies.png', 'DefaultMovies.png')
        self.addDirectoryItem('TV Shows', 'tvshows_menu', 'tvshows.png', 'DefaultTVShows.png')

        if lang == 'el':
            self.addDirectoryItem('YouTube Playlists', 'ytube_menu', 'tvshows.png', 'DefaultVideo.png')

        self.addDirectoryItem('Tools', 'tools_menu', 'tools.png', 'DefaultAddonProgram.png')
        self.endDirectory(cached=False)
    
    #Movies menu from Root
    def moviesMenu(self):
        self.addDirectoryItem('Most Popular', 'movies&url=most_popular', 'most-popular.png', 'DefaultMovies.png')
        self.addDirectoryItem('Latest Movies', 'movies&url=latest_movies', 'latest-movies.png', 'DefaultMovies.png')
        self.addDirectoryItem('Highly Rated', 'movies&url=highly_rating', 'highly-rated.png', 'DefaultMovies.png')
        self.addDirectoryItem('Most Voted', 'movies&url=most_voted', 'most-voted.png', 'DefaultMovies.png')
        self.addDirectoryItem('Years', 'movies&url=movies_years', 'years.png', 'DefaultMovies.png')
        self.addDirectoryItem('Genres', 'movies&url=movies_genres', 'genres.png', 'DefaultMovies.png')
        self.addDirectoryItem('My Favorite Movies', 'movies&url=favorites', 'userlists.png', 'DefaultTVShows.png')
        
        if streamdbApi != '' and len(streamdbApi) > 0:
            self.addDirectoryItem('History', 'movies&url=history', 'userlists.png', 'DefaultTVShows.png')

        self.addDirectoryItem('Search for Movies', 'search_movies_menu', 'search.png', 'DefaultFolder.png')
        self.endDirectory()
    
    #tvshows menu from Root
    def tvshows(self):
        self.addDirectoryItem('Most Popular', 'tv&url=most_popular', 'most-voted.png', 'DefaultTVShows.png')
        self.addDirectoryItem('Latest TV Shows', 'tv&url=latest_tv_shows', 'new-tvshows.png', 'DefaultTVShows.png')
        self.addDirectoryItem('Highly Rated', 'tv&url=highly_rating', 'highly-rated.png', 'DefaultMovies.png')
        self.addDirectoryItem('Most Voted', 'tv&url=most_voted', 'most-voted.png', 'DefaultMovies.png')
        self.addDirectoryItem('Networks', 'tv&url=tv_networks', 'genres.png', 'DefaultMovies.png')
        self.addDirectoryItem('Years', 'tv&url=tv_years', 'years.png', 'DefaultMovies.png')
        self.addDirectoryItem('Genres', 'tv&url=tv_genres', 'genres.png', 'DefaultMovies.png')
        self.addDirectoryItem('My Favorite TV Shows', 'tv&url=favorites', 'userlists.png', 'DefaultTVShows.png')

        if streamdbApi != '' and len(streamdbApi) > 0:
            self.addDirectoryItem('History', 'tv&url=history', 'userlists.png', 'DefaultTVShows.png')

        self.addDirectoryItem('Search TV Shows', 'search_tvshows_menu', 'search.png', 'DefaultFolder.png')
        self.endDirectory()
    
    #YT menu from Root
    def ytMenu(self):
        self.addDirectoryItem('Most Popular', 'ytube&url=most_popular', 'most-popular.png', 'DefaultMovies.png')
        self.addDirectoryItem('Latest', 'ytube&url=latest', 'latest-movies.png', 'DefaultMovies.png')
        self.addDirectoryItem('Playlists', 'ytube&url=genres', 'genres.png', 'DefaultMovies.png')
        #self.addDirectoryItem('My Favorites', 'ytube&url=favorites', 'userlists.png', 'DefaultTVShows.png')
        self.addDirectoryItem('Search', 'search_yt_menu', 'search.png', 'DefaultFolder.png')
        self.endDirectory()

    def search_yt(self):
        self.addDirectoryItem('Titles Search', 'yt_search&select=yt', 'search.png', 'DefaultMovies.png')
        self.endDirectory()

    def search_movies(self):
        self.addDirectoryItem('Titles Search', 'movies_search&select=movies', 'search.png', 'DefaultMovies.png')
        self.addDirectoryItem('People Search', 'movies_search&select=people', 'people-search.png', 'DefaultMovies.png')
        self.endDirectory()

    def search_tvshows(self):
        self.addDirectoryItem('Titles Search', 'tv_search&select=shows', 'search.png', 'DefaultMovies.png')
        self.addDirectoryItem('People Search', 'tv_search&select=people', 'people-search.png', 'DefaultMovies.png')
        #self.addDirectoryItem('Networks Search', 'tv_search&select=networks', 'search.png', 'DefaultMovies.png')
        self.endDirectory()

    def tools(self):
        self.addDirectoryItem('Cleaning Tools', 'cleantools_menu', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('General Settings', 'open_settings&query=0.0', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        self.addDirectoryItem('View Change Log', 'view_changelog', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        self.addDirectoryItem('View Previous Change Logs', 'view_previous_changelogs', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        self.addDirectoryItem('Optional Installs', 'installs_menu', 'tools.png', 'DefaultAddonProgram.png')
        self.endDirectory()
        
    def cleantools(self):
        self.addDirectoryItem('Clear All Cache', 'clear_all_cache', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        self.addDirectoryItem('Clear Cache', 'clear_cache', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        self.addDirectoryItem('Clear All Search Cache', 'clear_search_cache&select=all', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        self.addDirectoryItem('Clean Settings',  'clean_settings',  'tools.png',  'DefaultAddonProgram.png', isFolder=False)
        self.addDirectoryItem('Clear History',  'clear_history',  'tools.png',  'DefaultAddonProgram.png', isFolder=False)
        self.addDirectoryItem('Clear Favorites',  'clear_favorites',  'tools.png',  'DefaultAddonProgram.png', isFolder=False)
        self.addDirectoryItem('Clear Likes',  'clear_likes',  'tools.png',  'DefaultAddonProgram.png', isFolder=False)
        self.endDirectory()

    def installsmenu(self):
        if not control.condVisibility('System.HasAddon(script.scrubsv2.artwork)'):
            self.addDirectoryItem('script.scrubsv2.artwork - Install Addon', 'installAddon&id=script.scrubsv2.artwork', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        else:
            self.addDirectoryItem('script.scrubsv2.artwork - Open Settings', 'open_settings&query=0.0', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        if not control.condVisibility('System.HasAddon(plugin.video.youtube)'):
            self.addDirectoryItem('plugin.video.youtube - Install Addon', 'installAddon&id=plugin.video.youtube', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        else:
            self.addDirectoryItem('plugin.video.youtube - Open Settings', 'open_settings&id=plugin.video.youtube', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
        
        self.endDirectory()

    def views(self):
        try:
            items = [('Movies', 'movies')]
            items += [('TV Shows', 'tvshows')]
            items += [('Seasons', 'seasons')]
            items += [('Episodes', 'episodes')]
            select = control.selectDialog([i[0] for i in items], 'Setup ViewTypes')
            if select == -1:
                return
            content = items[select][1]
            title = 'Click Here To Save View'
            url = '%s?action=add_view&content=%s' % (sysaddon, content)
            poster = control.addonPoster()
            banner = control.addonBanner()
            fanart = control.addonFanart()

            try:
                item = control.item(label=title, offscreen=True)
            except:
                item = control.item(label=title)
            ##New Ends
            item.setArt({'icon': poster, 'thumb': poster, 'poster': poster, 'banner': banner})
            item.setProperty('Fanart_Image', fanart)
            ##New Starts
            if kodi_version >= 20:
                info_tag = ListItemInfoTag(item, 'video')
                info_tag.set_info({'title': title})
            else:
                item.setInfo(type='Video', infoLabels={'title': title})
            ##New Ends
            #item.setInfo(type='Video', infoLabels={'title': title}) # Seems to be a useless line of code lol. (been commented out since before the kodi_v20 changes.)
            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            ## Added in to help those to disable the TopBar lol.
            self.addDirectoryItem('Force Open SideMenu/SlideMenu', 'open_sidemenu', 'tools.png', 'DefaultAddonProgram.png', isFolder=False)
            control.content(syshandle, content)
            control.directory(syshandle, cacheToDisc=True)
            from resources.lib.modules import views
            views.setView(content, {})
        except:
            return


    def clearCache(self):
        from resources.lib.modules import cache
        yes = control.yesnoDialog('Clear Cache?')
        if not yes:
            return
        cache.cache_clear()
        control.infoDialog('Cache Cleared.', sound=True, icon='INFO')

    def clearCacheProviders(self):
        from resources.lib.modules import cache
        yes = control.yesnoDialog('Clear Providers Cache?')
        if not yes:
            return
        cache.cache_clear_providers()
        control.infoDialog('Providers Cache Cleared.', sound=True, icon='INFO')


    def clearCacheSearch(self, select):
        from resources.lib.modules import cache
        yes = control.yesnoDialog('Clear All Search Cache?')
        if not yes:
            return
        cache.cache_clear_search(select)
        control.infoDialog('All Search Cache Cleared.', sound=True, icon='INFO')


    def clearCacheAll(self):
        from resources.lib.modules import cache
        yes = control.yesnoDialog('Clear All Cache?')
        if not yes:
            return
        cache.cache_clear_all()
        control.infoDialog('All Cache Cleared.', sound=True, icon='INFO')

    def cleanHistory(self):
        from resources.lib.modules import cache
        yes = control.yesnoDialog('Clean History?')
        if not yes:
            return
        cache.clean_history()
        control.infoDialog('History Cleaned.', sound=True, icon='INFO')
    
    def cleanFavorites(self):
        from resources.lib.modules import cache
        yes = control.yesnoDialog('Clean Favorites?')
        if not yes:
            return
        cache.clean_favorites()
        control.infoDialog('Favorites Cleaned.', sound=True, icon='INFO')

    def cleanLikes(self):
        from resources.lib.modules import cache
        yes = control.yesnoDialog('Clean Likes?')
        if not yes:
            return
        cache.clean_likes()
        control.infoDialog('Favorites Likes.', sound=True, icon='INFO')

    def cleanSettings(self):
        from resources.lib.modules import cache
        yes = control.yesnoDialog('Clean Old Settings?')
        if not yes:
            return
        cache.clean_settings()
        control.infoDialog('Old Settings Cleaned.', sound=True, icon='INFO')


    def clearDebugLog(self):
        yes = control.yesnoDialog('Clear Debug Log?')
        if not yes:
            return
        log_utils.empty_log()
        control.infoDialog('Debug Log Cleared.', sound=True, icon='INFO')


    def clearViewTypes(self):
        from resources.lib.modules import views
        yes = control.yesnoDialog('Clear All ViewTypes?')
        if not yes:
            return
        views.deleteView()
        control.infoDialog('All ViewTypes Cleared.', sound=True, icon='INFO')


    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True):
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        artPath = control.artPath()
        fanart = control.addonFanart()
        thumb = os.path.join(artPath, thumb) if not (artPath == None or thumb == None) else icon
        cm = []
        cm.append(('[B]View Change Log[/B]', 'RunPlugin(%s?action=view_changelog)' % sysaddon))
        cm.append(('[B]Clean Tools Widget[/B]', 'RunPlugin(%s?action=cleantools_widget)' % sysaddon))
        if queue == True:
            cm.append(('Queue Item', 'RunPlugin(%s?action=queue_item)' % sysaddon))
        if not context == None:
            cm.append((context[0], 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        try:
            item = control.item(label=name, offscreen=True)
        except:
            item = control.item(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'fanart': fanart})
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def addDirectory(self, items, queue=False, isFolder=True):
        if items == None or len(items) == 0:
            control.idle()
            #sys.exit()
        sysfanart = control.addonFanart()
        for i in items:
            try:
                url = '%s?action=%s&url=%s' % (sysaddon, i['action'], i['url'])
                title = i['title']
                icon = i['image'] if 'image' in i and not i['image'] == (None or 'None' or '0') else 'DefaultVideo.png'
                fanart = i['fanart'] if 'fanart' in i and not i['fanart'] == (None or 'None' or '0') else sysfanart
                try:
                    item = control.item(label=title, offscreen=True)
                except:
                    item = control.item(label=title)
                item.setProperty('IsPlayable', 'true')
                item.setArt({'icon': icon, 'thumb': icon, 'fanart': fanart})
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
            except Exception:
                #log_utils.log('addDirectory', 1)
                pass
        self.endDirectory()


    def endDirectory(self, cached=True):
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=cached)


