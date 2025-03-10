# -*- coding: utf-8 -*-
from modules import source_utils, kodi_utils
#from modules.kodi_utils import Thread, json, logger
from caches import links_cache
from modules import scraper as cl, client
import re, time

scraper = cl.create_scraper()
logger = kodi_utils.logger
json = kodi_utils.json
post_link = source_utils.post_link
extensions = source_utils.supported_video_extensions()
internal_results, check_title, clean_title, get_aliases_titles = source_utils.internal_results, source_utils.check_title, source_utils.clean_title, source_utils.get_aliases_titles
get_file_info, release_info_format, seas_ep_filter = source_utils.get_file_info, source_utils.release_info_format, source_utils.seas_ep_filter

class source:
	def __init__(self):
		self.scrape_provider = 'coverapi'
		self.sources = []
	
	def coverapi(self, imdb, type, season = 0, episode = 0):
		return self.get_coverapi_data(imdb, type, season, episode)

	def get_coverapi_data(self, imdb, type = 'movie', season = 0, episode = 0):
		file_link   = None
		data_json   = None
		content		= None
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
				return source_utils.build_link(cache[0][1], 'coverapi')
		
		url =   'https://coverapi.store/embed/' + imdb +'/'

		content = source_utils.get_link(url)
		
		if content is None:
			return

		z = re.search(r"news_id:.+'(.*?)'", content)

		if z is None:
			return
		
		news_id     = z.group(1)

		if type == 'movie':
			ref_link =   'https://coverapi.store/embed/' + imdb +'/'
			link = 'https://coverapi.store/engine/ajax/controller.php'
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0', 'Referer': ref_link}
			
			try:
				list = client.request(link, post={'mod': 'players', 'news_id': str(news_id)}, headers=headers, XHR=True)
			except:
				list = None
						
			if list is None or list == '':
				return
			
			data_json = json.loads(list)
			logger("data_json", str(data_json))
			
			if 'html5' in data_json:
				file = data_json['html5']
			else:
				file = data_json
					
			logger("file", str(file))

			z = re.search(r"file:"'(.*?)'",", file)
			t = re.search(r"title:"'(.*?)'",", file)
			logger("z", str(z))
			if z is None:
				return

			file_link = z.group(1)
			file_link = file_link.strip('\"').replace("https:", "http:")
			md5 = source_utils.get_md5(file_link)

			if t is not None:
				file_title = t.group(1)
				file_title = file_title.strip('\"')
			else:
				file_title = imdb

			links.add_link(file_link, type, imdb, time_now, self.scrape_provider, md5, season, episode, file_title)

			return source_utils.build_link(file_link, 'coverapi')
		else:
			play_url    = 'https://coverapi.store/uploads/playlists/' + str(news_id) + '.txt?v=' + str(time_now)
			list        = source_utils.get_link(play_url)

			try:
				data_json   = json.loads(list)
			
				if 'playlist' in data_json:
					i = 0
					s = 0

					#TV Shows with seasons
					for _item in data_json['playlist']:

						if 'playlist' in _item:
							season_name = _item['comment']
							se = re.search(r'\b\d{1,2}', season_name)
							s += 1
							
							if se is None:
								seas = i
							else:
								seas = int(se.group(0))
								
							for _index in _item['playlist']:
								i += 1
								episode_name    = _index['comment']
								episode_url     = _index['file']
								episode_url 	= episode_url.replace("https:", "http:")
								
								e = re.search(r'\b\d{1,3}', _index['comment'])
								
								if e is None:
									epis = i
								else:
									epis = e.group(0)

								md5 = source_utils.get_md5(episode_url)
								links.add_link(episode_url, 'tv', imdb, time_now, self.scrape_provider, md5, seas, epis)
						
						else:
							i += 1
							episode_name    = _item['comment']
							episode_url     = _item['file']
							episode_url 	= episode_url.replace("https:", "http:")

							e = re.search(r'\b\d{1,3}', episode_name)
							
							if e is None:
								epis = i
							else:
								epis = e.group(0)
							md5 = source_utils.get_md5(episode_url)
							links.add_link(episode_url, 'tv', imdb, time_now, self.scrape_provider, md5, 1, epis)

				#Return the link
				cache = links.get_link(type, imdb, expires, self.scrape_provider, season, episode )
		
				if cache is not None:
					return source_utils.build_link(cache[0][1], self.scrape_provider)
			except:
				pass