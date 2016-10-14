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

def getTMDBbyName(dbtype, title, year):
	data = {}
	tmdbId = ''
	if dbtype!='tv':
		url = baseURL + 'search/' + dbtype + basePARM + "&query=" + title.replace(" ","%20") + "&year=" + year
		xbmc.log(url)
		request = urllib2.Request(url=url, data=json.dumps(data), headers=HEADERS)
		response = json.loads(urllib2.urlopen(request, timeout=3).read())
		if response["total_results"]!=0: tmdbId = response["results"][0]["id"]
	if tmdbId == '':
		url = baseURL + 'search/' + dbtype + basePARM + "&query=" + title.replace(" ","%20")
		request = urllib2.Request(url=url, data=json.dumps(data), headers=HEADERS)
		response = json.loads(urllib2.urlopen(request, timeout=3).read())
		if response["total_results"]!=0: tmdbId = response["results"][0]["id"]
	return tmdbId

def tmdbRated(rating, dbid, dbtype, tmdbId, title):
	if rating>10: rating=0
	if dbtype=='movie':
		if int(dbid)<0 and tmdbId!="":
			request = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"field": "title", "operator": "is", "value": title}, "limits": { "start" : 0, "end": 0 }, "properties" : ["imdbnumber"] }, "id": "1"}
			response = json.loads(xbmc.executeJSONRPC(json.dumps(request, encoding='utf-8')))
			if "result" in response and "movies" in response["result"]:
				movies = response["result"]["movies"][0]
				dbid= movies["movieid"]
		request = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : ' + str(dbid) + ', "userrating": ' + str(rating) + '}}'
	else:
		if int(dbid)<0 and tmdbId!="":
			request = {"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "filter": {"field": "title", "operator": "is", "value": title}, "limits": { "start" : 0, "end": 0 }, "properties" : ["imdbnumber"] }, "id": "1"}
			response = json.loads(xbmc.executeJSONRPC(json.dumps(request, encoding='utf-8')))
			if "result" in response and "tvshows" in response["result"]:
				tvshows = response["result"]["tvshows"][0]
				dbid= movies["tvshowid"]
		request = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetTvShowDetails", "params": {"tvshowid" : ' + str(dbid) + ', "userrating": ' + str(rating) + '}}'
	response = json.loads(xbmc.executeJSONRPC(request))

	url = baseURL + dbtype + '/' + str(tmdbId) + '/rating' + basePARM
	data = {'value': rating}
	request = urllib2.Request(url=url, data=json.dumps(data), headers=HEADERS)
	if rating==0: request.get_method = lambda: 'DELETE'
	response = json.loads(urllib2.urlopen(request, timeout=3).read())
	xbmc.executebuiltin('Notification(' + lang(30010) + ',' + response["status_message"] + ')')

def tmdbWatchFav(list, dbtype, tmdbId, state):
	url = baseURL + 'account/id/'+ list + basePARM
	data = { 'media_type': dbtype, 'media_id': tmdbId, list: state }
	request = urllib2.Request(url=url, data=json.dumps(data), headers=HEADERS)
	response = json.loads(urllib2.urlopen(request, timeout=3).read())
	xbmc.executebuiltin('Notification(' + lang(30010) + ',' + response["status_message"] + ')')

def prompt(dbid, dbtype, tmdbId, title):
	request = urllib2.Request(baseURL + dbtype + '/'+ str(tmdbId) + '/account_states' + basePARM)
	response = json.loads(urllib2.urlopen(request, timeout=3).read())
	if str(response["watchlist"])=='False':
		pList = [lang(30011)]
		watchSts = True
	else:
		pList = [lang(30012)]
		watchSts = False
	if str(response["favorite"])=='False':
		pList.append(lang(30013))
		favSts = True
	else:
		pList.append(lang(30014))
		favSts = False
	if str(response["rated"])!='False': pList.append(lang(30015))
	for i in reversed(range(1, 11)):
		pList.append(str(i)) 
	sel = xbmcgui.Dialog().select(lang(30010)+" - "+title, pList)
	if sel == -1: return
	elif sel == 0:
		tmdbWatchFav("watchlist", dbtype, tmdbId, watchSts)
	elif sel == 1:
		tmdbWatchFav("favorite", dbtype, tmdbId, favSts)
	else:
		if lang(30015)==pList[sel]:
			rating = 0
		else:
			rating = int(pList[sel])
		tmdbRated(rating, dbid, dbtype, tmdbId, title)

def main():
	dbid=xbmc.getInfoLabel('ListItem.DBID')
	dbtype = xbmc.getInfoLabel('ListItem.DBTYPE')
	IMDBNumber = xbmc.getInfoLabel('ListItem.IMDBNumber')
	if dbtype=='tvshow': dbtype='tv'

	tit = xbmc.getInfoLabel('ListItem.Title')
	if (tit==""): tit = xbmc.getInfoLabel('ListItem.Label')

	
	tmdbId = xbmc.getInfoLabel('ListItem.Top250');
	if str(tmdbId) == '':
		if str(IMDBNumber) == '':
			tmdbId = getTMDBbyName(dbtype, tit, xbmc.getInfoLabel('ListItem.Year'))
		else:
			tmdbId = getTMDBbyId(dbtype, IMDBNumber)
	
	if str(tmdbId) == '':
		xbmc.executebuiltin('Notification(' + lang(30010) + ',' + lang(30017) + ')')
	else:
		prompt(dbid, dbtype, tmdbId, tit.decode("utf-8"))

if __name__ == '__main__':
	if addon.getSetting('session_id')=='':
		if getSession() == True: 
			basePARM = basePARM + '&session_id=' + addon.getSetting('session_id')
			main()
		else:
			xbmc.executebuiltin('Notification(' + lang(30016) + ',)')
			xbmcaddon.Addon().openSettings() 
	else:
		basePARM = basePARM + '&session_id=' + addon.getSetting('session_id')
		main()
	