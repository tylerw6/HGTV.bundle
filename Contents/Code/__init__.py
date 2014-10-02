NAME = "HGTV"
PREFIX = '/video/hgtv'
BASE_URL = "http://www.hgtv.com"

# Full Episode URLs
FULLEP_URL = "http://www.hgtv.com/hgtv-full-episodes/videos/index.html"
SHOW_LINKS_URL = "http://www.hgtv.com/on-tv/index.html"

# NB: this is a "made up" URL, they don't have direct play URLs
# for videos (actually they do have direct play URLs but almost never use them)
# and even their listing pages are all over the map
# therefore the URL service is local (within the plugin) as opposed
# to putting it globally within the services.bundle for use with PlexIt and the like
VIDEO_URL = "http://www.hgtv.com/video/?videoId=%s&showId=%s"

VPLAYER_MATCHES = Regex("SNI.HGTV.Player.FullSize\('vplayer-1','([^']*)'")
RE_AMPERSAND = Regex('&(?!amp;)')
RE_SEASON  = Regex('Season (\d{1,2})')
RE_EP = Regex('Ep. (\d{1,3})')

# Below is a compiled list of shows known to have a Full Episodes link on its show page and the URL for that full episode page
TOP_SHOWS = [ {'name' : 'All American Handyman', 'url' : 'http://www.hgtv.com/hgtv-all-american-handyman/videos/index.html'},
              {'name' : 'Brother vs Brother', 'url' : 'http://www.hgtv.com/hgtv/video/player/0,1000149,HGTV_32796_15241_78444-119114,00.html'},
              {'name' : 'Bang for Your Buck', 'url' : 'http://www.hgtv.com/hgtv-bang-for-your-buck/videos/index.html'},
              {'name' : 'Color Splash', 'url' : 'http://www.hgtv.com/hgtv74/videos/index.html'},
               {'name' : 'Curb Appeal',  'url' : 'http://www.hgtv.com/hgtv42/videos/index.html'},
              {'name' : "HGTV'd", 'url' : 'http://www.hgtv.com/hgtv-hgtvd/videos/index.html'}, 
              {'name' : 'HGTV Design Star', 'url' : 'http://www.hgtv.com/hgtv/video/player/0,1000149,HGTV_32796_15041_77321-117842,00.html'}, 
              {'name' : 'House Crashers', 'url' : 'http://www.hgtv.com/hgtv-house-crashers/videos/index.html'},
              {'name' : 'House Hunters', 'url' : 'http://www.hgtv.com/hgtv40/videos/index.html'},
              {'name' : 'House Hunters International', 'url' : 'http://www.hgtv.com/hgtv56/videos/index.html'},
              {'name' : 'House Hunters Renovation', 'url' : 'http://www.hgtv.com/hgtv-house-hunters-renovation2/videos/index.html'},
              {'name' : 'My First Place', 'url' : 'http://www.hgtv.com/hgtv58/videos/index.html'},
              {'name' : 'My Yard Goes Disney', 'url' : 'http://www.hgtv.com/hgtv-my-yard-goes-disney/videos/index.html'},
              {'name' : 'Property Brothers', 'url' : 'http://www.hgtv.com/hgtv-property-brothers/videos/index.html'},
              {'name' : 'Property Virgins', 'url' : 'http://www.hgtv.com/hgtv48/videos/index.html'},
              {'name' : 'Selling New York', 'url' : 'http://www.hgtv.com/hgtv-selling-new-york/videos/index.html'},
              {'name' : 'The Antonio Treatment', 'url' : 'http://www.hgtv.com/hgtv-the-antonio-treatment/videos/index.html'}
               ]

# This regex can be used to pull the banner image at the top of every page but hard to read for some shows (RE_LOGO.search(content).group(1))
#RE_LOGO = Regex('background-image: url\((.+?)\);')
####################################################################################################
def Start():

    ObjectContainer.title1 = NAME
    HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler(PREFIX, NAME)
def MainMenu():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(ShowMenu, title="Top HGTV Shows"), title="Top HGTV Shows"))
    oc.add(DirectoryObject(key = Callback(GetSections, path=FULLEP_URL, title="Full Episodes"), title="Full Episodes"))
    oc.add(DirectoryObject(key = Callback(Alphabet, title="All HGTV Shows"), title="All HGTV Shows"))
    return oc
####################################################################################################
# This function produces a list of shows known to have full episodes
@route(PREFIX + '/showmenu')
def ShowMenu(title):

    oc = ObjectContainer(title2=title)

    for show in TOP_SHOWS:
        title = show['name']
        url = show['url']
        oc.add(DirectoryObject(key = Callback(GetSections, path=url, title=title), title = title))

    # sort our shows into alphabetical order here
    oc.objects.sort(key = lambda obj: obj.title)

    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There are no shows to list")
    else:
        return oc
####################################################################################################
# A to Z pull for HGTV
@route(PREFIX + '/alphabet')
def Alphabet(title):
    oc = ObjectContainer(title2=title)
    for ch in list('#ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        oc.add(DirectoryObject(key=Callback(AllShows, title=ch, ch=ch), title=ch))
    return oc
####################################################################################################
# This function produces a list of all HGTV Shows
@route(PREFIX + '/allshows')
def AllShows(title, ch):

    oc = ObjectContainer()

    for s in HTML.ElementFromURL(SHOW_LINKS_URL).xpath('//div[@id="dm-shows-az"]/ul/li/a'):
        title = s.text
        if title.startswith(ch) or (title[0].isalpha()==False and ch=='#'):
            show_url = s.xpath("./@href")[0]
            oc.add(DirectoryObject(key = Callback(GetVideoLinks, show_url=show_url, title=title), title = title))

    # sort our shows into alphabetical order here
    oc.objects.sort(key = lambda obj: obj.title)
    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There are no shows to list")
    else:
        return oc
####################################################################################################
# This function pulls the video and full episode links from a show's main page
@route(PREFIX + '/getvideolinks')
def GetVideoLinks(title, show_url):

    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(BASE_URL + show_url)
    # Get the link for the "Videos" and "Full Episode" buttons listed at the top left side of the page for most shows
    link_list = data.xpath('//ul[@class="button-nav"]/li/a')
    if link_list > 0:
        for link in link_list:
            vid_title = link.xpath('.//text()')[0]
            if vid_title in ['ABOUT', 'PHOTOS ']:
                continue
            vid_url = BASE_URL + link.xpath('./@href')[0]
            oc.add(DirectoryObject(key = Callback(GetSections, path=vid_url, title=vid_title), title=vid_title))
    # Get the "Video" link for pages that have the alternative setup like Brother vs Brother and HGTV Star
    else:
        vid_url = data.xpath('//li[@class="tab-videos"]/a/@href')[0]
        vid_title = 'Videos'
        oc.add(DirectoryObject(key = Callback(GetSections, path=vid_url, title=vid_title), title=vid_title))
        
    if len(oc) < 1:
        return ObjectContainer(header="No Videos", message="This show does not have a video page")
    else:
        return oc
####################################################################################################
# This function pulls the titles for each carousels sections on a video page and gets the first video URL for that carousel
# This first video url is later used to pull all the videos that are listed in the video player at the top of the page
@route(PREFIX + '/getsections')
def GetSections(path, title):

    oc = ObjectContainer(title2=title)
    content = HTTP.Request(path).content
    data = HTML.ElementFromString(content)

    matches = VPLAYER_MATCHES.search(content)
    if matches:
        show_id = matches.group(1)
        xml = HTTP.Request('http://www.hgtv.com/hgtv/channel/xml/0,,%s,00.xml' %show_id).content.strip()
        xml = RE_AMPERSAND.sub('&amp;', xml)
        title = XML.ElementFromString(xml).xpath("//title/text()")[0].strip()
        if 'Season' in title:
            season = int(RE_SEASON.search(title).group(1))
        else:
            season = 0
        oc.add(DirectoryObject(key = Callback(GetShows, path=path, season=season, title=title), title=title))
    else:
        return ObjectContainer(header="Empty", message="There are no videos to list right now.")
        #pass

    # This pulls the data for any additional sections/carousels that may be listed under the video player
    for section in data.xpath("//ul[@class='channel-list']/li"):
        title = section.xpath("./h4/text()")[0].strip()
        url = section.xpath("./div/div[@class='crsl-wrap']/ul/li[1]/a/@href")[0]
        if 'Season' in title:
            season = int(RE_SEASON.search(title).group(1))
        else:
            season = 0
        oc.add(DirectoryObject(key = Callback(GetShows, path=BASE_URL+url, season=season, title=title), title=title))

    if len(oc) < 1:
        return ObjectContainer(header="Sorry", message="There are no video sections for this show")
    else:
        return oc
####################################################################################################
# This function produces the videos listed within a particular carousel
# It takes the first video URL within a section or carousel and uses that URL to get the video player info
# and its corresponding xml file that list all the data for each video listed under the video player
@route(PREFIX + '/getshows', season=int)
def GetShows(path, title, season):

    oc = ObjectContainer(title2=title)
    content = HTTP.Request(path).content
    matches = VPLAYER_MATCHES.search(content)

    show_id = matches.group(1)
    xml = HTTP.Request('http://www.hgtv.com/hgtv/channel/xml/0,,%s,00.xml' % show_id).content.strip()
    xml = RE_AMPERSAND.sub('&amp;', xml)

    for c in XML.ElementFromString(xml).xpath("//video"):
        title = c.xpath("./clipName")[0].text.strip()
        duration = Datetime.MillisecondsFromString(c.xpath("./length")[0].text)
        desc = c.xpath("./abstract")[0].text
        video_id = c.xpath("./videoId")[0].text
        thumb_url = c.xpath("./thumbnailUrl")[0].text.replace('_92x69.jpg', '_480x360.jpg')
        if season > 0 or 'Ep.' in title:
            if 'Ep.' in title:
                episode = int(RE_EP.search(title).group(1))
            else:
                episode = 0
            oc.add(
                EpisodeObject(
                    url = VIDEO_URL % (video_id, show_id),
                    title = title,
                    duration = duration,
                    summary = desc,
                    index = episode,
                    season = season,
                    thumb = Resource.ContentsOfURLWithFallback(url=thumb_url)
                )
            )
        else:
            oc.add(
                VideoClipObject(
                    url = VIDEO_URL % (video_id, show_id),
                    title = title,
                    duration = duration,
                    summary = desc,
                    thumb = Resource.ContentsOfURLWithFallback(url=thumb_url)
                )
            )

    if len(oc) < 1:
        return ObjectContainer(header="Sorry", message="This section does not contain any videos")
    else:
        return oc
