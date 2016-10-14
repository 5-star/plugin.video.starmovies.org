# -*- coding: utf-8 -*-
import sys, os, re
import json
import time
import urllib, urllib2
import urlparse
import xbmcplugin
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
menu = args.get('menu', ['None'])[0]
lang = addon.getLocalizedString

def jsonrpc(query):
	return json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))

def setUrl(pQuery):
	return sys.argv[0] + '?' + urllib.urlencode(pQuery)

def getRequest(url):
	request = urllib2.Request(url)
	response = json.load(urllib2.urlopen(request))
	return response
		
def list_items(listType, videoType):
	xbmcplugin.setContent(addon_handle, "movies")
	url = "http://www.5star-movies.com/WebService.asmx/getList?listType="+listType+"&videoType="+videoType+"&pg=0&pgSize=5000&usr="+addon.getSetting('usr')+"&pwd="+addon.getSetting('pwd')
	for item in getRequest(url):
		title = item['title']
		infolabels={'Top250': item[listType], 'title': item['title'], 'year': item['release_date'], 'rating': item['userrating'], "mediatype": 'movie'}
		li = ListItem(item['title'])
		li.setInfo('video', infolabels)
		li.setProperty('IsPlayable', 'true')
		li.setArt({ "poster" : "http://image.tmdb.org/t/p/w500"+item['poster']})
		addDirectoryItem(addon_handle, url, li, isFolder=False)
	endOfDirectory(addon_handle)

def synch(listType, videoType):
	if videoType=="M":
		query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetMovies','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded'] } }
		movies = jsonrpc(query)['result'].get("movies", [])
	else:
		query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetTvShows','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded'] } }
		movies = jsonrpc(query)['result'].get("tvshows", [])
	for movie in movies:
		if movie["imdbnumber"]!="" and (listType=="collection" or (listType=="watched" and movie["playcount"]>0) or (listType=="rated" and movie["userrating"]>0)):
			url = "http://www.5star-movies.com/WebService.asmx/synchList?listType=" + listType + "&videoType=" + videoType
			url = url + "&usr=" + urllib.quote(addon.getSetting('tmdb_user').encode("utf-8"))
			url = url + "&pwd=" + addon.getSetting('tmdb_password')
			if videoType=="M":
				url = url + "&kodiId=" + str(movie["movieid"]) 
			else:
				url = url + "&kodiId=" + str(movie["tvshowid"]) 
			url = url + "&externalId=" + movie["imdbnumber"] 
			url = url + "&rating=" + str(movie["userrating"])
			if (listType=="watched"): url = url + "&date=" + str(movie["lastplayed"])[:10]
			if (listType=="collection"): url = url + "&date=" + str(movie["dateadded"])[:10]
			if (listType=="rated"): url = url + "&date="
			try:
				request = urllib2.Request(url)
				response = urllib2.urlopen(request).read()
			except:
				xbmc.log(url,3)

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
		addDirectoryItem(addon_handle, "", ListItem(""), False)
		addDirectoryItem(addon_handle, setUrl({'menu': 'synch', 'type': 'collection'}), ListItem("Synch Collection"), True)
		addDirectoryItem(addon_handle, setUrl({'menu': "synch", 'type': 'rated'}), ListItem("Synch Rated Movies and TV"), True)
		addDirectoryItem(addon_handle, setUrl({'menu': "synch", 'type': 'watched'}), ListItem("Synch Watched Movies and TV"), True)
		endOfDirectory(addon_handle)
	elif menu == 'ratedMovies':
		list_items("rated","M")
	elif menu == 'ratedTv':
		list_items("rated","S")
	elif menu == 'watchlistMovies':
		list_items("watchlist","M")
	elif menu == 'watchlistTv':
		list_items("watchlist","S")
	elif menu == 'favoriteMovies':
		list_items("favorites","M")
	elif menu == 'favoriteTv':
		list_items("favorites","S")
	elif menu == 'synch':
		listType = args.get('type', None)[0]
		synch(listType, "M")
		synch(listType, "S")
		xbmc.executebuiltin('Notification(Synched completed,)')

if addon.getSetting('usr')=='' or addon.getSetting('pwd')=='':
	xbmc.executebuiltin('Notification(' + lang(30016) + ',)')
	xbmcaddon.Addon().openSettings() 
else:
	Main()
	