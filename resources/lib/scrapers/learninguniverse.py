# -*- coding: utf-8 -*-
from modules import source_utils, client
from modules.kodi_utils import logger
from caches import links_cache
import re, urllib, os, time
import simplejson as json

extensions = source_utils.supported_video_extensions()
internal_results, check_title, clean_title, get_aliases_titles = source_utils.internal_results, source_utils.check_title, source_utils.clean_title, source_utils.get_aliases_titles
get_file_info, release_info_format, seas_ep_filter = source_utils.get_file_info, source_utils.release_info_format, source_utils.seas_ep_filter

class source:
	def __init__(self):
		self.scrape_provider = 'learninguniverse'

	def learninguniverse(self, imdb, type, season = 0, episode = 0):
		return self.get_learninguniverse_data( imdb, type, season, episode)
		
	def get_learninguniverse_data(self, imdb, type = 'movie', season = 0, episode = 0 ):
		links 		= links_cache.LinksCache()
		time_now 	= int(time.time())
		expires 	= time_now - 43200
		
		if (type == 'movie'):
			cache = links.get_link(type, imdb, expires, self.scrape_provider )
		else:
			type = 'tv'
			cache = links.get_link(type, imdb, expires, self.scrape_provider, season, episode )
		
		if cache is not None:
			if cache[0][0] < expires:
				links.delete_record(type, self.scrape_provider, cache[0][5], imdb, season, episode)
			else:
				return source_utils.build_link(cache[0][1], self.scrape_provider)

		url   = 'https://learninguniverse.eu/videos/' + imdb
		
		content = source_utils.get_link(str(url))
		
		if content is None:
			return

		#zs = re.search(r'tracks:.*?"file":.*?"(.*?)"', content)
		
		#if zs is not None:
		#	slink = zs.group(1)
		#	#self.savesub(slink, imdb)

		z = re.search(r"sources:.*?file:.*?'(.*?)'", content)
		
		if z is not None:
			link = z.group(1)
			link = link.replace('https://', 'http://')
			md5 = source_utils.get_md5(link)
			links.add_link(link, type, imdb, time_now, self.scrape_provider, md5, season, episode)

			return source_utils.build_link(link, self.scrape_provider)
		
		return None