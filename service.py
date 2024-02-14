# -*- coding: utf-8 -*-

import xbmc
import xbmcvfs
import xbmcgui
import xbmcaddon
import threading
from resources.lib.modules import control
from resources.lib.modules import bookmarks
from resources.lib.modules import favorites
from resources.lib.modules import history
from resources.lib.modules import likes
from resources.lib.modules import cache

addon_name = xbmc.getInfoLabel('Container.PluginName')
addon_name = xbmcaddon.Addon(addon_name).getAddonInfo('name')
addon_icon = xbmcaddon.Addon().getAddonInfo('icon')
addon_path = xbmcvfs.translatePath('special://home/addons/plugin.video.scrapee')
streamdbApi = control.setting('streamdb.api')

def syncTv():
    bookmarks.syncdb('tv')
    favorites.syncfdb('tv')
    history.synchdb('tv')
    likes.syncldb('tv')

def syncMovies():
    bookmarks.syncdb()
    favorites.syncfdb()
    history.synchdb()
    likes.syncldb()

def syncLibrary():
    cache.delete_cache('user_data.json')
    cache.delete_cache('user_data_movie.json')
    cache.delete_cache('user_data_tv.json')
    syncMovies()
    syncTv()

try:
    timeout = 10
    if streamdbApi != '' and len(streamdbApi) > 0:
        schedSync = threading.Timer(timeout, syncLibrary)
        schedSync.start()
        xbmcgui.Dialog().notification(addon_name, f"Syncing Databases", addon_icon)
        xbmc.log('Scrapee DB Sync started', xbmc.LOGINFO)
except Exception:
    xbmc.log('Scrapee DB Sync Failed', xbmc.LOGINFO)
    pass

#if __name__ == '__main__':
#syncLibrary()