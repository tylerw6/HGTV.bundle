NAME = "HGTV"
BASE_URL = "http://www.hgtv.com"

# Full Episode URLs
SHOW_LINKS_URL = "http://www.hgtv.com/full-episodes/package/index.html"

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

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/video/hgtv', NAME)
def MainMenu():

	oc = ObjectContainer()

	for s in HTML.ElementFromURL(SHOW_LINKS_URL).xpath('//h2'):
		title = s.text

		if title == "Featured Series":
			continue

		url = s.xpath("./../p[@class='cta']/a/@href")[0]
		thumb_url = s.xpath("./../a/img/@src")[0]

		oc.add(
			DirectoryObject(
				key = Callback(GetSeasons, path=BASE_URL + url, title=title, thumb_url=thumb_url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url)
			)
		)

	# There are a couple of shows missing from the "full episodes" listings, let's add these as well
	more_shows = {}
	more_shows['Property Brothers'] = 'http://www.hgtv.com/hgtv-property-brothers/videos/index.html'
	more_shows['Candace Tells All'] = 'http://www.hgtv.com/candice-tells-all-full-episodes/videos/index.html'

	for s in more_shows.keys():
		oc.add(
			DirectoryObject(
				key = Callback(GetSeasons, path=more_shows[s], title=s, thumb_url=''),
				title = s
			)
		)

	# sort our shows into alphabetical order here
	oc.objects.sort(key = lambda obj: obj.title)

	return oc

####################################################################################################
@route('/video/hgtv/seasons')
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
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url)
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
					thumb = Resource.ContentsOfURLWithFallback(url=thumb_url)
				)
			)
		except:
			pass

	if len(oc) < 1:
		oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")

	return oc

####################################################################################################
@route('/video/hgtv/shows')
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
			duration = Datetime.MillisecondsFromString(c.xpath("./length")[0].text)
			desc = c.xpath("./abstract")[0].text
			video_id = c.xpath("./videoId")[0].text
			thumb_url = c.xpath("./thumbnailUrl")[0].text.replace('_92x69.jpg', '_480x360.jpg')

			oc.add(
				EpisodeObject(
					url = VIDEO_URL % (video_id, show_id),
					title = title,
					duration = duration,
					summary = desc,
					thumb = Resource.ContentsOfURLWithFallback(url=thumb_url)
				)
			)
		except:
			pass

	if len(oc) < 1:
		oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")

	return oc
