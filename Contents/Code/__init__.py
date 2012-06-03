NAME = "HGTV"
ART = "art-default.jpg"
ICON = "icon-default.png"

# Full Episode URLs
SHOW_LINKS_URL = "http://www.hgtv.com/full-episodes/package/index.html"

BASE_URL = "http://www.hgtv.com"

# NB: this is a "made up" URL, they don't have direct play URLs
# for videos and even their listing pages are all over the map
# therefore the URL service is local (within the plugin) as opposed
# to putting it globally within the services.bundle
VIDEO_URL = "http://www.hgtv.com/video/?videoId=%s&showId=%s"

VPLAYER_MATCHES = Regex("SNI.HGTV.Player.FullSize\('vplayer-1','([^']*)'")

####################################################################################################
def Start():

	Plugin.AddPrefixHandler("/video/hgtv", MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	ObjectContainer.title1 = NAME
	ObjectContainer.content = 'Items'
	ObjectContainer.art = R(ART)
	ObjectContainer.viewGroup = "List"

	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR

##################################################################################################
def MainMenu():

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

##################################################################################################
def GetShows(path,title=None):

	html = HTTP.Request(path).content
	matches = VPLAYER_MATCHES.search(html)
	oc = ObjectContainer(view_group='List')
	try:

		show_id = matches.group(1)
		xmlcontent = HTTP.Request('http://www.hgtv.com/hgtv/channel/xml/0,,%s,00.xml' % show_id).content.strip()
		
		for c in XML.ElementFromString(xmlcontent).xpath("//video"):
			title = c.xpath("./clipName")[0].text

			duration = GetDurationFromString(c.xpath("length")[0].text)
			desc = c.xpath("abstract")[0].text
			videoId = c.xpath("videoId")[0].text

			thumb_url = c.xpath("thumbnailUrl")[0].text
			oc.add(
				EpisodeObject(
					url = VIDEO_URL % (videoId, show_id),
					title = title,
					duration = duration,
					summary = desc,
					thumb=Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
				)
			)
	except:
		oc = MessageContainer("Sorry","This section does not contain any videos")

	return oc

##################################################################################################
def GetDurationFromString(duration):

	seconds = 0

	try:
		duration = duration.split(':')
		duration.reverse()

		for i in range(0, len(duration)):
			seconds += int(duration[i]) * (60**i)
	except:
		pass

	return seconds * 1000
