# -*- coding: utf-8 -*-

import sys

from resources.lib.modules import bookmarks
from resources.lib.modules import control

def getMovieIndicators(refresh=False):
    try:
        indicators_ = bookmarks._indicators()
        return indicators_
    except:
        pass


def getTVShowIndicators(refresh=False):
    try:
        indicators_ = bookmarks._indicators()
        return indicators_
    except:
        pass

def getSeasonIndicators(imdb):
    pass

def getMovieOverlay(indicators_, imdb):
    try:
        overlay = bookmarks._get_watched('movie', imdb, '', '')
        return str(overlay)
    except:
        return '6'


def getTVShowOverlay(indicators_, imdb, tmdb):
    try:
        playcount = bookmarks._get_watched('tvshow', imdb, '', '')
        return str(playcount)
    except:
        return '6'


def getSeasonOverlay(indicators_, imdb, season):
    try:
        playcount = bookmarks._get_watched('season', imdb, season, '')
        return str(playcount)
    except:
        return '6'


def getEpisodeOverlay(indicators_, imdb, tmdb, season, episode):
    try:
        overlay = bookmarks._get_watched('episode', imdb, season, episode)
        return str(overlay)
    except:
        return '6'


def markMovieDuringPlayback(imdb, watched):
    try:
        if int(watched) == 7:
            bookmarks.reset(1, 1, 'movie', imdb, '', '')
    except:
        pass


def markEpisodeDuringPlayback(imdb, tmdb, season, episode, watched):
    try:
        if int(watched) == 7:
            bookmarks.reset(1, 1, 'episode', imdb, season, episode)
    except:
        pass


def movies(imdb, watched):
    control.busy()
    try:
        if int(watched) == 7:
            bookmarks.reset(1, 1, 'movie', imdb, '', '')
        else:
            bookmarks._delete_record('movie', imdb, '', '')
        
        control.refresh()
        control.idle()
    except:
        pass


def episodes(imdb, tmdb, season, episode, watched):
    control.busy()
    try:
        if int(watched) == 7:
            bookmarks.reset(1, 1, 'episode', imdb, season, episode)
        else:
            bookmarks._delete_record('episode', imdb, season, episode)
        control.refresh()
        control.idle()
    except:
        pass


def tvshows(tvshowtitle, imdb, tmdb, season, watched):
    control.busy()
    try:
        from resources.lib.indexers import episodes
        name = control.addonInfo('name')
        dialog = control.progressDialogBG
        dialog.create(str(name), str(tvshowtitle))
        dialog.update(0, str(name), str(tvshowtitle))
        items = []
        if season:
            items = episodes.episodes().get(tvshowtitle, '0', imdb, tmdb, meta=None, season=season, idx=False)
            items = [i for i in items if int('%01d' % int(season)) == int('%01d' % int(i['season']))]
            items = [{'label': '%s S%02dE%02d' % (tvshowtitle, int(i['season']), int(i['episode'])), 'season': int('%01d' % int(i['season'])), 'episode': int('%01d' % int(i['episode'])), 'unaired': i['unaired']} for i in items]
            for i in range(len(items)):
                if control.monitor.abortRequested():
                    return sys.exit()
                dialog.update(int((100 / float(len(items))) * i), str(name), str(items[i]['label']))
                _season, _episode, unaired = items[i]['season'], items[i]['episode'], items[i]['unaired']
                if int(watched) == 7:
                    if not unaired == 'true':
                        bookmarks.reset(1, 1, 'episode', imdb, _season, _episode)
                    else:
                        pass
                else:
                    bookmarks._delete_record('episode', imdb, _season, _episode)
        else:
            seasons = episodes.seasons().get(tvshowtitle, '0', imdb, tmdb, meta=None, idx=False)
            seasons = [i['season'] for i in seasons]
            for s in seasons:
                items = episodes.episodes().get(tvshowtitle, '0', imdb, tmdb, meta=None, season=s, idx=False)
                items = [{'label': '%s S%02dE%02d' % (tvshowtitle, int(i['season']), int(i['episode'])), 'season': int('%01d' % int(i['season'])), 'episode': int('%01d' % int(i['episode'])), 'unaired': i['unaired']} for i in items]
                for i in range(len(items)):
                    if control.monitor.abortRequested():
                        return sys.exit()
                    dialog.update(int((100 / float(len(items))) * i), str(name), str(items[i]['label']))
                    _season, _episode, unaired = items[i]['season'], items[i]['episode'], items[i]['unaired']
                    if int(watched) == 7:
                        if not unaired == 'true':
                            bookmarks.reset(1, 1, 'episode', imdb, _season, _episode)
                        else:
                            pass
                    else:
                        bookmarks._delete_record('episode', imdb, _season, _episode)
        try:
            dialog.close()
        except:
            pass
    except:
        try:
            dialog.close()
        except:
            pass

    control.refresh()
    control.idle()


