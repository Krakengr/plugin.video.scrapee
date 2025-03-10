# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from modules.kodi_utils import database, links_db
from modules.kodi_utils import logger

GET_ALL = 'SELECT id FROM links'
DELETE_ALL = 'DELETE FROM links'
MOVIE_SELECT = 'SELECT added, url, filename, info, size, hash from links where imdb = "%s" AND source = "%s"'
EPISODE_SELECT = 'SELECT added, url, filename, info, size, hash from links where imdb = "%s" AND source = "%s" AND season = "%s" AND episode = "%s"'
LIKE_DELETE = 'DELETE FROM links WHERE imdb = %s'
CLEAN = 'DELETE from links WHERE expire >= ?'
timeout = 240

class LinksCache(object):
	def __init__(self):
		self._connect_database()
		self._set_PRAGMAS()
		self.time = datetime.now()

	def delete_record(self, media_type, source, hash, imdb, season = 0, episode = 0):
		sql_delete = "DELETE FROM links WHERE imdb = '%s' AND source = '%s' AND hash = '%s'" % (imdb, source, hash)
		if media_type == 'tv':
			sql_delete += " AND season = '%s' AND episode = '%s'" % (str(season), str(episode))
		try:
			self.dbcur.execute(sql_delete)
			self.dbcon.commit()
		except:
			pass

	def get_link(self, media_type, imdb, expires, source, season = 0, episode = 0):
		try:
			if media_type == 'movie':
				cache_data = self.dbcur.execute(MOVIE_SELECT % (imdb, source)).fetchall()
			else:
				cache_data = self.dbcur.execute(EPISODE_SELECT % (imdb, source, str(season), str(episode))).fetchall()
			
			if cache_data:
				return cache_data
				
			return None
		except: return None

	def add_link(self, link, media_type, imdb, now, source, hash, season = 0, episode = 0, filename = '', info = '', size = '', expire = 0):
		try:
			sql_insert = "INSERT INTO links VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, %d)" % (link, media_type, filename, info, imdb, str(season), str(episode), source, hash, size, now, expire)
			logger("sql_insert", str(sql_insert))
			self.dbcur.execute(sql_insert)
			self.dbcon.commit()
		except:
			pass

	def _connect_database(self):
		self.dbcon = database.connect(links_db, timeout=timeout, isolation_level=None)

	def _execute(self, command, params):
		self.dbcur.execute(command, params)

	def _vacuum(self):
		self.dbcur.execute('VACUUM')

	def _set_PRAGMAS(self):
		self.dbcur = self.dbcon.cursor()
		self.dbcur.execute('''PRAGMA synchronous = OFF''')
		self.dbcur.execute('''PRAGMA journal_mode = OFF''')
