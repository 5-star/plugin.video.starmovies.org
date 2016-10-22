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

def jsonrpc(query):
	return json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))

def setUrl(pQuery):
	return sys.argv[0] + '?' + urllib.urlencode(pQuery)

def getRequest(url):
	request = urllib2.Request(url)
	response = json.load(urllib2.urlopen(request))
	return response
		
def synch(listType, videoType):
	if videoType=="M":
		query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetMovies','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded', 'file'] } }
		movies = jsonrpc(query)['result'].get("movies", [])
	else:
		query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetTvShows','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded', 'file'] } }
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
			if (listType=="watched"): url = url + "&date=" + str(movie["lastplayed"])[:10] + "&link=" + urllib.quote_plus(movie["file"].encode('utf-8'))
			if (listType=="collection"): url = url + "&date=" + str(movie["dateadded"])[:10] + "&link="
			if (listType=="rated"): url = url + "&date=" + "&file="
			try:
				request = urllib2.Request(url)
				response = urllib2.urlopen(request).read()
			except:
				xbmc.log(url.encode("utf-8"),3)

addon = xbmcaddon.Addon("plugin.video.5star_movies")
synch(sys.argv[1], sys.argv[2])
xbmc.executebuiltin('Notification(Synch completed,'+sys.argv[1]+')')
