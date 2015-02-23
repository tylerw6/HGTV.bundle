NAME = "HGTV"
PREFIX = '/video/hgtv'
BASE_URL = "http://www.hgtv.com"

FULLEP_URL = "http://www.hgtv.com/shows/full-episodes"
SHOW_LINKS_URL = "http://www.hgtv.com/shows/shows-a-z"

NAMESPACES = {"a":"http://www.w3.org/2005/SMIL21/Language"}

####################################################################################################
def Start():

    ObjectContainer.title1 = NAME
    HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler(PREFIX, NAME)
def MainMenu():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(FullEpMenu, title="Full Episodes"), title="Full Episodes"))
    oc.add(DirectoryObject(key = Callback(Alphabet, title="All HGTV Shows"), title="All HGTV Shows"))
    return oc
####################################################################################################
# This function produces a list of shows from the HGTV full episodes page
@route(PREFIX + '/fullepmenu')
def FullEpMenu(title):

    oc = ObjectContainer(title2=title)

    for item in HTML.ElementFromURL(FULLEP_URL).xpath('//div[@class="parbase editorialPromo section"]//ul/li'):
        title = item.xpath('.//h4/a/text()')[0]
        url = item.xpath('./div[@class="media"]/a/@href')[0]
        thumb = item.xpath('./div[@class="media"]/a/img/@src')[0]
        desc = item.xpath('.//h4/a/span//text()')[0]
        oc.add(DirectoryObject(key = Callback(VideoBrowse, url=url, title=title), title=title, thumb=thumb, summary=desc))

    # sort shows in alphabetical order here
    oc.objects.sort(key = lambda obj: obj.title)

    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There are no full episode shows to list")
    else:
        return oc
####################################################################################################
# A to Z pull for HGTV shows
@route(PREFIX + '/alphabet')
def Alphabet(title):
    oc = ObjectContainer(title2=title)
    for ch in HTML.ElementFromURL(SHOW_LINKS_URL).xpath('//section[@class="site-index"]/h2//text()'):
        title = ch
        ch = ch.lower()
        oc.add(DirectoryObject(key=Callback(AllShows, title=title, ch=ch), title=title))
    
    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There are no shows to list")
    else:
        return oc
####################################################################################################
# This function produces a list of all HGTV Shows based on letter chosen in Alphabet function
@route(PREFIX + '/allshows')
def AllShows(title, ch):

    oc = ObjectContainer(title2=title)

    for show in HTML.ElementFromURL(SHOW_LINKS_URL).xpath('//h2[@id="%s"]/following-sibling::ul/li/a' %ch):
        title = show.text
        show_url = show.xpath("./@href")[0]
        oc.add(DirectoryObject(key = Callback(GetVideoLinks, show_url=show_url, title=title), title = title))

    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There are no shows to list")
    else:
        return oc
####################################################################################################
# This function pulls the video and full episode links from a show's main page
@route(PREFIX + '/getvideolinks')
def GetVideoLinks(title, show_url):

    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(show_url)
    try:
        video_url = data.xpath('//div[@class="sub-navigation"]//a[contains(text(), "Videos")]//@href')[0]
        oc.add(DirectoryObject(key = Callback(VideoBrowse, url=video_url, title="Videos"), title="Videos"))
    except:
        pass
    # there can be more than one full episode link here if there are multiple seasons so make it a list and loop thru
    try:
        fullep_list = data.xpath('//div[@class="sub-navigation"]//a[contains(text(), "Full Episodes")]')
        for item in fullep_list:
            fullep_url = item.xpath('.//@href')[0]
            full_title = item.xpath('.//text()')[0]
            oc.add(DirectoryObject(key = Callback(VideoBrowse, url=fullep_url, title=full_title), title=full_title))
    except:
        pass
        
    if len(oc) < 1:
        return ObjectContainer(header="No Videos", message="This show does not have a video page")
    else:
        return oc
####################################################################################################
# This function produces a list of videos for any page with a video player in it 
@route(PREFIX + '/videobrowse')
def VideoBrowse(url, title = None):

    oc = ObjectContainer(title2=title)
    page = HTML.ElementFromURL(url)
    
    # To prevent any issues with URLs that do not contain the video playlist json, we put the json pull in a try/except
    try:
        json_data = page.xpath('//div[@class="video-player-container"]/@data-video-prop')[0]
        json = JSON.ObjectFromString(json_data)
    except: json = None
    
    if json:
        for video in json['channels'][0]['videos']:
            vid_smil = video['releaseUrl']

            if not vid_smil.startswith('http://'):
                continue

            title = video['title'].replace('&amp,', '&')
            duration = int(video['length'])*1000
            desc = video['description']
            thumb = BASE_URL + video['thumbnailUrl']

            oc.add(
                CreateObject(
                    url = url,
                    vid_smil = vid_smil,
                    title = title,
                    duration = duration,
                    summary = desc,
                    thumb = thumb
                )
            )
    else:
        Log('%s does not contain a video list json or the json is incomplete' %url)

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are currently no videos for this show.")
    else:
        return oc

####################################################################################################
# This function creates an object container for RSS feeds that have a media file in the feed
@route(PREFIX + '/createobject', duration=int)
def CreateObject(url, vid_smil, title, duration, thumb, summary, include_container=False):

    smil = XML.ElementFromURL(vid_smil)
    res_list = []
    
    for videos in smil.xpath('//a:video', namespaces=NAMESPACES):
        vid_source = videos.xpath('./@src', namespaces=NAMESPACES)[0]
        # All videos appear to be mp4 but do a check to make sure
        vid_type = vid_source.split('.')[-1]
        if vid_type != 'mp4':
            Log('The %s video is of type %s and not compatible with this plugin' %(vid_source, vid_type))
            continue
        vid_resolution = videos.xpath('./@height', namespaces=NAMESPACES)[0]
        # The smil breaks the video up into parts to include ads but every part references the same mp4 file just at different start and end points
        # Since there are multiple occurrences of each source and resolution, we get the first one and then break out
        if (vid_source, vid_resolution) not in res_list:
            res_list.append((vid_source, vid_resolution))
        else:
            break
    #Log('This value of res_list is %s' %res_list)
        
    # This makes sure that the smil returned at least one value for the video and resolution
    if len(res_list)==0:
        Log ('no values for resolution and video source')
        return ObjectContainer(header="Empty", message="The video information associated with this webpage is incomplete or invalid.")
    else:
        # A few videos mention the season or episode but most do not so since this is an internal feature, we are just making them all VideoClipObjects
        new_object = VideoClipObject(
            key = Callback(CreateObject, url=url, vid_smil=vid_smil, title=title, duration=duration, thumb=thumb, summary=summary, include_container=True),
            rating_key = vid_source,
            title = title,
            summary = summary,
            thumb = Resource.ContentsOfURLWithFallback(url=thumb),
            duration = duration,
            items = [
                MediaObject(
                    parts = [
                        PartObject(key=source)
                            ],
                            container = Container.MP4,
                            video_codec = VideoCodec.H264,
                            audio_codec = AudioCodec.AAC,
                            audio_channels = 2,
                            video_resolution = resolution
                )for source,resolution in res_list
            ]
        )

    if include_container:
        return ObjectContainer(objects=[new_object])
    else:
        return new_object
