import re, sys, urllib2

PLUGIN_PREFIX   = "/video/hgtv"

# Full Episode URLs
SHOW_LINKS_URL			 = "http://www.hgtv.com/full-episodes/package/index.html"

# Clip URLs
BASE_URL				= "http://www.hgtv.com"

CACHE_INTERVAL			= 2000

ART = "art-default.jpg"
ICON = "icon-default.png"
NAME = "HGTV"
VIDEO_URL="http://www.hgtv.com/video/?videoId=%s&showId=%s"

####################################################################################################
def Start():
 
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	MediaContainer.title1 = NAME
	MediaContainer.content = 'Items'
	MediaContainer.art = R(ART)
	MediaContainer.viewGroup = "List"

	DirectoryItem.thumb = R(ICON)
	
	HTTP.CacheTime = CACHE_INTERVAL
##################################################################################################

def MainMenu():
#	dir= MediaContainer(viewGroup = 'List')

	oc = ObjectContainer( view_group = 'List')
	for s in HTML.ElementFromURL(SHOW_LINKS_URL).xpath('//h2'):
		title = s.text
		url = s.xpath("../p[@class='cta']/a")[0].get('href')
		thumb_url = s.xpath("../a/img")[0].get('src')
		oc.add(
			DirectoryObject(
				key = Callback(GetShows, path=BASE_URL + url, title=title),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
			)
		)
	return oc

	
def GetShows(path,title=None):

	html = HTTP.Request(path).content
	matches = re.search("SNI.HGTV.Player.FullSize\('vplayer-1','([^']*)'", html)
	try:
		oc = ObjectContainer(view_group='List')

		show_id = matches.group(1)
		matches = re.search("mdManager.addParameter\(\"SctnId\",[\s]*\"([^\"]*)", html)
		showURL='http://www.hgtv.com/hgtv/channel/xml/0,,'+show_id+',00.xml'
		xmlcontent = HTTP.Request('http://www.hgtv.com/hgtv/channel/xml/0,,'+show_id+',00.xml').content.strip()

		#Log("Gerk: show URL: %s",showURL)
		#Log(xmlcontent)
 		#videos=XML.ElementFromString(xmlcontent)
		#videos=XML.ObjectFromString(xmlcontent)
		#Log(videos)
		
		for c in XML.ElementFromString(xmlcontent).xpath("//video"):
			title = c.xpath("./clipName")[0].text
			Log("Gerk: in init title: %s",title)
			duration = GetDurationFromString(c.xpath("length")[0].text)
			desc = c.xpath("abstract")[0].text
			videoId = c.xpath("videoId")[0].text
			Log("Gerk: videoId from init: %s",videoId)
			#url = c.xpath("./videoUrl")[0].text.replace('http://wms','rtmp://flash').replace('.wmv','').replace('scrippsnetworks.com/','scrippsnetworks.com/ondemand/&').split('&')
			thumb_url = c.xpath("thumbnailUrl")[0].text
			#dir.Append(RTMPVideoItem(url[0], clip=url[1], title=title, summary=desc, duration=duration, thumb=Function(GetThumb, path=thumb)))
			#Log("Gerk: url: %s",url)
			oc.add(
				EpisodeObject(
					url = VIDEO_URL % (videoId, show_id),
					title = title,
					duration = duration,
					summary = desc,
					thumb=Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
				)
			)
			return oc
	except:
		oc = MessageContainer("Sorry","This section does not contain any videos")
		return oc

	
def GetDurationFromString(duration):

	try:
		durationArray = duration.split(":")

		if len(durationArray) == 3:
			hours = int(durationArray[0])
			minutes = int(durationArray[1])
			seconds = int(durationArray[2])
		elif len(durationArray) == 2:
			hours = 0
			minutes = int(durationArray[0])
			seconds = int(durationArray[1])
		elif len(durationArray)	==	1:
			hours = 0
			minutes = 0
			seconds = int(durationArray[0])
			
		return int(((hours)*3600 + (minutes*60) + seconds)*1000)
		
	except:
		return 0