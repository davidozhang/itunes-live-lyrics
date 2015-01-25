#!/usr/bin/python

'''
iTunes Live Lyrics Mac Client
Author: David Zhang
Started: August 2, 2014
Last Updated: Jan 24, 2015
Version: 1.1 (Updates to come later!)
(C) Copyright David Zhang, 2015.
All lyrics fetched through the app belong to respective artists, owners, Lyrics Wiki and Gracenote. I do not own any of the lyrics contents.
'''

from Foundation import *
from ScriptingBridge import *
from bs4 import BeautifulSoup as bs
import time
import re
import urllib
import requests
import StringIO

iTunes=SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")

def queryConstructor(currentArtist, currentTrack, callAPI):
	
	artistQuery = ''
	songQuery = ''
	symbol = ''
	if not callAPI:
		symbol = ':'
	
	for i in range (0, len(currentArtist.split())):
                if i==len(currentArtist.split())-1:
                	artistQuery+=currentArtist.split()[i]+symbol
                else:
                	artistQuery+=currentArtist.split()[i]+'_'
        for j in range (0, len(currentTrack.split())):
                if j==len(currentTrack.split())-1:
                	songQuery+=currentTrack.split()[j]
                else:
                	songQuery+=currentTrack.split()[j]+'_'
	
	return artistQuery, songQuery

def songInfo(currentArtist, currentTrack, currentAlbum, currentGenre):

	border = ''
	max = 0

	displayList = [
		'NOW PLAYING: '+currentArtist+' - '+currentTrack,
		'Album: '+currentAlbum, 'Genre: '+currentGenre,
		'Artist Hometown: '+getHometown(currentArtist,currentTrack),
	]
	for i in displayList:
		if len(i)>max:
			max=len(i)

	for i in range (0,max): border+='-'
        border+='----'

	max+=4
	print '\n'+border
	for j in displayList:
		display='| '+j
		while len(display)<max-1:
			display+=' '
		display+='|'
		print display
	print border+'\n'

def lyricsNotFound(currentArtist, currentTrack):

	diagnoseFirstLine = getFirstLine(currentArtist, currentTrack)

	if '(' in currentTrack or ')' in currentTrack or '[' in currentTrack or ']' in currentTrack:	
		trackRemoveBrackets = re.sub(r'\[.*\]','',currentTrack)
		trackRemoveBrackets = re.sub(r'\(.*\)','',trackRemoveBrackets)
	
		firstLine = getFirstLine(currentArtist, trackRemoveBrackets)
		detectLyrics(currentArtist, trackRemoveBrackets, firstLine)
	elif 'ft.' in currentArtist:
		currentArtist = currentArtist[:currentArtist.index('ft.')].strip()
		if 'ft.' in currentTrack:
			currentTrack = currentTrack[:currentTrack.index('ft.')].strip()
		firstLine = getFirstLine(currentArtist, currentTrack)
		detectLyrics(currentArtist, currentTrack,firstLine)
	else:
		print "No Lyrics Found.. Sorry!"
	
def detectLyrics(currentArtist, currentTrack, firstLine):

	if firstLine=='Not found':
		lyricsNotFound(currentArtist, currentTrack)
	else:
		displayLyrics(currentArtist, currentTrack, extractHTML(currentArtist, currentTrack,firstLine))

def displayLyrics(currentArtist, currentTrack, soup):

	if firstLine not in soup or '<p>NewPP limit report' not in soup:
		lyricsNotFound(currentArtist, currentTrack)
	else:
		print soup[soup.index(firstLine):soup.index('<p>NewPP limit report')].replace('<br/>','\n').replace('<i>','').replace('</i>','').replace('<b>','').replace('</b>','').replace('<!--','').strip()

def extractHTML(currentArtist, currentTrack, firstLine):
	
	artistQuery,songQuery = queryConstructor(currentArtist, currentTrack, False)
	r = requests.get('http://lyrics.wikia.com/'+artistQuery+songQuery)
	return str(bs(r.text)).decode('utf_8')

def getHometown(currentArtist, currentTrack):

	urlRoot = 'http://lyrics.wikia.com/api.php?func=getHometown&artist='
	artistQuery, songQuery = queryConstructor(currentArtist, currentTrack, True)
	r = requests.get(urlRoot+artistQuery+'&song='+songQuery+'&fmt=text')
	buf = StringIO.StringIO(bs(r.text).get_text())
	
	if buf.readline().replace('\n','')=='':
		return 'N/A'	
	else: 
		return buf.readline().replace('\n','')

def getFirstLine(currentArtist, currentTrack):

	urlRoot = 'http://lyrics.wikia.com/api.php?func=getSong&artist='
	artistQuery, songQuery = queryConstructor(currentArtist, currentTrack, True)
	artistQuery = urllib.quote(artistQuery)
	songQuery = urllib.quote(songQuery)
	r = requests.get(urlRoot+artistQuery+'&song='+songQuery+'&fmt=text')
	buf = StringIO.StringIO(bs(r.text).get_text())
	
	return buf.readline().replace('\n','').replace('[...]','')

try:
	oldArtist = iTunes.currentTrack().artist()
	oldTrack = iTunes.currentTrack().name()
	oldAlbum = iTunes.currentTrack().album()
	oldGenre = iTunes.currentTrack().genre()

	songInfo(oldArtist, oldTrack, oldAlbum, oldGenre)
	firstLine = getFirstLine(oldArtist, oldTrack)
	detectLyrics(oldArtist, oldTrack, firstLine)

	while True:
		time.sleep(2)
		currentArtist = iTunes.currentTrack().artist()
		currentTrack = iTunes.currentTrack().name()
		currentAlbum = iTunes.currentTrack().album()
		currentGenre = iTunes.currentTrack().genre()

		if currentArtist!=oldArtist or currentTrack!=oldTrack:
			songInfo(currentArtist, currentTrack, currentAlbum, currentGenre)
			firstLine = getFirstLine(currentArtist, currentTrack)
			detectLyrics(currentArtist, currentTrack, firstLine)

		oldArtist = currentArtist
		oldTrack = currentTrack
except TypeError:
	print ""
	print "------------------------------------------------------------"
	print "| iTunesLiveLyrics detected no active iTunes song session. |"
	print "| Play your iTunes song then reload the client. Thanks!    |"
	print "------------------------------------------------------------"

except:
	print ""
	print "--------------------------------------------"
	print "| iTunesLiveLyrics Client has been closed. |"
	print "--------------------------------------------"