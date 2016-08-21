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
basePARM = '?api_key=fb77526161109488c45abd0f75960a0f&session_id=' + addon.getSetting('session_id')
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

def getTMDBbyName(dbtype, title, year):
	data = {}
	tmdbId = ''
	if dbtype!='tv':
		url = baseURL + 'search/' + dbtype + basePARM + "&query=" + title.replace(" ","%20") + "&year=" + year
		request = urllib2.Request(url=url, data=json.dumps(data), headers=HEADERS)
		response = json.loads(urllib2.urlopen(request, timeout=3).read())
		if response["total_results"]!=0: tmdbId = response["results"][0]["id"]
	if tmdbId == '':
		url = baseURL + 'search/' + dbtype + basePARM + "&query=" + title.replace(" ","%20")
		request = urllib2.Request(url=url, data=json.dumps(data), headers=HEADERS)
		response = json.loads(urllib2.urlopen(request, timeout=3).read())
		if response["total_results"]!=0: tmdbId = response["results"][0]["id"]
	return tmdbId

def tmdbRated(rating, dbid, dbtype, tmdbId):
	if rating>10: rating=0
	if dbtype=='movie':
		request = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : ' + str(dbid) + ', "userrating": ' + str(rating) + '}}'
	else:
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

def prompt(dbid, dbtype, tmdbId):
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
	sel = xbmcgui.Dialog().select(lang(30010), pList)
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
		tmdbRated(rating, dbid, dbtype, tmdbId)

def main():
	dbid=xbmc.getInfoLabel('ListItem.DBID')
	dbtype = xbmc.getInfoLabel('ListItem.DBTYPE')
	IMDBNumber = xbmc.getInfoLabel('ListItem.IMDBNumber')
	if dbtype=='tvshow': dbtype='tv'

	if str(IMDBNumber) == '':
		tmdbId = getTMDBbyName(dbtype, xbmc.getInfoLabel('ListItem.Title'), xbmc.getInfoLabel('ListItem.Year'))
	else:
		tmdbId = getTMDBbyId(dbtype, IMDBNumber)
	
	if str(tmdbId) == '':
		xbmc.executebuiltin('Notification(' + lang(30010) + ',' + lang(30017) + ')')
	else:
		prompt(dbid, dbtype, tmdbId)

if __name__ == '__main__':
	main()