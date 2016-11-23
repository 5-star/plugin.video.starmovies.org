# -*- coding: utf-8 -*-
import os
import sys
import json
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import urllib
import urllib2

addon = xbmcaddon.Addon()
lang = addon.getLocalizedString
USR=addon.getSetting('usr')
PWD=addon.getSetting('pwd')

baseURL = 'http://api.themoviedb.org/3/'
basePARM = '?api_key=fb77526161109488c45abd0f75960a0f'
HEADERS = {'Accept': 'application/json','Content-Type': 'application/json'}

def getTMDBbyId(dbtype, IMDBNumber):
	tmdbId = ''
	if dbtype=='tv':
		request = urllib2.Request(baseURL + 'find/' + IMDBNumber + basePARM + '&external_source=tvdb_id')
		response = json.loads(urllib2.urlopen(request, timeout=3).read())
		tmdbId = response["tv_results"][0]["id"]
	else:
		request = urllib2.Request(baseURL + 'find/' + IMDBNumber + basePARM + '&external_source=imdb_id')
		response = json.loads(urllib2.urlopen(request, timeout=3).read())
		tmdbId = response["movie_results"][0]["id"]
	return tmdbId

def getTMDBbyName(dbType, title, year):
	data = {}
	tmdbId = ''
	if dbType=="tvshow": dbType="tv"
	if dbType!='tv':
		url = baseURL + 'search/' + dbType + basePARM + "&query=" + title.replace(" ","%20") + "&year=" + year
		request = urllib2.Request(url=url, data=json.dumps(data), headers=HEADERS)
		response = json.loads(urllib2.urlopen(request, timeout=3).read())
		if response["total_results"]!=0: tmdbId = response["results"][0]["id"]
	if tmdbId == '':
		url = baseURL + 'search/' + dbType + basePARM + "&query=" + title.replace(" ","%20")
		request = urllib2.Request(url=url, data=json.dumps(data), headers=HEADERS)
		response = json.loads(urllib2.urlopen(request, timeout=3).read())
		if response["total_results"]!=0: tmdbId = response["results"][0]["id"]
	return tmdbId

def api(func, lstType, rating, videoType, tmdbId, kodiId, imdbId):
	url = 'http://www.5star-movies.com/WebService.asmx/kodiMark?func='+ func + '&lstType=' + lstType +'&videoType=' + videoType + '&tmdbId=' + str(tmdbId) + '&imdbId='+imdbId+'&tvdbId=0&kodiId='+str(kodiId)+'&rating=' + str(rating) + '&usr='+USR+'&pwd='+PWD
	request = urllib2.Request(url=url)
	response = urllib2.urlopen(request, timeout=3).read()
	xbmc.executebuiltin('Notification(' + lang(30010) + ',' + response + ')')
	
def prompt(dbid, dbType, tmdbId, title, imdbId):
	if dbType=="tvshow": videoType="S"
	else: videoType="M"
	url="http://www.5star-movies.com/Webservice.asmx/getStates?videoType="+videoType+"&tmdbId="+str(tmdbId)+"&imdbId="+imdbId+"&usr="+USR+"&pwd="+PWD
	request = urllib2.Request(url)
	response = json.loads(urllib2.urlopen(request, timeout=3).read())
	if str(response["watchlist"])=='None':
		pList = [lang(30011)]
		func = "Mark"
	else:
		pList = [lang(30012)]
		func = "unMark"
	if str(response["favorites"])=='None':
		pList.append(lang(30013))
		func = "Mark"
	else:
		pList.append(lang(30014))
		func = "unMark"
	if str(response["watched"])=='None':
		pList.append(lang(30022))
		func = "Mark"
	else:
		pList.append(lang(30023))
		func = "unMark"
	if str(response["rated"])!='None': pList.append(lang(30015))
	for i in reversed(range(1, 11)):
		pList.append(str(i))
	sel = xbmcgui.Dialog().select(lang(30010)+" - "+title, pList)
	# Handle Selection
	if sel == -1: return
	elif sel == 0:
		api(func, "watchlist", 0, videoType, tmdbId, dbid, imdbId)
	elif sel == 1:
		api(func, "favorites", 0, videoType, tmdbId, dbid, imdbId)
	elif sel == 2:
		api(func, "watched", 0, videoType, tmdbId, dbid, imdbId)
	else:
		if lang(30015)==pList[sel]:
			rating = 0
		else:
			rating = int(pList[sel])
		if rating==0: func="unMark"
		else: func="Mark"
		api(func, "rated", rating, videoType, tmdbId, dbid, imdbId)

# Prepares and shows the selection list
def main():
	dbid=xbmc.getInfoLabel('ListItem.DBID')
	dbType = xbmc.getInfoLabel('ListItem.DBTYPE')
	if dbType!="tvshow": IMDBNumber = xbmc.getInfoLabel('ListItem.IMDBNumber')
	else: IMDBNumber = ""
	tit = xbmc.getInfoLabel('ListItem.Title')
	if (tit==""): tit = xbmc.getInfoLabel('ListItem.Label')

	tmdbId = xbmc.getInfoLabel('ListItem.Top250');
	if str(tmdbId) == '':
		if str(IMDBNumber) == '':
			tmdbId = getTMDBbyName(dbType, tit, xbmc.getInfoLabel('ListItem.Year'))
		else:
			tmdbId = getTMDBbyId(dbType, IMDBNumber)

	if str(tmdbId) == '':
		xbmc.executebuiltin('Notification(' + lang(30010) + ',' + lang(30017) + ')') # Title not found
	else:
		prompt(dbid, dbType, tmdbId, tit.decode("utf-8"), IMDBNumber)

if __name__ == '__main__':
	if USR == '' or PWD == '' :
		xbmc.executebuiltin('Notification(' + lang(30016) + ',)') # Set user and passsword
		xbmcaddon.Addon().openSettings() 
	else:
		main()
