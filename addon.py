import sys, os, re
import json
import time
import urllib
import urllib2
import urlparse
import xbmcplugin
import xbmcaddon
import ctypes
from copy import deepcopy
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory
import urlresolver

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
menu = args.get('menu', ['None'])[0]
lang = addon.getLocalizedString
baseURL = 'http://api.themoviedb.org/3/'
basePARM = '?api_key=fb77526161109488c45abd0f75960a0f'
HEADERS = {'Accept': 'application/json','Content-Type': 'application/json'}

def getRequest(url, parm):
	request = urllib2.Request(baseURL+url+basePARM+parm)
	response = json.load(urllib2.urlopen(request))
	return response

def getSession():
	try:
		sts = False
		rsp = getRequest('authentication/token/new','')
		if 'success' in rsp and rsp['success']==True	:
			rsp = getRequest('authentication/token/validate_with_login','&request_token='+rsp['request_token']+'&username='+addon.getSetting('tmdb_user')+'&password='+addon.getSetting('tmdb_password'))
			if 'success' in rsp and rsp['success']==True:
				rsp = getRequest('authentication/session/new','&request_token='+rsp['request_token'])
				if 'success' in rsp and rsp['success']==True:
					addon.setSetting('session_id', rsp['session_id'])
					sts = True
		return sts
	except:
		return False
	
def setUrl(pQuery):
	return sys.argv[0] + '?' + urllib.urlencode(pQuery)

def jsonrpc(query):
	return json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))

def get_tmdbid(imdbid):
	request = urllib2.Request(baseURL + "movie/" + str(imdbid)+basePARM)
	try:
		response = json.load(urllib2.urlopen(request))
		return response["id"]
	except:
		return None

def get_imdbid(tmdbid):
	request = urllib2.Request(baseURL + "movie/" + str(tmdbid)+basePARM)
	response = json.load(urllib2.urlopen(request))
	return response["imdb_id"]

def get_xbmc_movies():
	query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetMovies','params': {'properties': ['imdbnumber', 'file', 'userrating', 'title'] } }
	movies = jsonrpc(query)['result'].get("movies", [])
	kodiMovie = []
	for movie in movies:
		kodiMovie.append([movie["imdbnumber"], movie["file"], movie["userrating"], movie["title"] ])
	return kodiMovie

def get_xbmc_tv():
	query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetTVShows','params': {'properties': ['imdbnumber', 'file', 'userrating'] } }
	shows = jsonrpc(query)['result'].get("tvshows", [])
	kodiTv = []
	for show in shows:
		kodiTv.append([show["imdbnumber"], show["file"], show["userrating"] ])			
	return kodiTv

def getMultiPage(url, lista):
	request = urllib2.Request(url)
	response = json.load(urllib2.urlopen(request))
	js = []
	if lista:
		results = "items"
		npage = 1
	else:
		results = "results"
		npage = response["total_pages"]
	for item in response[results]:
		js.append(deepcopy(item))
	for p in range(2, npage+1):
		url = url + "&page="+str(p)
		request = urllib2.Request(url)
		response = json.load(urllib2.urlopen(request))
		for item in response[results]:
			js.append(deepcopy(item))
	return js

def list_movies(url, type, lista):
	ur1 = urlresolver.HostedMediaFile(url='http://vodlocker.com/8et8git7xngv')
	ur2 = urlresolver.HostedMediaFile(url='https://r19---sn-aigllndk.googlevideo.com/videoplayback?id=33e92d39f523ae09&itag=37&source=webdrive&begin=0&requiressl=yes&hcs=yes&mm=30&mn=sn-aigllndk&ms=nxu&mv=m&nh=IgpwcjAxLmxocjI1KhgyMDAxOjQ4NjA6MToxOjA6MjFkMTowOjE&pl=32&sc=yes&shardbypass=yes&mime=video/mp4&lmt=1472778731841713&mt=1473189454&ip=2001:8a0:6d08:f01:1878:3ac:9a39:f50c&ipbits=48&expire=1473218524&sparams=ip,ipbits,expire,id,itag,source,requiressl,hcs,mm,mn,ms,mv,nh,pl,sc,shardbypass,mime,lmt&signature=2407A8FC3E8575E2C4BF44FEA13F013E8E76F7B1.735EE88CE86F24CD8DDF63A3633019E4C9832F44&key=ck2', title='bigodes')
	ur3 = urlresolver.HostedMediaFile(url='https://redirector.googlevideo.com/videoplayback?requiressl=yes&id=32263fea983fb2dc&itag=37&source=webdrive&ttl=transient&app=explorer&ip=2a05:840::e098&ipbits=0&expire=1473010466&sparams=requiressl,id,itag,source,ttl,ip,ipbits,expire&signature=757E42C8865EFEBD088899FE66DDC35B73C0B5B6.7602B1003267C3D4918C6C212E224403A583D22F&key=ck2&mm=31&mn=sn-5hne6nls&ms=au&mt=1472995489&mv=u&nh=IgpwcjA0LmFtczE1KgkxMjcuMC4wLjE&pl=48', title='bigodes')
	urr = ur1.resolve()
	if urr==False: urr=""
	urr="plugin://plugin.video.exodus/?action=playItem&title=Jason+Bourne&source=%5B%7B%22debrid%22%3A+%22%22%2C+%22url%22%3A+%22http%3A%2F%2Fmovie4k.to%2FJason-Bourne-watch-movie-7361541.html%22%2C+%22debridonly%22%3A+false%2C+%22direct%22%3A+false%2C+%22label%22%3A+%22359+%7C+%5BB%5DMOVIE4K%5B%2FB%5D+%7C+ALLMYVIDEOS+%22%2C+%22source%22%3A+%22allmyvideos.net%22%2C+%22provider%22%3A+%22Movie4K%22%2C+%22quality%22%3A+%22SD%22%7D%5D"
	xbmc.log("#123 stream_url "+urr,3)
	urr2 = urlresolver.resolve('http://vodlocker.com/8et8git7xngv') 
	xbmc.log("#123 web url "+urr2,3)
	xbmcplugin.setContent(addon_handle, "movies")
	parm = "&sort_by=created_at.desc"
	for item in getMultiPage(baseURL+url+basePARM+parm, lista):
		infolabels={'Top250': item['id'], 'title': item['title'], 'year': item['release_date'], 'rating': item['vote_average'], "mediatype": 'movie'}
		li = ListItem(infolabels['title'])
		li.setInfo('video', infolabels)
		li.setProperty('IsPlayable', 'true')
		if item['poster_path']!=None:
			li.setArt({ "poster" : "http://image.tmdb.org/t/p/w500"+item['poster_path']})
		addDirectoryItem(addon_handle, urr, li, isFolder=False)
	endOfDirectory(addon_handle)

def list_rated_movies(url, type, lista):
	xbmcplugin.setContent(addon_handle, "movies")
	# gets the full list of movies in kodi
	kodiMovie = get_xbmc_movies()
	# for each TMDB movie
	parm = "&sort_by=created_at.desc"
	for item in getMultiPage(baseURL+url+basePARM+parm, lista):
		# TMDB has maximum access per minute, so wait...
		time.sleep(0.05)
		# get the imdb id from TMDB
		request = urllib2.Request(baseURL + "movie/" + str(item['id'])+basePARM)
		response = json.load(urllib2.urlopen(request))
		imdbid = response["imdb_id"]
		url = '-'
		userrating = '*'
		title = item['title']
		# look for the movie on the kodi list of movies
		for km in kodiMovie:
			if imdbid == km[0]:
				url = km[1]
				title = km[3]
				if item['rating']!=km[2]:
					userrating = ' - Rating: Kodi='+str(km[2])+', TMDB='+str(item['rating'])
				else:
					userrating = ''
				km[2]=0
		infolabels={'Top250': item['id'], 'title': title, 'year': item['release_date'], 'rating': item['rating'], "mediatype": 'movie'}
		li = ListItem(title + userrating)
		li.setInfo('video', infolabels)
		li.setProperty('IsPlayable', 'true')
		if userrating == '*':
			userrating = ' - Not on the Library'
			li.setArt({ "poster" : "http://image.tmdb.org/t/p/w500"+item['poster_path']})
		#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
		addDirectoryItem(addon_handle, url, li, isFolder=False)
	# rated movies in kodi which does not exist in tmdb
	for km in kodiMovie:
		if km[2]!=0:
			infolabels={'title': km[3], 'rating': km[2], "mediatype": 'movie'}
			li = ListItem(km[3]+' - Rating '+str(km[2]) + ' not in TMDB')
			addDirectoryItem(addon_handle, km[1], li, isFolder=False)
	endOfDirectory(addon_handle)
	
def list_tv(url, type, lista):
	xbmcplugin.setContent(addon_handle, "tvshows")
	parm = "&sort_by=created_at.desc"
	for item in getMultiPage(baseURL+url+basePARM+parm, lista):
		infolabels={'Top250': item['id'], 'name': item['name'], 'year': item['first_air_date'], 'rating': item['vote_average'], "mediatype": 'tvshow'}
		li = ListItem(infolabels['name'])
		li.setInfo('video', infolabels)
		li.setProperty('IsPlayable', 'true')
		li.setArt({ "poster" : "http://image.tmdb.org/t/p/w500"+item['poster_path']})
		addDirectoryItem(addon_handle, url, li, isFolder=False)
	endOfDirectory(addon_handle)

def list_rated_tv(url, type, lista):
	xbmcplugin.setContent(addon_handle, "tvshows")
	# gets the full list of shows in kodi
	kodiTv = get_xbmc_tv()
	# for each TMDB show
	parm = "&sort_by=created_at.desc"
	for item in getMultiPage(baseURL+url+basePARM+parm, lista):
		# TMDB has maximum access per minute, so wait...
		time.sleep(0.05)
		# get the imdb id from TMDB
		request = urllib2.Request(baseURL + "tv/" + str(item['id'])+"/external_ids"+basePARM)
		response = json.load(urllib2.urlopen(request))
		tvdbid = response["tvdb_id"]
		url = '-'
		userrating = ' - Not on the Library'
		# look for the show on the kodi list of shows
		for tv in kodiTv:
			if str(tvdbid) == tv[0]:
				url = tv[1]
				if item['rating']!=tv[2]:
					userrating = ' Rating: Kodi='+str(tv[2])+', TMDB='+str(item['rating'])
				else:
					userrating = ''
				tv[2]=0
		infolabels={'Top250': item['id'], 'name': item['name'], 'year': item['first_air_date'], 'rating': item['rating'], "mediatype": 'tvshow'}
		li = ListItem(item['name'] + userrating)
		li.setInfo('video', infolabels)
		li.setProperty('IsPlayable', 'true')
		li.setArt({ "poster" : "http://image.tmdb.org/t/p/w500"+item['poster_path']})
		addDirectoryItem(addon_handle, url, li, isFolder=False)
	# rated movies in kodi which does not exist in tmdb
	for tv in kodiTv:
		if tv[2]!=0:
			infolabels={'title': tv[3], 'rating': tv[2], "mediatype": 'tvshow'}
			li = ListItem(tv[3]+' - Rating: Kodi='+str(tv[2]))
			addDirectoryItem(addon_handle, tv[1], li, isFolder=False)
	endOfDirectory(addon_handle)

def Main():
	if menu is 'None':
		xbmcplugin.setContent(addon_handle, "menu")
		imgPath=xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')).decode('utf-8')
		addDirectoryItem(addon_handle, setUrl({'menu': 'ratedMovies'}), ListItem(lang(30004), iconImage=imgPath+'/resources/movies.png'), True)
		addDirectoryItem(addon_handle, setUrl({'menu': 'ratedTv'}), ListItem(lang(30005), iconImage=imgPath+'/resources/episodes.png'), True)
		addDirectoryItem(addon_handle, setUrl({'menu': 'watchlistMovies'}), ListItem(lang(30006), iconImage=imgPath+'/resources/movies.png'), True)
		addDirectoryItem(addon_handle, setUrl({'menu': 'watchlistTv'}), ListItem(lang(30007), iconImage=imgPath+'/resources/episodes.png'), True)
		addDirectoryItem(addon_handle, setUrl({'menu': 'favoriteMovies'}), ListItem(lang(30008), iconImage=imgPath+'/resources/movies.png'), True)
		addDirectoryItem(addon_handle, setUrl({'menu': 'favoriteTv'}), ListItem(lang(30009), iconImage=imgPath+'/resources/episodes.png'), True)
		for item in getMultiPage(baseURL+"account/id/lists"+basePARM, False):
			li = ListItem(item['name'], iconImage=imgPath+'/resources/movies.png')
			li.addContextMenuItems([('Synch with TMDB',"XBMC.RunPlugin(" + sys.argv[0] + "?menu=KodiTv&id=" + str(item['id']) + ")")])
			addDirectoryItem(addon_handle, setUrl({'menu': item['id']}), li, True)
		endOfDirectory(addon_handle)
	elif menu == 'ratedMovies':
		list_rated_movies("account/id/rated/movies","movies", False)
	elif menu == 'ratedTv':
		list_rated_tv("account/id/rated/tv","episodes", False)
	elif menu == 'watchlistMovies':
		list_movies("account/id/watchlist/movies","movies", False)
	elif menu == 'watchlistTv':
		list_tv("account/id/watchlist/tv","episodes", False)
	elif menu == 'favoriteMovies':
		list_movies("account/id/favorite/movies","movies", False)
	elif menu == 'favoriteTv':
		list_tv("account/id/favorite/tv","episodes", False)
	elif menu == 'KodiRated':
		listId = args.get('id', None)[0]
	elif menu == 'KodiMovie':
		listId = args.get('id', None)[0]
		kodiMovie = get_xbmc_movies()
		tmdbMovie = getMultiPage(baseURL+"list/"+listId+basePARM, True)
		for item in tmdbMovie:
			imdbid = get_imdbid(item['id'])
			time.sleep(1)
			for km in kodiMovie:
				if imdbid == km[0]:
					km[0]=''
					item['id']=0
		for km in kodiMovie:
			if km[0]!='':
				time.sleep(1)
				tmdbid = get_tmdbid(km[0])
				if tmdbid != None:
					url = baseURL + 'list/' + listId + '/add_item' + basePARM
					data = { 'media_id': tmdbid }
					request = urllib2.Request(url=url, data=json.dumps(data), headers=HEADERS)
					response = json.loads(urllib2.urlopen(request, timeout=3).read())
	else:
		list_movies("list/"+menu,"movies", True)

if addon.getSetting('session_id')=='':
	if getSession() == True: 
		basePARM = basePARM + '&session_id=' + addon.getSetting('session_id')
		Main()
	else:
		xbmc.executebuiltin('Notification(' + lang(30016) + ',)')
		xbmcaddon.Addon().openSettings() 
else:
	basePARM = basePARM + '&session_id=' + addon.getSetting('session_id')
	Main()
