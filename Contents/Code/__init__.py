# ALSO CHANGED TABBING TO 4 SPACES THROUGHOUT CODE 
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
    # Found this new show with full episodes was available on website, so added it to list
    more_shows['Brother Vs. Brother'] = 'http://www.hgtv.com/hgtv/video/player/0,1000149,HGTV_32796_15241_78444-119114,00.html'

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
    # Moved this element call to top and changed it to use content, since it may also be used for finding the video link
    data = HTML.ElementFromString(html)
    # A few of the Watch Full Episodes links pulled in the function above from the full episode page are to the show main page 
    # instead of the video page. If it is a show main page, we use that main show page to find that show's video page link
    if path.endswith('show/index.html'):
    # VIDEO PAGE DOES NOT ALWAYS FOLLOW THE SAME NAMING SCHEME AS MAIN PAGE, SO WE CANNOT JUST CHANGE PATH NAME TO VIDEO FOLDER
    # There appears to be two different formats for show pages. Either show has a full episode button at the top or
    # the page has a bar of links that run across the top of the page tha include a video section
        try:
            # Look for full episode button
            new_path = BASE_URL + data.xpath('//ul[@class="button-nav"]/li/a//@href')[1]
        except:
            # Look for the videos link in the top bar
            try:
                new_path = data.xpath('//li[contains(@class,"tab-videos emroom")]/a/@href')[0]
            except:
            # HGTV design star is changing its name and base url from HGTV Design Star (/hgtv-design-star/) to HGTV Star(/hgtv-star/).
            # Currently the full episode page still uses the old main show url (http://www.hgtv.com/hgtv-design-star/show/index.html).
            # To prevent errors from any future changes they may make, added an exception for the old show's base url.
                if '/hgtv-design-star/' in path:
                    new_path = 'http://www.hgtv.com/hgtv/video/player/0,1000149,HGTV_32796_15041_77321-117842,00.html'
                else:
                    pass
        # Then we have to add the parses for the new path and make value of path is the new path, since that variable is sent to next function
        html = HTTP.Request(new_path).content
        data = HTML.ElementFromString(html)
        path = new_path
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
            # Added source network since available and not always HGTV
            source = c.xpath("./sourceNetwork")[0].text
            video_id = c.xpath("./videoId")[0].text
            thumb_url = c.xpath("./thumbnailUrl")[0].text.replace('_92x69.jpg', '_480x360.jpg')

            oc.add(
                # Changed this to an VideoClipObject since not including episode or season data so no ? marks in results. 
                VideoClipObject(
                    url = VIDEO_URL % (video_id, show_id),
                    title = title,
                    duration = duration,
                    summary = desc,
                    source_title = source,
                    thumb = Resource.ContentsOfURLWithFallback(url=thumb_url)
                )
            )
        except:
            pass

    if len(oc) < 1:
        oc = ObjectContainer(header="Sorry", message="This section does not contain any videos")

    return oc
