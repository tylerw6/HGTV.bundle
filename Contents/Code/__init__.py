NAME = "HGTV"
ART = "art-default.jpg"
ICON = "icon-default.png"

# Full Episode URLs
SHOW_LINKS_URL = "http://www.hgtv.com/full-episodes/package/index.html"

BASE_URL = "http://www.hgtv.com"

# NB: this is a "made up" URL, they don't have direct play URLs
# for videos (actually they do have direct play URLs but almost never use them)
# and even their listing pages are all over the map
# therefore the URL service is local (within the plugin) as opposed
# to putting it globally within the services.bundle for use with PlexIt and the like
VIDEO_URL = "http://www.hgtv.com/video/?videoId=%s&showId=%s"

VPLAYER_MATCHES = Regex("SNI.HGTV.Player.FullSize\('vplayer-1','([^']*)'")
RE_AMPERSAND = Regex('&(?!amp;)')

####################################################################################################
def Start():

	Plugin.AddPrefixHandler("/video/hgtv", MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	ObjectContainer.title1 = NAME
	ObjectContainer.content = 'Items'
	ObjectContainer.art = R(ART)

	DirectoryObject.thumb = R(ICON)

	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
def MainMenu():

	oc = ObjectContainer()

	for s in HTML.ElementFromURL(SHOW_LINKS_URL).xpath('//h2'):
		title = s.text

		if title == "Featured Series":
			continue

		url = s.xpath("../p[@class='cta']/a")[0].get('href')
		thumb_url = s.xpath("../a/img")[0].get('src')

		oc.add(
			DirectoryObject(
				key = Callback(GetSeasons, path=BASE_URL + url, title=title, thumb_url=thumb_url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
			)
		)

	# There are a couple of shows missing from the "full episodes" listings, let's add these as well
	moreShows = {}
	moreShows['Property Brothers'] = 'http://www.hgtv.com/hgtv-property-brothers/videos/index.html'
	moreShows['Candace Tells All'] = 'http://www.hgtv.com/candice-tells-all-full-episodes/videos/index.html'

	for s in moreShows.keys():
		oc.add(
			DirectoryObject(
				key = Callback(GetSeasons, path=moreShows[s], title=s, thumb_url=''),
				title = s,
				thumb = Resource.ContentsOfURLWithFallback(url='', fallback=ICON)
			)
		)
		
	# sort our shows into alphabetical order here
	oc.objects.sort(key = lambda obj: obj.title)
	
	return oc

####################################################################################################
def GetSeasons(path, title, thumb_url):

	oc = ObjectContainer(title2=title)
	html = HTTP.Request(path).content
	matches = VPLAYER_MATCHES.search(html)

	# grab the current season link and title only on this pass, grab each season's actual shows in GetShows()
	try:
		show_id = matches.group(1)
		xml = HTTP.Request('http://www.hgtv.com/hgtv/channel/xml/0,,%s,00.xml' % show_id).content.strip()
		xml = RE_AMPERSAND.sub('&amp;', xml)
		title = XML.ElementFromString(xml).xpath("//title/text()")[0].strip()

		oc.add(
			DirectoryObject(
				key = Callback(GetShows, path=path, title=title),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
			)
		)
	except:
		pass

	# now try to grab any additional seasons/listings via xpath
	data = HTML.ElementFromURL(path)

	for season in data.xpath("//ul[@class='channel-list']/li"):
		try:
			title = season.xpath("./h4/text()")[0].strip()
			url = season.xpath("./div/div[@class='crsl-wrap']/ul/li[1]/a/@href")[0]

			oc.add(
				DirectoryObject(
					key = Callback(GetShows, path= BASE_URL + url, title=title),
					title = title,
					thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
				)
			)
		except:
			pass

	if len(oc) < 1:
		oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")

	return oc

####################################################################################################
def GetShows(path, title):

	oc = ObjectContainer(title2=title)
	html = HTTP.Request(path).content
	matches = VPLAYER_MATCHES.search(html)

	show_id = matches.group(1)
	xml = HTTP.Request('http://www.hgtv.com/hgtv/channel/xml/0,,%s,00.xml' % show_id).content.strip()
	xml = RE_AMPERSAND.sub('&amp;', xml)

	for c in XML.ElementFromString(xml).xpath("//video"):
		try:
			title = c.xpath("./clipName")[0].text.strip()
			duration = GetDurationFromString(c.xpath("./length")[0].text)
			desc = c.xpath("./abstract")[0].text
			videoId = c.xpath("./videoId")[0].text
			thumb_url = c.xpath("./thumbnailUrl")[0].text.replace('_92x69.jpg', '_480x360.jpg')

			oc.add(
				EpisodeObject(
					url = VIDEO_URL % (videoId, show_id),
					title = title,
					duration = duration,
					summary = desc,
					thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
				)
			)
		except:
			pass

	if len(oc) < 1:
		oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")

	return oc

####################################################################################################
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
