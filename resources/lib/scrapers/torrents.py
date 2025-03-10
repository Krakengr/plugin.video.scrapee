# -*- coding: utf-8 -*-
from modules import source_utils
from modules.kodi_utils import Thread
from modules.utils import clean_file_name, normalize
from modules.settings import torrents_limit
from caches import links_cache
from modules.kodi_utils import logger
import re, requests, time, json

extensions = source_utils.supported_video_extensions()
internal_results, check_title, clean_title, get_aliases_titles = source_utils.internal_results, source_utils.check_title, source_utils.clean_title, source_utils.get_aliases_titles
get_file_info, release_info_format, seas_ep_filter = source_utils.get_file_info, source_utils.release_info_format, source_utils.seas_ep_filter

results = '''{
	"results": []
}'''

json_data = json.loads(results)

class source:
	def __init__(self):
		self.scrape_provider = ''
		self.links = links_cache.LinksCache()
		self.limit = torrents_limit()
	def torrent(self, imdb, title, type, season = 0, episode = 0, year = 0):
		return self.get_torrent_data(imdb, title, type, season, episode, year)
	def make_nums(self, num):
		num = str(num)
		if len(num) == 1:
			num = '0' + num
		return num
	def get_torrent_data(self, imdb, title, type = 'movie', season = 0, episode = 0, year = 0):
		self.scrape_provider = 'thepiratebay'
		
		self.time_now 	= int(time.time())
		expires 	= self.time_now - 43200
		self.type   = type
		self.imdb   = imdb
		self.season   = season
		self.episode   = episode
		url = 'https://proxy.wafflehacker.io/?destination=https://knaben.xyz/thepiratebay/s/?q=' + title.replace(" ", "+")
				
		if (self.type == 'movie'):
			cache = self.links.get_link(self.type, self.imdb, expires, self.scrape_provider)
			#https://1337x.to/category-search/The%20Brutalist%202024/Movies/1/
			category = '201'
			if year > 0:
				url += '+(' + str(year) + ')'
		else:
			self.type = 'tv'
			cache = self.links.get_link(self.type, self.imdb, expires, self.scrape_provider, self.season, self.episode )
			#https://1337x.to/category-search/The%20Brutalist%202024/TV/1/
			#208 = HD TV SHOWS
			category = '205'
			url += '+S' + self.make_nums(self.season) + 'E' + self.make_nums(self.episode)
		
		if cache is not None:
			valid = 0
			for c in cache:
				if c[0] < expires:
					self.links.delete_record(self.type, self.scrape_provider, c[5], self.imdb, self.season, self.episode)
				valid += 1
				tmp = source_utils.build_link(c[1], self.scrape_provider, c[2], c[2] + ' - ' + c[3])
				json_data['results'].append(tmp)
			if valid > 0:
				return json_data
		
		url += '&category=200&page=0&orderby=99'
		url2 = url
		
		content = source_utils.get_link(url)
		logger("thepiratebay", url)

		z = re.findall(r'(?s)<div class="detName">(.*?)<\/center>', content)
		re_hash = r'magnet:\?xt=urn:btih:(.*?)&'
		re_seeders = r'<td align="right">([0-9]+)<\/td>'
		re_title = r'<a.*?class="detLink".*?>(.*?)<\/a>'
		hash = None

		if z is None:
			return
		i = 0
		g = 0
		limit = 2 if self.limit is None else self.limit

		for a in z:
			try:
				hash_re = re.search(re_hash, a)
				hash = hash_re.group(1).lower()
				seeders_re = re.search(re_seeders, a)
				self.seeders = seeders_re.group(1) if seeders_re is not None else 0
				if self.seeders < 50:
					continue
				title_re = re.search(re_title, a)
				self.title = title_re.group(1)
			except:
				pass
			if hash is not None:
				get = self.magnet2link(hash)
				if get:
					g += 1
					if g == limit:
						break
			i = i + 1

			if i == 4:
				break
	
	def magnet2link(self, hash):
		url = 'https://webtor.io/' + hash
		try:
			tmp = source_utils.get_link(url)
			re_resource = r'<input.*?name="resource-id" value="(.*?)".*?>'
			re_item = r'<input.*?name="item-id" value="(.*?)".*?>'
			re_cfsr_ = r'window\._CSRF.*?"(.*?)";'
			re_session = r'window\._sessionID.*?"(.*?)";'
			re_filename_ = r'<h1.*?>(.*?)<\/h1>'
			re_resourceid = re.search(re_resource, tmp)
			re_itemid = re.search(re_item, tmp)
			re_cfsr = re.search(re_cfsr_, tmp)
			re_sessionid = re.search(re_session, tmp)
			re_filename = re.search(re_filename_, tmp)
			if re_resourceid is None or re_itemid is None or re_sessionid is None or re_cfsr is None:
				return False
		except:
			return False
		resourceid = re_resourceid.group(1)
		itemid = re_itemid.group(1)
		cfsr = re_cfsr.group(1)
		sessionid = re_sessionid.group(1)
		filename = re_filename.group(1) if re_filename is not None else self.title
		filename = filename.replace('#&nbsp;', '' )
		headers = {
            "st-auth-mode": "cookie",
            "x-csrf-token": cfsr,
            "x-layout": "{{ template \"main\" . }}",
            "x-requested-with": "XMLHttpRequest",
            "x-session-id": sessionid
        }
		link = "https://webtor.io/download-file"
		session = requests.Session()
		response = requests.post(link, data={'resource-id': resourceid, 'item-id': itemid}, headers=headers)
		site = response.text
		re_log = r'data-async-progress-log="(.*)/log".*?>'
		re_url = r'var url.*?"(.*?)";'
		log = re.search(re_log, site)
		tm = 'https://webtor.io' + log.group(1) + '/log'
		tmp = source_utils.get_link(tm)
		url_re = re.search(re_url, tmp)
		if url_re is not None:
			url = url_re.group(1).rstrip('\\').replace('\\u0026', '&').replace("\&", "&")
			#.replace("https:", "http:")
			display_name = 'Seeders: ' + self.seeders
			self.links.add_link(url, self.type, self.imdb, self.time_now, self.scrape_provider, hash, self.season, self.episode, filename, display_name)