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

addon = xbmcaddon.Addon("plugin.video.starmovies.org")

def jsonrpc(query):
	return json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))

def jsonrpc2(query):
	return xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8'))

def setUrl(pQuery):
	return sys.argv[0] + '?' + urllib.urlencode(pQuery)
 
def synchCollection(videoType):
	if videoType=="M":
		query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetMovies','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded', 'file'] } }
		movies = "[" + jsonrpc2(query) + "]"
	else:
		query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetTvShows','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded', 'file'] } }
		movies = "[" + jsonrpc2(query) + "]"
	usr = addon.getSetting('tmdb_user').encode("utf-8")
	pwd = addon.getSetting('tmdb_password').encode("utf-8")
	movies = movies.replace("ã","a")
	movies = movies.replace("â","a")
	movies = movies.replace("ä","a")
	movies = movies.replace("á","a")
	movies = movies.replace("à","a")
	movies = movies.replace("â","a")
	movies = movies.replace("è","e")
	movies = movies.replace("é","e")
	movies = movies.replace("ê","e")
	movies = movies.replace("í","i")
	movies = movies.replace("ó","o")
	movies = movies.replace("ò","o")
	movies = movies.replace("ô","o")
	movies = movies.replace("õ","o")
	movies = movies.replace("ô","o")
	movies = movies.replace("ù","u")
	movies = movies.replace("ú","u")
	movies = movies.replace("ç","c")
	movies = movies.replace("³","")
	movies = movies.replace("Á","A")
	movies = movies.replace("À","A")
	movies = movies.replace("Ê","E")
	movies = movies.replace("È","E")
	movies = movies.replace("É","E")
	movies = movies.replace("î","i")
	movies = movies.replace("Ô","O")
	movies = movies.replace("","")
	movies = movies.replace("–","")
	movies = movies.replace("´","'")
	movies = movies.replace("ñ","n")
	movies = movies.replace("½","")
	movies = movies.replace("ø","")
	data = {'videoType': videoType, 'usr': urllib.quote(usr), 'pwd': urllib.quote(pwd), 'json': movies}
	try:
		request = urllib2.Request("https://www.starmovies.org/WebService.asmx/synchCollection")
		request.add_header('Content-Type','application/json')
		response = urllib2.urlopen(request, str(data))
	except urllib2.HTTPError, error:
		xbmc.log(error.read(),3)

class ScanMonitor(xbmc.Monitor):
	def __init__(self, *args, **kwargs):
		xbmc.Monitor.__init__(self)

	def onCleanFinished(self, database):
		synchCollection("S")
		synchCollection("M")

	def onScanFinished(self, database):
		synchCollection("S")
		synchCollection("M")

scan_monitor = ScanMonitor()

while not xbmc.abortRequested:
	xbmc.sleep(1000)

del scan_monitor
