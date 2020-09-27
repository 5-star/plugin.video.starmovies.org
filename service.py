# -*- coding: utf-8 -*-
import synch
import sys, os, re
import json
import time
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
 
class ScanMonitor(xbmc.Monitor):
	def __init__(self, *args, **kwargs):
		xbmc.Monitor.__init__(self)

	def onCleanFinished(self, database):
		synch.synchCollection("S")
		synch.synchCollection("M")

	def onScanFinished(self, database):
		synch.synchCollection("S")
		synch.synchCollection("M")

scan_monitor = ScanMonitor()

while not xbmc.Monitor().abortRequested:
	xbmc.sleep(1000)

del scan_monitor
