# -*- coding: utf-8 -*-

from resources.lib.modules import bookmarks
from resources.lib.modules import favorites
from resources.lib.modules import history
from resources.lib.modules import likes
from resources.lib.modules import cache

def deleteRecords():
    cache.clean_history(False)
    cache.clean_favorites(False)
    cache.clean_likes(False)

def deleteFiles():
    cache.delete_cache('user_data.json')
    cache.delete_cache('user_data_movie.json')
    cache.delete_cache('user_data_tv.json')

def syncTv():
    bookmarks.syncdb('tv')
    favorites.syncfdb('tv')
    history.synchdb('tv')
    likes.syncldb('tv')

def firstSync():
    from resources.lib.modules import control
    import xbmcgui, xbmc, os, xbmcaddon

    if os.path.exists(control.syncFile):
        return

    streamdbApi = control.setting('streamdb.api')
    
    if streamdbApi == '' or len(streamdbApi) == 0:
        return
    
    addon_name = xbmc.getInfoLabel('Container.PluginName')
    addon_name = xbmcaddon.Addon(addon_name).getAddonInfo('name')
    addon_icon = xbmcaddon.Addon().getAddonInfo('icon')

    xbmcgui.Dialog().notification(addon_name, 'Please Wait, Synchronizing Data...', addon_icon)
    xbmc.log('Scrapee First DB Sync started', xbmc.LOGINFO)
    syncMovies()
    syncTv()

    with open(control.syncFile, 'w') as file:
        file.write('')
        file.close()
    
def syncMovies():
    bookmarks.syncdb()
    favorites.syncfdb()
    history.synchdb()
    likes.syncldb()

def syncLibrary():
    deleteFiles()
    deleteRecords()
    syncMovies()
    syncTv()