# -*- coding: utf-8 -*-
import sys, os, re
import json
import time
import ssl
import xbmcplugin
import xbmcaddon
import xbmcgui
import xbmcvfs
from xbmcplugin import addDirectoryItem, endOfDirectory

try:
    from urllib.parse import parse_qs, urlencode, quote, unquote
    import urllib.request
    python="3"
except ImportError:
    from urllib import urlencode, quote, unquote
    from urlparse import parse_qs
    import urllib2
    python="2"

addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
args = parse_qs(sys.argv[2][1:])
menu = args.get('menu', ['None'])[0]
lang = addon.getLocalizedString

def setUrl(pQuery):
    return sys.argv[0] + '?' + urlencode(pQuery)

def getRequest2(url):
    try:
        context = ssl._create_unverified_context()
        request = urllib2.Request(url)
        response = json.load(urllib2.urlopen(request, context=context))
        return response
    except Exception as e:
        xbmc.log(str(e),3)

def getRequest3(url):
    try:
        request = urllib.request.Request(url)
        response = json.load(urllib.request.urlopen(request))
        return response
    except Exception as e:
        xbmc.log(str(e),3)
        
def list_items(listType, videoType, order):
    if videoType=="S":
        dbType="tvshow"
        xbmcplugin.setContent(addon_handle, "tvshows")
    else:
        dbType="movie"
    xbmcplugin.setContent(addon_handle, "movies")	
    url = "https://www.starmovies.org/WebService.asmx/getList?listType="+listType+"&videoType="+videoType+"&order="+order+"&pg=0&pgSize=5000&usr="+addon.getSetting('usr')+"&pwd="+addon.getSetting('pwd')
    if python=="3":
        items = getRequest3(url)
    else:
        items = getRequest2(url)
    if items==None:
        li = xbmcgui.ListItem("Check settings user or password")
        addDirectoryItem(addon_handle, "", li, isFolder=False)
    else:
        for item in items:
            if listType=="watched" and videoType=="S" and item["season"]!=None:
                title=item["title"]+" - "+"s"+str(item["episode"])+"e"+str(item["season"])+" "+str(item["episodetitle"])
            else: title=item["title"]
            infolabels={'IMDBNumber': item['imdbId'], 'title': title, 'year': item['release_date'], 'rating': item['userrating'], "mediatype": dbType}
            li = xbmcgui.ListItem(title)
            li.setInfo('video', infolabels)
            if item["poster"]!=None:
                li.setArt({ "poster" : item["poster"].strip() })
                li.setArt({ "thumbnail" : item["poster"].strip() })
                li.setArt({ "poster" : item['poster']})
            if item["backdrop"]!=None:
                li.setArt({ "fanart" : item["backdrop"].strip() })		
            li.setProperty('IsPlayable', 'true')
            link=item['link']
            if link==None: link="noLink"
            addDirectoryItem(addon_handle, quote(link), li, isFolder=False)
    endOfDirectory(addon_handle)

def Main():
    if menu == 'None':
        xbmcplugin.setContent(addon_handle, "menu")
        imgPath=xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
        li = xbmcgui.ListItem(lang(30004))
        li.setArt({'icon':imgPath+'/resources/movies.png'})
        addDirectoryItem(addon_handle, setUrl({'menu': 'ratedMovies'}), li, True)
        li = xbmcgui.ListItem(lang(30005))
        li.setArt({'icon':imgPath+'/resources/episodes.png'})
        addDirectoryItem(addon_handle, setUrl({'menu': 'ratedTv'}), li, True)
        li = xbmcgui.ListItem(lang(30007))
        li.setArt({'icon':imgPath+'/resources/movies.png'})
        addDirectoryItem(addon_handle, setUrl({'menu': 'watchlistMovies'}), li, True)
        li = xbmcgui.ListItem(lang(30007))
        li.setArt({'icon':imgPath+'/resources/episodes.png'})
        addDirectoryItem(addon_handle, setUrl({'menu': 'watchlistTv'}), li, True)
        li = xbmcgui.ListItem(lang(30008))
        li.setArt({'icon':imgPath+'/resources/movies.png'})
        addDirectoryItem(addon_handle, setUrl({'menu': 'favoriteMovies'}), li, True)
        li = xbmcgui.ListItem(lang(30009))
        li.setArt({'icon':imgPath+'/resources/episodes.png'})
        addDirectoryItem(addon_handle, setUrl({'menu': 'favoriteTv'}), li, True)
        li = xbmcgui.ListItem(lang(30018))
        li.setArt({'icon':imgPath+'/resources/movies.png'})
        addDirectoryItem(addon_handle, setUrl({'menu': 'watchedMovies'}), li, True)
        li = xbmcgui.ListItem(lang(30019))
        li.setArt({'icon':imgPath+'/resources/episodes.png'})
        addDirectoryItem(addon_handle, setUrl({'menu': 'watchedTv'}), li, True)
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
