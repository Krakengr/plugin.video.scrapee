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