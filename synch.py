# -*- coding: utf-8 -*-
import sys, os, re
import json
import time
import ssl
import xbmc
import xbmcplugin
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory

try:
    import urllib.request
    from urllib.parse import parse_qs, urlencode, quote, unquote
    python="3"
except ImportError:
    import urllib2
    from urllib import urlencode, quote, unquote
    python="2"

addon = xbmcaddon.Addon("plugin.video.starmovies.org")

def getRequest2(url):
    try:
        context = ssl._create_unverified_context()
        request = urllib2.Request(url)
        response = urllib2.urlopen(request, context=context)
        return response
    except:
        pass

def getRequest3(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            return response
    except:
        pass

def jsonrpc(query):
    return json.loads(xbmc.executeJSONRPC(json.dumps(query)))

def jsonrpc2(query):
    return xbmc.executeJSONRPC(json.dumps(query))

def setUrl(pQuery):
    return sys.argv[0] + '?' + urlencode(pQuery)

def synchCollection(videoType):
    if videoType=="M":
        query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetMovies','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded', 'file'] } }
        movies = "[" + jsonrpc2(query) + "]"
    else:
        query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetTvShows','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded', 'file'] } }
        movies = "[" + jsonrpc2(query) + "]"
    usr = addon.getSetting('usr')
    pwd = addon.getSetting('pwd')
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
    query_args = {'videoType': videoType, 'usr': quote(usr), 'pwd': quote(pwd), 'json': movies}
    url = "https://www.starmovies.org/WebService.asmx/synchCollection"
    try:
        if python=="3":
            data = urllib.parse.urlencode(query_args).encode("utf-8")
            req = urllib.request.Request(url)
            response=urllib.request.urlopen(req, data=data)
            xbmc.log(str(response.read()), 3)
            ####xbmc.executebuiltin('Notification(Synch completed,'+response.read()+')')
        else:
            data = urlencode(query_args)
            context = ssl._create_unverified_context()
            request = urllib2.Request("https://www.starmovies.org/WebService.asmx/synchCollection", data)
            response = urllib2.urlopen(request, context=context)
            xbmc.executebuiltin('Notification(Synch completed,'+response.read()+')')
    except urllib.error.HTTPError as error:
        xbmc.executebuiltin('Notification(ERROR:,'+error.read()+')')

def synch(listType, videoType):
    if videoType=="M":
        query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetMovies','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded', 'file'] } }
        movies = jsonrpc(query)['result'].get("movies", [])
    else:
        query = {'jsonrpc': '2.0','id': 0,'method': 'VideoLibrary.GetTvShows','params': {'properties': ['imdbnumber', 'userrating', 'playcount', 'lastplayed', 'dateadded', 'file'] } }
        movies = jsonrpc(query)['result'].get("tvshows", [])

    for movie in movies:
        if movie["imdbnumber"]!="" and (listType=="collection" or (listType=="watched" and movie["playcount"]>0) or (listType=="rated" and movie["userrating"]>0)):
            url = "https://www.starmovies.org/WebService.asmx/synchList?listType=" + listType + "&videoType=" + videoType
            url = url + "&usr=" + quote(addon.getSetting('usr'))
            url = url + "&pwd=" + addon.getSetting('pwd')
            if videoType=="M":
                url = url + "&kodiId=" + str(movie["movieid"]) 
            else:
                url = url + "&kodiId=" + str(movie["tvshowid"]) 
            url = url + "&externalId=" + movie["imdbnumber"] 
            url = url + "&rating=" + str(movie["userrating"])
            plDate=str(movie["lastplayed"])[:10]
            if plDate=="" : plDate="2000-01-01" 
            addDate=str(movie["dateadded"])[:10]
            if addDate=="": addDate="2000-01-01" 
            if (listType=="watched"): url = url + "&date=" + plDate + "&link=" + urllib.quote_plus(movie["file"])
            if (listType=="collection"): url = url + "&date=" + addDate + "&link="
            if (listType=="rated"): url = url + "&date=" + "&link="
            if python=="3":
                response = getRequest3(url)
            else:
                response = getRequest2(url)
            xbmc.log("=============================================================================",3)
            xbmc.log(url,3)
            xbmc.log(str(response),3)

if len(sys.argv)>1:
    addon = xbmcaddon.Addon("plugin.video.starmovies.org")
    xbmc.executebuiltin('Notification(Synch started,'+sys.argv[1]+')')
    if sys.argv[1]=="collection":
        synchCollection(sys.argv[2])
    else:
        synch(sys.argv[1], sys.argv[2])
    xbmc.executebuiltin('Notification(Synch completed,'+sys.argv[1]+')')
