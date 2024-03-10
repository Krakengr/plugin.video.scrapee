# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcaddon
from resources.lib.modules import control
from resources.lib.modules import sync

try:
    import threading
except:
    pass

addon_name = xbmc.getInfoLabel('Container.PluginName')
addon_name = xbmcaddon.Addon(addon_name).getAddonInfo('name')
addon_icon = xbmcaddon.Addon().getAddonInfo('icon')
streamdbApi = control.setting('streamdb.api')

def syncLibrary():
    sync.syncLibrary()

def versionCheck():
    try:
        if control.version_check():
            xbmcgui.Dialog().notification(addon_name, 'There is a new version available', addon_icon)
    except:
        pass

try:
    versionCheck()

    if streamdbApi != '' and len(streamdbApi) > 0:
        try:
            timeout = 10
            schedSync = threading.Timer(timeout, syncLibrary)
            schedSync.start()
        except:
            syncLibrary()

        xbmcgui.Dialog().notification(addon_name, 'Syncing Database', addon_icon)
except Exception:
    xbmc.log('Scrapee DB Sync Failed', xbmc.LOGINFO)
    pass

#if __name__ == '__main__':
#syncLibrary()