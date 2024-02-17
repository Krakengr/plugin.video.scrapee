# -*- coding: utf-8 -*-

import xbmc
import xbmcvfs
import xbmcgui
import xbmcaddon
import threading
from resources.lib.modules import control
from resources.lib.modules import sync

addon_name = xbmc.getInfoLabel('Container.PluginName')
addon_name = xbmcaddon.Addon(addon_name).getAddonInfo('name')
addon_icon = xbmcaddon.Addon().getAddonInfo('icon')
streamdbApi = control.setting('streamdb.api')

def syncLibrary():
    sync.syncLibrary()

try:
    timeout = 10
    if streamdbApi != '' and len(streamdbApi) > 0:
        schedSync = threading.Timer(timeout, syncLibrary)
        schedSync.start()
        xbmcgui.Dialog().notification(addon_name, 'Syncing Database', addon_icon)
        xbmc.log('Scrapee DB Sync started', xbmc.LOGINFO)
except Exception:
    xbmc.log('Scrapee DB Sync Failed', xbmc.LOGINFO)
    pass

#if __name__ == '__main__':
#syncLibrary()