# -*- coding: utf-8 -*-

from six.moves.urllib_parse import parse_qsl
from kodi_six import xbmc

def router(_argv):
    params = dict(parse_qsl(_argv.replace('?', '')))
    action = params.get('action')
    select = params.get('select')
    url = params.get('url')
    query = params.get('query')
    id = params.get('id')
    setting = params.get('setting')
    source = params.get('source')
    content = params.get('content')
    image = params.get('image')
    meta = params.get('meta')
    item = params.get('item')
    media_type = params.get('type')
    imdb = params.get('imdb')
    tmdb = params.get('tmdb')
    tvdb = params.get('tvdb')
    name = params.get('name')
    title = params.get('title')
    fileurl = params.get('fileurl')
    tvshowtitle = params.get('tvshowtitle')
    season = params.get('season')
    episode = params.get('episode')
    year = params.get('year')
    premiered = params.get('premiered')
    windowedtrailer = params.get('windowedtrailer')
    windowedtrailer = int(windowedtrailer) if windowedtrailer in ("0", "1") else 0

    #if action != None:
    #   xbmc.log('Action: ' + action, xbmc.LOGINFO)

    if action == None:
        from resources.lib.indexers import navigator
        navigator.navigator().root()

    elif action == 'movies_menu':
        from resources.lib.indexers import navigator
        from resources.lib.modules import control
       
        #bookmarks.syncdb()
        #favorites.syncfdb()
        #history.synchdb()
        #likes.syncldb()

        if not control.condVisibility('System.HasAddon(script.module.cloudscraper)'):
            control.installAddon('script.module.cloudscraper')
            
        navigator.navigator().moviesMenu()
    
    elif action == 'tvshows_menu':
        from resources.lib.indexers import navigator
        from resources.lib.modules import control
        
        #bookmarks.syncdb('tv')
        #favorites.syncfdb('tv')
        #history.synchdb('tv')
        #likes.syncldb('tv')

        if not control.condVisibility('System.HasAddon(script.module.cloudscraper)'):
            control.installAddon('script.module.cloudscraper')

        navigator.navigator().tvshows()
    
    elif action == 'tv_search':
        from resources.lib.indexers import tvshows
        tvshows.tvshows().search_term_menu(select)

    elif action == 'movies_search':
        from resources.lib.indexers import movies
        movies.movies().search_term_menu(select)

    elif action == 'tv_searchterm':
        from resources.lib.indexers import tvshows
        tvshows.tvshows().search_term(select, name)

    elif action == 'movies_searchterm':
        from resources.lib.indexers import movies
        movies.movies().search_term(select, name)
        
    elif action == 'movies':
        from resources.lib.indexers import movies
        movies.movies().get(url)
    
    elif action == 'tv':
        from resources.lib.indexers import tvshows
        tvshows.tvshows().get(url)

    elif action == 'ytube_menu':
        from resources.lib.modules import control
        if not control.condVisibility('System.HasAddon(plugin.video.youtube)'):
            control.installAddon('plugin.video.youtube')
        from resources.lib.indexers import navigator
        navigator.navigator().ytMenu()

    elif action == 'ytube':
        from resources.lib.indexers import youtube
        youtube.ytube().get(url)

    elif action == 'yt_search':
        from resources.lib.indexers import youtube
        youtube.ytube().search_term_menu(select)
    
    elif action == 'yt_searchterm':
        from resources.lib.indexers import youtube
        youtube.ytube().search_term(select, name)

    elif action == 'play':
        from resources.lib.modules import sources
        sources.sources().play(title, year, media_type, imdb, tmdb, tvdb, season, episode, tvshowtitle, premiered, meta, select, fileurl)

    elif action == 'episodes':
        from resources.lib.indexers import episodes
        episodes.episodes().get(imdb, tmdb, season, year, meta)

    elif action == 'seasons':
        from resources.lib.indexers import episodes
        episodes.seasons().get(tvshowtitle, year, imdb, tmdb, meta)

    elif action == 'search_movies_menu':
        from resources.lib.indexers import navigator
        navigator.navigator().search_movies()
    
    elif action == 'search_yt_menu':
        from resources.lib.indexers import navigator
        navigator.navigator().search_yt()

    elif action == 'search_tvshows_menu':
        from resources.lib.indexers import navigator
        navigator.navigator().search_tvshows()
    
    elif action == 'trailer':
        from resources.lib.modules import control
        if not control.condVisibility('System.HasAddon(plugin.video.youtube)'):
            control.installAddon('plugin.video.youtube')
        from resources.lib.modules import trailer
        trailer.source().get(name, url, tmdb, imdb, season, episode, windowedtrailer)

    elif action == 'open_settings':
        from resources.lib.modules import control
        control.openSettings(query, id)

    elif action == 'queue_item':
        from resources.lib.modules import control
        control.queueItem()

    elif action == 'service':
        from resources.lib.modules import libtools
        libtools.libepisodes().service()


    elif action == 'tools_menu':
        from resources.lib.indexers import navigator
        navigator.navigator().tools()


    elif action == 'open_root':
        from resources.lib.indexers import navigator
        navigator.navigator().root()


    elif action == 'add_item':
        from resources.lib.modules import sources
        sources.sources().addItem(title)


    elif action == 'add_view':
        from resources.lib.modules import views
        views.addView(content)

    elif action == 'clean_settings':
        from resources.lib.indexers import navigator
        navigator.navigator().cleanSettings()

    elif action == 'clear_favorites':
        from resources.lib.indexers import navigator
        navigator.navigator().cleanFavorites()

    elif action == 'clear_history':
        from resources.lib.indexers import navigator
        navigator.navigator().cleanHistory()

    elif action == 'clear_likes':
        from resources.lib.indexers import navigator
        navigator.navigator().cleanLikes()       

    elif action == 'cleantools_menu':
        from resources.lib.indexers import navigator
        navigator.navigator().cleantools()


    elif action == 'cleantools_widget':
        from resources.lib.indexers import navigator
        navigator.navigator().cleantools_widget()


    elif action == 'clear_all_cache':
        from resources.lib.indexers import navigator
        navigator.navigator().clearCacheAll()

    elif action == 'clear_cache':
        from resources.lib.indexers import navigator
        navigator.navigator().clearCache()

    elif action == 'clear_debuglog':
        from resources.lib.indexers import navigator
        navigator.navigator().clearDebugLog()

    elif action == 'clear_meta_cache':
        from resources.lib.indexers import navigator
        navigator.navigator().clearCacheMeta()

    elif action == 'clear_resolveurl_cache':
        from resources.lib.modules import control
        control.execute('RunPlugin(plugin://script.module.resolveurl/?mode=reset_cache)')

    elif action == 'clear_search_cache':
        from resources.lib.indexers import navigator
        navigator.navigator().clearCacheSearch(select)

    elif action == 'clear_viewtypes':
        from resources.lib.indexers import navigator
        navigator.navigator().clearViewTypes()


    elif action == 'color_choice':
        from resources.lib.modules import colorcode
        colorcode.colorChoice(setting, query)


    elif action == 'devtools_menu':
        from resources.lib.indexers import navigator
        navigator.navigator().devtools()


    elif action == 'episodes':
        from resources.lib.indexers import episodes
        episodes.episodes().get(tvshowtitle, year, imdb, tmdb, meta, season, episode)


    elif action == 'episodes_playcount':
        from resources.lib.modules import playcount
        playcount.episodes(imdb, tmdb, season, episode, query)


    elif action == 'moreplugs_menu':
        from resources.lib.indexers import navigator
        navigator.navigator().moreplugs()


    elif action == 'movie_to_library':
        from resources.lib.modules import libtools
        libtools.libmovies().add(name, title, year, imdb, tmdb)


    elif action == 'movies_playcount':
        from resources.lib.modules import playcount
        playcount.movies(imdb, query)


    elif action == 'movies_to_library':
        from resources.lib.modules import libtools
        libtools.libmovies().range(url)


    elif action == 'movies_to_library_silent':
        from resources.lib.modules import libtools
        libtools.libmovies().silent(url)


    elif action == 'tvshows_search':
        from resources.lib.indexers import tvshows
        tvshows.tvshows().search_term_menu(select)


    elif action == 'tvshows_searchterm':
        from resources.lib.indexers import tvshows
        tvshows.tvshows().search_term(select, name)


    elif action == 'tvshows_to_library':
        from resources.lib.modules import libtools
        libtools.libtvshows().range(url)


    elif action == 'tvshows_to_library_silent':
        from resources.lib.modules import libtools
        libtools.libtvshows().silent(url)

    elif action == 'update_library':
        from resources.lib.modules import libtools
        libtools.libepisodes().update(query)


    elif action == 'view_changelog':
        from resources.lib.modules import log_utils
        log_utils.changelog()


    elif action == 'view_previous_changelogs':
        from resources.lib.modules import log_utils
        log_utils.previous_changelogs()


    elif action == 'view_debuglog':
        from resources.lib.modules import log_utils
        log_utils.view_log()


    elif action == 'views_menu':
        from resources.lib.indexers import navigator
        navigator.navigator().views()


    elif action == 'installs_menu':
        from resources.lib.indexers import navigator
        navigator.navigator().installsmenu()


    elif action == 'installAddon':
        from resources.lib.modules import control
        control.installAddon(id)


    elif action == 'alt_play':
        from resources.lib.modules import player
        player.playItem(url)
        #player.playMedia(url)

    elif action == 'addlike':
        from resources.lib.modules import likes
        likes.addLike(meta, content)


    elif action == 'deletelike':
        from resources.lib.modules import likes
        likes.deleteLike(meta, content)


    elif action == 'favoritesNavigator':
        from resources.lib.indexers import navigator
        navigator.navigator().favorites()


    elif action == 'movieFavorites':
        from resources.lib.indexers import movies
        movies.movies().favorites()


    elif action == 'tvFavorites':
        from resources.lib.indexers import tvshows
        tvshows.tvshows().favorites()


    elif action == 'addFavorite':
        from resources.lib.modules import favorites
        favorites.addFavorite(meta, content)


    elif action == 'deleteFavorite':
        from resources.lib.modules import favorites
        favorites.deleteFavorite(meta, content)
    

    elif action == 'open_sidemenu': # Forces open the side menu aka slide menu.
        from resources.lib.modules import control
        control.execute('SetProperty(MediaMenu,True,Home)')


    elif action == 'testing':
        from resources.lib.modules import log_utils
        try:
            test = []
            """ # Some saved testing items...
            Movie_imdb = 'tt0379786'
            Movie_tmdb = '16320'
            Movie_title = 'Serenity'
            Movie_year = '2005'
            TVShow_imdb = 'tt0303461'
            TVShow_tmdb = '1437'
            TVShow_title = 'Firefly'
            TVShow_year = '2002'
            TVShow_season = '1'
            TVShow_episode = '4'
            """
            log_utils.log('Testing - test: ' + repr(test))
        except:
            log_utils.log('Testing', 1)
            pass


