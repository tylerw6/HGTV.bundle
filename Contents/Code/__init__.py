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

    more_shows = {}
    # ljunkie - haven't found a way to get a listing from the site - these are were "guessed" and verified 
    more_shows['Brother Vs. Brother'] = 'http://www.hgtv.com/hgtv/video/player/0,1000149,HGTV_32796_15241_78444-119114,00.html'
    more_shows['15 Bodacious Backyards'] = 'http://www.hgtv.com/hgtv-15-bodacious-backyards/videos/index.html'
    more_shows['15 Fresh Handmade Gift Ideas'] = 'http://www.hgtv.com/hgtv-15-fresh-handmade-gift-ideas/videos/index.html'
    more_shows['25 Great Holiday Ideas'] = 'http://www.hgtv.com/hgtv-25-great-holiday-ideas/videos/index.html'
    more_shows['All American Handyman'] = 'http://www.hgtv.com/hgtv-all-american-handyman/videos/index.html'
    more_shows['Amazing Water Homes'] = 'http://www.hgtv.com/hgtv-amazing-water-homes/videos/index.html'
    more_shows['Amazing Waterfront Homes'] = 'http://www.hgtv.com/hgtv-amazing-waterfront-homes/videos/index.html'
    more_shows['B. Original'] = 'http://www.hgtv.com/hgtv-b-original/videos/index.html'
    more_shows['Bang for Your Buck'] = 'http://www.hgtv.com/hgtv-bang-for-your-buck/videos/index.html'
    more_shows['Bath Crashers'] = 'http://www.hgtv.com/hgtv-bath-crashers/videos/index.html'
    more_shows['Bathtastic!'] = 'http://www.hgtv.com/hgtv-bathtastic/videos/index.html'
    more_shows['Battle On the Block'] = 'http://www.hgtv.com/hgtv-battle-on-the-block/videos/index.html'
    more_shows['Beautiful Homes'] = 'http://www.hgtv.com/hgtv-beautiful-homes/videos/index.html'
    more_shows['Behind the Magic: Disney Holidays'] = 'http://www.hgtv.com/hgtv-behind-the-magic-disney-holidays/videos/index.html'
    more_shows['Beyond Repair'] = 'http://www.hgtv.com/hgtv-beyond-repair/videos/index.html'
    more_shows['Bought & Sold'] = 'http://www.hgtv.com/hgtv-bought-sold/videos/index.html'
    more_shows['Brother Vs. Brother'] = 'http://www.hgtv.com/hgtv-brother-vs-brother/videos/index.html'
    more_shows['Candice Tells All'] = 'http://www.hgtv.com/hgtv-candice-tells-all/videos/index.html'
    more_shows['Celebrity Holiday Homes '] = 'http://www.hgtv.com/hgtv-celebrity-holiday-homes/videos/index.html'
    more_shows['Celebrity Motor Homes'] = 'http://www.hgtv.com/hgtv-celebrity-motor-homes/videos/index.html'
    more_shows['Closet Cases'] = 'http://www.hgtv.com/hgtv-closet-cases/videos/index.html'
    more_shows['Cool Pools'] = 'http://www.hgtv.com/hgtv-cool-pools/videos/index.html'
    more_shows['Cousins Undercover'] = 'http://www.hgtv.com/hgtv-cousins-undercover/videos/index.html'
    more_shows['Cousins on Call'] = 'http://www.hgtv.com/hgtv-cousins-on-call/videos/index.html'
    more_shows['Deck Wars'] = 'http://www.hgtv.com/hgtv-deck-wars/videos/index.html'
    more_shows['Decked Out'] = 'http://www.hgtv.com/hgtv-decked-out/videos/index.html'
    more_shows['Deserving Design'] = 'http://www.hgtv.com/hgtv-deserving-design/videos/index.html'
    more_shows['Design Remix'] = 'http://www.hgtv.com/hgtv-design-remix/videos/index.html'
    more_shows['Dina\'s Party'] = 'http://www.hgtv.com/hgtv-dinas-party/videos/index.html'
    more_shows['Donna Decorates Dallas'] = 'http://www.hgtv.com/hgtv-donna-decorates-dallas/videos/index.html'
    more_shows['Double Take'] = 'http://www.hgtv.com/hgtv-double-take/videos/index.html'
    more_shows['Elbow Room'] = 'http://www.hgtv.com/hgtv-elbow-room/videos/index.html'
    more_shows['Endless Yard Sale'] = 'http://www.hgtv.com/hgtv-endless-yard-sale/videos/index.html'
    more_shows['Extreme Homes'] = 'http://www.hgtv.com/hgtv-extreme-homes/videos/index.html'
    more_shows['First Time Design'] = 'http://www.hgtv.com/hgtv-first-time-design/videos/index.html'
    more_shows['Flea Market Flip'] = 'http://www.hgtv.com/hgtv-flea-market-flip/videos/index.html'
    more_shows['Going Yard'] = 'http://www.hgtv.com/hgtv-going-yard/videos/index.html'
    more_shows['HGTV\'d'] = 'http://www.hgtv.com/hgtv-hgtvd/videos/index.html'
    more_shows['HGTV Design Star'] = 'http://www.hgtv.com/hgtv-design-star/videos/index.html'
    more_shows['HGTV Home Makeover'] = 'http://www.hgtv.com/hgtv-home-makeover/videos/index.html'
    more_shows['HGTV Outrageous'] = 'http://www.hgtv.com/hgtv-hgtv-outrageous/videos/index.html'
    more_shows['HGTV Showdown'] = 'http://www.hgtv.com/hgtv-hgtv-showdown/videos/index.html'
    more_shows['HGTV Star'] = 'http://www.hgtv.com/hgtv-hgtv-star/videos/index.html'
    more_shows['HGTV Summer Showdown'] = 'http://www.hgtv.com/hgtv-hgtv-summer-showdown/videos/index.html'
    more_shows['HGTV: The Making of Our Magazine'] = 'http://www.hgtv.com/hgtv-hgtv-the-making-of-our-magazine/videos/index.html'
    more_shows['Halloween Block Party'] = 'http://www.hgtv.com/hgtv-halloween-block-party/videos/index.html'
    more_shows['Hollywood for Sale'] = 'http://www.hgtv.com/hgtv-hollywood-for-sale/videos/index.html'
    more_shows['Home Rules'] = 'http://www.hgtv.com/hgtv-home-rules/videos/index.html'
    more_shows['Home Strange Home'] = 'http://www.hgtv.com/hgtv-home-strange-home/videos/index.html'
    more_shows['Home by Novogratz'] = 'http://www.hgtv.com/hgtv-home-by-novogratz/videos/index.html'
    more_shows['Home for the Holidays'] = 'http://www.hgtv.com/hgtv-home-for-the-holidays/videos/index.html'
    more_shows['House Crashers'] = 'http://www.hgtv.com/hgtv-house-crashers/videos/index.html'
    more_shows['House Hunters Renovation'] = 'http://www.hgtv.com/hgtv-house-hunters-renovation/videos/index.html'
    more_shows['House Hunters: Where Are They Now?'] = 'http://www.hgtv.com/hgtv-house-hunters-where-are-they-now/videos/index.html'
    more_shows['I Brake For Yard Sales'] = 'http://www.hgtv.com/hgtv-i-brake-for-yard-sales/videos/index.html'
    more_shows['Kitchen Impossible'] = 'http://www.hgtv.com/hgtv-kitchen-impossible/videos/index.html'
    more_shows['Love It Or List It'] = 'http://www.hgtv.com/hgtv-love-it-or-list-it/videos/index.html'
    more_shows['Love It or List It, Too'] = 'http://www.hgtv.com/hgtv-love-it-or-list-it-too/videos/index.html'
    more_shows['Million Dollar Contractor'] = 'http://www.hgtv.com/hgtv-million-dollar-contractor/videos/index.html'
    more_shows['Million Dollar Rooms'] = 'http://www.hgtv.com/hgtv-million-dollar-rooms/videos/index.html'
    more_shows['Mom Caves'] = 'http://www.hgtv.com/hgtv-mom-caves/videos/index.html'
    more_shows['My Favorite Place'] = 'http://www.hgtv.com/hgtv-my-favorite-place/videos/index.html'
    more_shows['My First Place: Lessons Learned'] = 'http://www.hgtv.com/hgtv-my-first-place-lessons-learned/videos/index.html'
    more_shows['My First Renovation'] = 'http://www.hgtv.com/hgtv-my-first-renovation/videos/index.html'
    more_shows['My First Sale'] = 'http://www.hgtv.com/hgtv-my-first-sale/videos/index.html'
    more_shows['My House Goes Disney'] = 'http://www.hgtv.com/hgtv-my-house-goes-disney/videos/index.html'
    more_shows['My Yard Goes Disney'] = 'http://www.hgtv.com/hgtv-my-yard-goes-disney/videos/index.html'
    more_shows['Myles of Style'] = 'http://www.hgtv.com/hgtv-myles-of-style/videos/index.html'
    more_shows['Paint Over'] = 'http://www.hgtv.com/hgtv-paint-over/videos/index.html'
    more_shows['Posh Pets: Lifestyles of the Rich and Furry'] = 'http://www.hgtv.com/hgtv-posh-pets-lifestyles-of-the-rich-and-furry/videos/index.html'
    more_shows['Professional Grade'] = 'http://www.hgtv.com/hgtv-professional-grade/videos/index.html'
    more_shows['Property Brothers'] = 'http://www.hgtv.com/hgtv-property-brothers/videos/index.html'
    more_shows['Pumpkin Wars'] = 'http://www.hgtv.com/hgtv-pumpkin-wars/videos/index.html'
    more_shows['Rate My Space'] = 'http://www.hgtv.com/hgtv-rate-my-space/videos/index.html'
    more_shows['Rehab Addict'] = 'http://www.hgtv.com/hgtv-rehab-addict/videos/index.html'
    more_shows['Renovation Raiders'] = 'http://www.hgtv.com/hgtv-renovation-raiders/videos/index.html'
    more_shows['Room Crashers'] = 'http://www.hgtv.com/hgtv-room-crashers/videos/index.html'
    more_shows['Run My Makeover'] = 'http://www.hgtv.com/hgtv-run-my-makeover/videos/index.html'
    more_shows['Scoring the Deal'] = 'http://www.hgtv.com/hgtv-scoring-the-deal/videos/index.html'
    more_shows['Secrets From a Stylist'] = 'http://www.hgtv.com/hgtv-secrets-from-a-stylist/videos/index.html'
    more_shows['Selling LA'] = 'http://www.hgtv.com/hgtv-selling-la/videos/index.html'
    more_shows['Selling New York'] = 'http://www.hgtv.com/hgtv-selling-new-york/videos/index.html'
    more_shows['Selling Spelling Manor'] = 'http://www.hgtv.com/hgtv-selling-spelling-manor/videos/index.html'
    more_shows['The Antonio Treatment'] = 'http://www.hgtv.com/hgtv-the-antonio-treatment/videos/index.html'
    more_shows['The Duchess'] = 'http://www.hgtv.com/hgtv-the-duchess/videos/index.html'
    more_shows['The High Low Project'] = 'http://www.hgtv.com/hgtv-the-high-low-project/videos/index.html'
    more_shows['Tough as Nails'] = 'http://www.hgtv.com/hgtv-tough-as-nails/videos/index.html'
    more_shows['Weekday Crafternoon'] = 'http://www.hgtv.com/hgtv-weekday-crafternoon/videos/index.html'
    more_shows['West End Salvage'] = 'http://www.hgtv.com/hgtv-west-end-salvage/videos/index.html'

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
