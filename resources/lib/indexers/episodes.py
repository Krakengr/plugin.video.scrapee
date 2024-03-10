# -*- coding: utf-8 -*-

import re
import os
import sys
import datetime

import simplejson as json
import six
from six.moves import range, urllib_parse
from kodi_six import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs

try:
    #from infotagger.listitem import ListItemInfoTag
    from resources.lib.modules.listitem import ListItemInfoTag
except:
    pass

from resources.lib.modules import bookmarks
from resources.lib.modules import control
from resources.lib.modules import cache
from resources.lib.modules import playcount
from resources.lib.modules import views

params = dict(urllib_parse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()
action = params.get('action')
control.moderator()
kodi_version = control.getKodiVersion()

class seasons:
    def __init__(self):
        self.list = []
        self.datetime = datetime.datetime.utcnow()
        self.today_date = self.datetime.strftime('%Y-%m-%d')
        self.addon_caching = control.setting('addon.caching') or 'true'
        self.lang = 'en' if control.setting('info.language') == 'English' else 'el'
        self.shownoyear = control.setting('show.noyear') or 'false'

    def get(self, tvshowtitle, year, imdb, tmdb, meta, idx=True, create_directory=True):
        try:
            root        = None
            filename    = imdb + '.xml'

            if cache.file_exists(filename, 'coverapi') and cache.file_time(filename, 'coverapi', True):
                root = cache.open_xml(filename, 'coverapi')
            
            #Try to refresh the cachefile
            else:
                cache.get_coverapi_data(imdb, 'tv')
                root = cache.open_xml(filename, 'coverapi')

            if (root is None):
                raise Exception()
            
            for value in root.findall('season'):
                title = value.findtext('title')
                season = value.findtext('number')
                self.list.append({'title': title, 'season': season, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'meta': meta})

            if create_directory == True:
                self.seasonDirectory(self.list)
            
            return self.list
        except:
            #log_utils.log('get', 1)
            pass

    def seasonDirectory(self, items):
        if items == None or len(items) == 0:
            control.idle()
            #sys.exit()
        sysaddon = sys.argv[0]
        syshandle = int(sys.argv[1])
        addonPoster = control.addonPoster()
        addonBanner = control.addonBanner()
        addonFanart = control.addonFanart()
        settingFanart = control.setting('fanart')
        try:
            indicators = playcount.getSeasonIndicators(items[0]['imdb'])
        except:
            pass
        watchedMenu = 'Mark as Watched'
        unwatchedMenu = 'Mark as Unwatched'
        
        for i in items:
            try:
                label = i['title']
                year = i['year']
                season = i['season']
                label = '%s (%s)' % (label, year)
                
                systitle = sysname = urllib_parse.quote_plus(i['title'])
                meta = json.loads(i['meta'])
                
                poster = meta['poster'] if 'poster' in meta else ''
                descr = meta['descr'] if 'descr' in meta else ''
                
                fanart = poster
                banner1 = poster
                banner = banner1 or fanart or addonBanner
                landscape = fanart
                
                ep_meta = {'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': poster, 'clearart': poster, 'landscape': landscape, 'duration': '45', 'status': ''}
                sysmeta = urllib_parse.quote_plus(json.dumps(ep_meta))
                imdb, tvdb, tmdb, year, season, fanart, duration, status = i['imdb'], i['tvdb'], i['tmdb'], i['year'], i['season'], fanart, '45', ''
                meta = dict((k,v) for k, v in six.iteritems(i) if not v == '0')
                meta.update({'mediatype': 'tvshow'})
                meta.update({'code': tmdb, 'imdbnumber': imdb, 'imdb_id': imdb, 'tvdb_id': tvdb})
                meta.update({'trailer': '%s?action=trailer&name=%s&tmdb=%s&imdb=%s&season=%s' % (sysaddon, systitle, tmdb, imdb, season)})
                
                if not 'duration' in i:
                    meta.update({'duration': '60'})
                elif i['duration'] == '0':
                    meta.update({'duration': '60'})
                try:
                    meta.update({'duration': str(int(meta['duration']) * 60)})
                except:
                    pass
                try:
                    seasonYear = i['year']
                    meta.update({'year': seasonYear})
                except:
                    pass
                meta.update({'plot': descr})
                cm = []
                cm.append(('Clean Tools Widget', 'RunPlugin(%s?action=cleantools_widget)' % sysaddon))
                cm.append(('Queue Item', 'RunPlugin(%s?action=queue_item)' % sysaddon))
                cm.append(('Add to Library', 'RunPlugin(%s?action=tvshow_to_library&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s)' % (sysaddon, systitle, year, imdb, tmdb)))
                if kodi_version < 17:
                    cm.append(('Information', 'Action(Info)'))
                try:
                    overlay = int(playcount.getSeasonOverlay(indicators, imdb, season))
                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=tvshows_playcount&name=%s&imdb=%s&tmdb=%s&season=%s&query=6)' % (sysaddon, systitle, imdb, tmdb, season)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=tvshows_playcount&name=%s&imdb=%s&tmdb=%s&season=%s&query=7)' % (sysaddon, systitle, imdb, tmdb, season)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass
                try:
                    item = control.item(label=label, offscreen=True)
                except:
                    item = control.item(label=label)
                art = {}
                art.update({'icon': poster, 'thumb': poster, 'poster': poster, 'banner': banner, 'landscape': landscape})
                if settingFanart == 'true':
                    art.update({'fanart': fanart})
                elif not addonFanart == None:
                    art.update({'fanart': addonFanart})
                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})
                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})
                item.setArt(art)
                item.addContextMenuItems(cm)
                if kodi_version >= 20:
                    info_tag = ListItemInfoTag(item, 'video')
                castwiththumb = i.get('castwiththumb')
                if castwiththumb and not castwiththumb == '0':
                    if kodi_version >= 18:
                        if kodi_version >= 20:
                            info_tag.set_cast(castwiththumb)
                        else:
                            item.setCast(castwiththumb)
                    else:
                        cast = [(p['name'], p['role']) for p in castwiththumb]
                        meta.update({'cast': cast})
                if kodi_version >= 20:
                    info_tag.set_info(control.metadataClean(meta))
                else:
                    item.setInfo(type='Video', infoLabels=control.metadataClean(meta))
                video_streaminfo = {'codec': 'h264'}
                if kodi_version >= 20:
                    info_tag.add_stream_info('video', video_streaminfo)
                else:
                    item.addStreamInfo('video', video_streaminfo)
                url = '%s?action=episodes&year=%s&imdb=%s&tmdb=%s&meta=%s&season=%s' % (sysaddon, year, imdb, tmdb, sysmeta, season)
                
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
                
            except:
                #log_utils.log('seasonDirectory', 1)
                pass
        try:
            control.property(syshandle, 'showplot', items[0]['plot'])
        except:
            #log_utils.log('seasonDirectory', 1)
            pass
        control.content(syshandle, 'seasons')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('seasons', {'skin.aeon.nox.silvo' : 50, 'skin.estuary': 55, 'skin.confluence': 500}) #View 50 List #View 501 LowList


class episodes:
    def __init__(self):
        self.list = []
        self.datetime = datetime.datetime.utcnow()
        self.systime = self.datetime.strftime('%Y%m%d%H%M%S%f')
        self.today_date = self.datetime.strftime('%Y-%m-%d')
        self.addon_caching = control.setting('addon.caching') or 'true'
        self.episode_thumbs = control.setting('episode.thumbs') or 'false'
        self.episode_views = control.setting('episode.views') or 'false'
        self.shownoyear = control.setting('show.noyear') or 'false'

    def get(self, imdb, tmdb, season, year, meta):
        
        try:
            root        = None
            filename    = imdb + '.xml'
            season      = int(season)

            if cache.file_exists(filename, 'coverapi') and cache.file_time(filename, 'coverapi', True):
                root = cache.open_xml(filename, 'coverapi')
            
            #Try to refresh the cachefile
            else:
                cache.get_coverapi_data(imdb, 'tv')
                root = cache.open_xml(filename, 'coverapi')
            
            if (root is None):
                raise Exception()
            
            for value in root.findall('season'):
                season_ = int(value.findtext('number'))
                
                if ( season_ != season):
                    continue

                epiz = value.find('episodes')

                for epis in epiz.findall('episode'):
                    e_title = epis.findtext('title')
                    
                    epi_ = epis.findtext('number')
                    episode_url = epis.findtext('link')
                    self.list.append({'title': e_title, 'episode': epi_, 'season': season_, 'year': year, 'link': episode_url, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'meta': meta})
            
            self.episodeDirectory(self.list)
            
            return self.list
        except:
            #log_utils.log('get', 1)
            pass

    def episodeDirectory(self, items):
        
        if items == None or len(items) == 0:
            control.idle()
            #sys.exit()
        
        sysaddon = sys.argv[0]
        syshandle = int(sys.argv[1])
        isPlayable = True
        indicators = playcount.getTVShowIndicators(refresh=True)

        try:
            multi = [i['title'] for i in items]
        except:
            multi = []
        multi = len([x for y,x in enumerate(multi) if x not in multi[:y]])
        multi = True if multi > 1 else False
        try:
            sysaction = items[0]['action']
        except:
            sysaction = ''
        isFolder = False
        watchedMenu = 'Mark as Watched'
        unwatchedMenu = 'Mark as Unwatched'
        playbackMenu = 'Auto Play'

        for i in items:
            
            try:
                if not 'label' in i:
                    i['label'] = i['title']
                if i['label'] == '0':
                    label = '%sx%02d . %s %s' % (i['season'], int(i['episode']), 'Episode', i['episode'])
                else:
                    label = '%sx%02d . %s' % (i['season'], int(i['episode']), i['title'])
                if multi == True:
                    label = '%s - %s' % (i['title'], label)

                imdb, tvdb, tmdb, year, season, episode = i['imdb'], i['tvdb'], i['tmdb'], i['year'], i['season'], i['episode']
                meta = json.loads(i['meta'])
                poster = meta['poster'] if 'poster' in meta else ''
                descr = meta['descr'] if 'descr' in meta else ''
                
                fanart = poster
                banner1 = poster
                banner = banner1
                landscape = fanart
                seasons_meta = {'poster': poster, 'fanart': fanart, 'banner': banner, 'clearlogo': banner, 'clearart': banner, 'landscape': landscape, 'duration': '45', 'status': 'aired'}
                
                seas_meta = urllib_parse.quote_plus(json.dumps(seasons_meta))
                systitle = urllib_parse.quote_plus(i['title'])
                systvshowtitle = urllib_parse.quote_plus(i['title'])
                syspremiered = urllib_parse.quote_plus(i['year'])
                meta = dict((k,v) for k, v in six.iteritems(i) if not v == '0')
                
                meta.update({'mediatype': 'episode'})
                
                meta.update({'code': tmdb, 'imdbnumber': imdb})
                meta.update({'trailer': '%s?action=trailer&name=%s&tmdb=%s&imdb=%s&season=%s&episode=%s' % (sysaddon, systvshowtitle, tmdb, imdb, season, episode)})
                
                if not 'duration' in i:
                    meta.update({'duration': '45'})
                elif i['duration'] == '0':
                    meta.update({'duration': '45'})
                try:
                    meta.update({'duration': str(int(meta['duration']) * 60)})
                except:
                    pass
                
                try:
                    meta.update({'year': i['year'] })
                except:
                    pass
                try:
                    meta.update({'title': i['title']})
                except:
                    pass
                try:
                    meta.update({'tvshowyear': i['year']}) # Kodi uses the year (the year the show started) as the year for the episode. Change it from the premiered date.
                except:
                    pass
                
                meta.update({'poster': poster, 'fanart': fanart, 'banner': banner})
                sysmeta = urllib_parse.quote_plus(json.dumps(meta))
                url = '%s?action=play&title=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s&meta=%s&t=%s' % (sysaddon, systitle, year, imdb, tmdb, tvdb, season, episode, systvshowtitle, syspremiered, sysmeta, self.systime)
                
                sysurl = urllib_parse.quote_plus(url)
                path = '%s?action=play&title=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&season=%s&episode=%s&tvshowtitle=%s&premiered=%s' % (sysaddon, systitle, year, imdb, tmdb, tvdb, season, episode, systvshowtitle, syspremiered)
                
                fileurl = i['link']

                if isFolder == True:
                    url = '%s?action=episodes&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&meta=%s&season=%s&episode=%s' % (sysaddon, systvshowtitle, year, imdb, tmdb, seas_meta, season, episode)
                else:
                    url = '%s?action=play&type=tv&title=%s&year=%s&imdb=%s&tmdb=%s&meta=%s&t=%s&fileurl=%s&season=%s&episode=%s' % (sysaddon, systitle, year, imdb, tmdb, sysmeta, self.systime, urllib_parse.quote_plus(fileurl), season, episode)
                sysurl = urllib_parse.quote_plus(url)
                cm = []
                cm.append(('Clean Tools Widget', 'RunPlugin(%s?action=cleantools_widget)' % sysaddon))
                cm.append(('Clear Providers', 'RunPlugin(%s?action=clear_sources)' % sysaddon))
                if multi == True:
                    cm.append(('Browse Series', 'Container.Update(%s?action=seasons&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s&meta=%s,return)' % (sysaddon, systvshowtitle, year, imdb, tmdb, seas_meta)))
                cm.append(('Queue Item', 'RunPlugin(%s?action=queue_item)' % sysaddon))
                cm.append(('Add to Library', 'RunPlugin(%s?action=tvshow_to_library&tvshowtitle=%s&year=%s&imdb=%s&tmdb=%s)' % (sysaddon, systvshowtitle, year, imdb, tmdb)))
                
                if kodi_version < 17:
                    cm.append(('Information', 'Action(Info)'))
                try:
                    overlay = int(playcount.getEpisodeOverlay(indicators, imdb, tmdb, season, episode))
                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=episodes_playcount&imdb=%s&tmdb=%s&season=%s&episode=%s&query=6)' % (sysaddon, imdb, tmdb, season, episode)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=episodes_playcount&imdb=%s&tmdb=%s&season=%s&episode=%s&query=7)' % (sysaddon, imdb, tmdb, season, episode)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except:
                    pass
                
                if isFolder == False:
                    cm.append((playbackMenu, 'RunPlugin(%s?action=alter_sources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))
                try:
                    item = control.item(label=label, offscreen=True)
                except:
                    item = control.item(label=label)
                art = {}
                thumb = poster
                
                clearlogo = meta.get('clearlogo', '')
                clearart = meta.get('clearart', '')
                art.update({'icon': thumb, 'thumb': thumb, 'banner': banner, 'poster': thumb, 'tvshow.poster': poster, 'season.poster': poster, 'landscape': landscape, 'clearlogo': clearlogo, 'clearart': clearart})
                art.update({'fanart': fanart})
                item.setArt(art)
                item.addContextMenuItems(cm)
                
                if isPlayable:
                    item.setProperty('IsPlayable', 'true')
                
                offset = bookmarks.get('episode', imdb, season, episode)
                
                if float(offset) > 120:
                    percentPlayed = int(float(offset) / float(meta['duration']) * 100)
                    item.setProperty('resumetime', str(offset))
                    item.setProperty('percentplayed', str(percentPlayed))
                
                if kodi_version >= 20:
                    info_tag = ListItemInfoTag(item, 'video')
                castwiththumb = False
                if castwiththumb and not castwiththumb == '0':
                    if kodi_version >= 18:
                        if kodi_version >= 20:
                            info_tag.set_cast(castwiththumb)
                        else:
                            item.setCast(castwiththumb)
                    else:
                        cast = [(p['name'], p['role']) for p in castwiththumb]
                        meta.update({'cast': cast})
                if kodi_version >= 20:
                    info_tag.set_info(control.metadataClean(meta))
                else:
                    item.setInfo(type='Video', infoLabels=control.metadataClean(meta))
                video_streaminfo = {'codec': 'h264'}
                if kodi_version >= 20:
                    info_tag.add_stream_info('video', video_streaminfo)
                else:
                    item.addStreamInfo('video', video_streaminfo)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)
            except:
                #log_utils.log('episodeDirectory', 1)
                pass
        if self.episode_views == 'true':
            control.content(syshandle, 'seasons')
            control.directory(syshandle, cacheToDisc=True)
            views.setView('seasons', {'skin.aeon.nox.silvo' : 50, 'skin.estuary': 55, 'skin.confluence': 500}) #View 50 List #View 501 LowList
        else:
            control.content(syshandle, 'episodes')
            control.directory(syshandle, cacheToDisc=True)
            views.setView('episodes', {'skin.aeon.nox.silvo' : 50, 'skin.estuary': 55, 'skin.confluence': 504}) #View 50 List #View 501 LowList


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
                cm = []
                cm.append(('Clean Tools Widget', 'RunPlugin(%s?action=cleantools_widget)' % sysaddon))
                if queue == True:
                    cm.append(('Queue Item', 'RunPlugin(%s?action=queue_item)' % sysaddon))
                try:
                    item = control.item(label=name, offscreen=True)
                except:
                    item = control.item(label=name)
                item.setArt({'icon': thumb, 'thumb': thumb, 'fanart': addonFanart})
                item.addContextMenuItems(cm)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                #log_utils.log('addDirectory', 1)
                pass
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)


