# -*- coding: utf-8 -*-

import os
import sys

from resources.lib.modules import control
from resources.lib.modules import log_utils
from kodi_six import xbmc, xbmcplugin, xbmcgui
from resources.lib.modules import views

try:
    from resources.lib.modules.listitem import ListItemInfoTag
except:
    pass

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
control.moderator()

kodi_version = control.getKodiVersion()

class play:
    def get(self, url):
        xbmc.log('self.curr_url: ' + str(url), xbmc.LOGINFO)
        if url == None:
            self.root()
        elif url == 'play_menu':
            self.root()

    def root(self):
        isFolder=True
        u = sys.argv[0] + '?url=r&mode=d&name=d&iconimage=s'
        ok = True
        liz = xbmcgui.ListItem('name')
        liz.setArt({ 'thumb': 'iconimage', 'icon': 'icon', 'fanart': 'fanart'})
        control.addItem(handle=syshandle, url=u, listitem=liz, isFolder=isFolder)
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=isFolder)
    
    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True):
        url = '%s&url=%s' % (sysaddon, query) if isAction == True else query
        name = str(name)
        xbmc.log('curr_url: ' + name, xbmc.LOGINFO)
        
        artPath = control.artPath()
        fanart = control.addonFanart()
        thumb = os.path.join(artPath, thumb) if not (artPath == None or thumb == None) else icon
        cm = []
        cm.append(('[B]View Change Log[/B]', 'RunPlugin(%s?action=view_changelog)' % sysaddon))
        cm.append(('[B]Clean Tools Widget[/B]', 'RunPlugin(%s?action=cleantools_widget)' % sysaddon))
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


