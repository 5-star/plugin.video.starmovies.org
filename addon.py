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
		
def list_items(listType, videoType, order):
	xbmcplugin.setContent(addon_handle, "movies")
	url = "http://www.5star-movies.com/WebService.asmx/getList?listType="+listType+"&videoType="+videoType+"&order="+order+"&pg=0&pgSize=5000&usr="+addon.getSetting('usr')+"&pwd="+addon.getSetting('pwd')
	for item in getRequest(url):
		if listType=="watched" and videoType=="S" and item["season"]!=None:
			title="s"+str(item["episode"])+"e"+str(item["season"])+" "+str(item["episodetitle"])+" - "+item["title"]
		else: title=item["title"]
		infolabels={'Top250': item['wid'], 'title': title, 'year': item['release_date'], 'rating': item['userrating'], "mediatype": 'movie'}
		li = ListItem(title)
		li.setInfo('video', infolabels)
		li.setArt({ "poster" : item["poster"].strip() })
		li.setArt({ "thumbnail" : item["poster"].strip() })
		li.setArt({ "fanart" : item["backdrop"].strip() })		
		li.setProperty('IsPlayable', 'true')
		li.setArt({ "poster" : "http://image.tmdb.org/t/p/w500"+item['poster']})
		addDirectoryItem(addon_handle, item['link'], li, isFolder=False)
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
		addDirectoryItem(addon_handle, setUrl({'menu': 'watchedMovies'}), ListItem(lang(30018), iconImage=imgPath+'/resources/movies.png'), True)
		addDirectoryItem(addon_handle, setUrl({'menu': 'watchedTv'}), ListItem(lang(30019), iconImage=imgPath+'/resources/episodes.png'), True)
		endOfDirectory(addon_handle)
	elif menu == 'ratedMovies':
		list_items("rated","M", "usrrating")
	elif menu == 'ratedTv':
		list_items("rated","S", "usrrating")
	elif menu == 'watchlistMovies':
		list_items("watchlist","M", "date")
	elif menu == 'watchlistTv':
		list_items("watchlist","S", "date")
	elif menu == 'favoriteMovies':
		list_items("favorites","M", "date")
	elif menu == 'favoriteTv':
		list_items("favorites","S", "date")
	elif menu == 'watchedMovies':
		list_items("watched","M", "watched")
	elif menu == 'watchedTv':
		list_items("watched","S", "watched")

if addon.getSetting('usr')=='' or addon.getSetting('pwd')=='':
	xbmc.executebuiltin('Notification(' + lang(30016) + ',)')
	xbmcaddon.Addon().openSettings() 
else:
	Main()
	