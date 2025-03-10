# -*- coding: utf-8 -*-
import time
from modules import settings, source_utils, kodi_utils, watched_status
from caches.favorites_cache import favorites
logger = kodi_utils.logger

CLIENT_ID = settings.streamdb_api_key()
sync_method = settings.database_sync()
json = kodi_utils.json
watched_db, favorites_db = kodi_utils.watched_db, kodi_utils.favorites_db
notification = kodi_utils.notification
standby_date = '2050-01-01T01:00:00.000Z'
res_format = '%Y-%m-%dT%H:%M:%S.%fZ'
API_ENDPOINT = 'https://streamdb.homebrewgr.info/index.php?api_key=%s'
set_bookmark_url = '&action=update-bookmark&tmdb=%s&time=%s&total_time=%s&type=%s&se=%s&ep=%s&title=%s&last_played=%s&resume_point=%s'
set_watched_url = '&action=mark-watched&tmdb=%s&last_played=%s&type=%s&title=%s&se=%s&ep=%s&bookmark_type=%s'
set_unwatched_url = '&action=delete-bookmark&tmdb=%s&type=%s&se=%s&ep=%s&bookmark_type=%s'
delete_bookmark_url = '&action=delete-bookmark&tmdb=%s&type=%s&se=%s&ep=%s'
delete_bookmarks_url = '&action=remove-history'
set_favorite_url = '&action=add-user-favorites&tmdb=%s&type=%s&title=%s'
delete_favorite_url = '&action=remove-user-favorites&tmdb=%s&type=%s'
delete_favorites_url = '&action=remove-favorites'
timeout = 20

def sync_databases():
    if CLIENT_ID == '' or sync_method == 0:
        return
    syncfavorites()
    syncfavorites('tv')
    syncbookmarks()
    syncbookmarks('movie', 'watched')
    syncbookmarks('tv')
    syncbookmarks('tv', 'watched')

    if sync_method == 1:
        notification(33220, 3000)
    pass

def syncbookmarks(type = 'movie', sync_type = 'progress'):
    if CLIENT_ID == '' or sync_method == 0:
        return
    
    type = 'movie' if type == 'movie' else 'tv'

    try:
        if sync_type == 'progress':
            data_link = 'https://streamdb.homebrewgr.info/index.php?action=get-sync-data&do=bookmarks&api_key=%s&type=%s' % (CLIENT_ID, type)
        elif sync_type == 'watched':
            data_link = 'https://streamdb.homebrewgr.info/index.php?action=get-sync-data&do=watchlist&api_key=%s&type=%s' % (CLIENT_ID, type)
        
        if type == 'tv':
            type = 'episode'
        
        content = source_utils.get_link(data_link)
        data_json = json.loads(content)

        if 'status' in data_json and data_json["status"] == "OK" and 'data' in data_json and len(data_json["data"]) > 0:
            watched_status.batch_erase_progress()
            for item in data_json["data"]:
                total_time = item['total_time'] if item['total_time'] is not None else 0
                episode = item['episode'] if type == 'episode' else ''
                season = item['season'] if type == 'episode' else ''
                resume_point = item['resume_point'] if item['resume_point'] is not None else ''
                last_played = item['last_played'] if item['last_played'] is not None else ''

                if sync_type == 'progress':
                    watched_status.set_sync_bookmark(type, item['tmdb_id'], season, episode, resume_point, 0, last_played, item['title'])
                elif sync_type == 'watched':
                    watched_status.set_sync_watched(type, item['tmdb_id'], season, episode, last_played, item['title'])
    except:
        return
    
def syncfavorites(type = 'movie'):
    if CLIENT_ID == '' or sync_method == 0:
        return

    type = 'movie' if type == 'movie' else 'tv'

    try:
        data_link = 'https://streamdb.homebrewgr.info/index.php?action=get-sync-data&do=favorites&api_key=%s&type=%s' % (CLIENT_ID, type)
        content = source_utils.get_link(data_link)
        data_json = json.loads(content)

        if type == 'tv':
            type = 'tvshow'

        if 'status' in data_json and data_json["status"] == "OK" and 'data' in data_json and len(data_json["data"]) > 0:
            favorites.clear_favorites(type)

            for item in data_json["data"]:
                favorites.set_favourite(type, item["tmdb_id"], item["title"], True)
    except:
        return
    
def mark_unwatched_status(media_type, tmdb_id, season, episode):
    if CLIENT_ID == '':
        return
    
    media_type = 'movie' if media_type == 'movie' else 'tv'

    try:
        url = API_ENDPOINT % CLIENT_ID
        url += set_unwatched_url % (tmdb_id, media_type, season, episode, 'watched')
        logger("url", url)
        source_utils.get_link(url)
    except:
        pass

def mark_watched_status(media_type, tmdb_id, season, episode, last_played, title):
    if CLIENT_ID == '':
        return
    
    media_type = 'movie' if media_type == 'movie' else 'tv'

    try:
        url = API_ENDPOINT % CLIENT_ID
        url += set_watched_url % (tmdb_id, last_played, media_type, title, season, episode, 'watched')
        logger("url", url)
        source_utils.get_link(url)
    except:
        pass

def delete_favourites(media_type, tmdb_id):
    if CLIENT_ID == '':
        return
    
    media_type = 'movie' if media_type == 'movie' else 'tv'

    try:
        url = API_ENDPOINT % CLIENT_ID
        url += delete_favorites_url % (tmdb_id, media_type)
        logger("url", url)
        source_utils.get_link(url)
    except:
        pass

def delete_favourite(media_type, tmdb_id):
    if CLIENT_ID == '':
        return
    
    media_type = 'movie' if media_type == 'movie' else 'tv'

    try:
        url = API_ENDPOINT % CLIENT_ID
        url += delete_favorite_url % (tmdb_id, media_type)
        logger("url", url)
        source_utils.get_link(url)
    except:
        pass

def set_favourite(media_type, tmdb_id, title):
    if CLIENT_ID == '':
        return
    
    media_type = 'movie' if media_type == 'movie' else 'tv'

    try:
        url = API_ENDPOINT % CLIENT_ID
        url += set_favorite_url % (tmdb_id, media_type, title)
        logger("url", url)
        source_utils.get_link(url)
    except:
        pass

def set_bookmark(params, last_played):
    if CLIENT_ID == '':
        return
    
    media_type, tmdb_id, curr_time, total_time = params.get('media_type'), params.get('tmdb_id'), params.get('curr_time'), params.get('total_time')
    title, season, episode = params.get('title'), params.get('season'), params.get('episode')
    adjusted_current_time = float(curr_time) - 5
    resume_point = round(adjusted_current_time/float(total_time)*100,1)
    media_type = 'movie' if media_type == 'movie' else 'tv'

    try:
        url = API_ENDPOINT % CLIENT_ID
        url += set_bookmark_url % (tmdb_id, curr_time, total_time, media_type, season, episode, title, last_played, resume_point)
        logger("url", url)
        source_utils.get_link(url)
    except:
        pass

def erase_bookmark(media_type, tmdb_id, season, episode):
    if CLIENT_ID == '':
        return
    
    media_type = 'movie' if media_type == 'movie' else 'tv'

    try:
        url = API_ENDPOINT % CLIENT_ID
        url += delete_bookmark_url % (tmdb_id, media_type, season, episode)
        logger("url", url)
        source_utils.get_link(url)
    except:
        pass

def erase_bookmarks():
    if CLIENT_ID == '':
        return
    
    try:
        url = API_ENDPOINT % CLIENT_ID
        url += delete_bookmarks_url
        logger("url", url)
        source_utils.get_link(url)
    except:
        pass