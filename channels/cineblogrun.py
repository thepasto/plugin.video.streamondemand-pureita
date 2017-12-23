# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-PureITA / XBMC Plugin
# Canale  cineblogrun
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "cineblogrun"
__category__ = "F,S"
__type__ = "generic"
__title__ = "cineblogrun (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.cineblog.run"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host]
]

def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand-pureita.cineblogrun mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Altadefinizione[/COLOR]",
                     action="peliculas",
                     url=host+"/categorie/film-in-altadefinizione/",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Sub Ita[/COLOR]",
                     action="peliculas",
                     url="%s/categorie/film-sub-ita/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_sub_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Categoria[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Lista A-Z[/COLOR]",
                     action="categorias_list",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

def categorias(item):
    logger.info("streamondemand.cineblogrun categorias")

    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<ul class="sub-menu">(.*?)</li></ul></li>')

    # The categories are the options for the combo
    patron = '<li id="[^>]+" class="[^>]+"><a href="([^"]+)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 extra=item.extra,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 url=urlparse.urljoin(host, scrapedurl)))

    return itemlist

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	
def categorias_list(item):
    logger.info("streamondemand.cineblogrun categorias")

    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<ul class="AZList">(.*?)</li></ul>')

    # The categories are the options for the combo
    patron = '<li><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 extra=item.extra,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 url=urlparse.urljoin(host, scrapedurl)))

    return itemlist	
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	
def search(item, texto):
    logger.info("[cineblogrun.py] " + item.url + " search " + texto)
    item.url = host + "?s=" + texto
    try:
        return peliculas(item)
    # The exception is caught, so as not to interrupt the global searcher if a channel fails
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

def novita(item):
    logger.info("streamondemand-pureita.cineblogrun novita")
    itemlist = []

    # Download the page
    data = scrapertools.anti_cloudflare(item.url, headers)

    # Extract the entries (folders)
    patron = r'<a href="([^"]+)"><div class="Image"><figure class="Objf TpMvPlay AAIco-play_arrow">'
    patron += r'<img src="[^"]+" alt="[^"]+">\s*</figure></div><h2 class="Title">([^"]+)</h2>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))


    return itemlist

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
		
def peliculas(item):
    logger.info("streamondemand-pureita.cineblogrun peliculas")
    itemlist = []

    # Download the page
    data = scrapertools.anti_cloudflare(item.url, headers)

    # Extract the entries (folders)
    patron = r'<a href="([^"]+)"><div class="Image"><figure class="Objf TpMvPlay AAIco-play_arrow">'
    patron += r'<img width=".+?" height=".+?" src="[^"]+" class="attachment-thumbnail size-thumbnail wp-post-image" alt="" />'
    patron += r'</figure></div><h2 class="Title">(.*?)</h2>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extra
    patronvideos = '<a class="nextpostslink" rel="next" href="([^"]+)">»</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/return_home_P.png",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/successivo_P.png",
                 folder=True))

    return itemlist

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

def peliculas_list(item):
    logger.info("streamondemand-pureita.cineblogrun peliculas")
    itemlist = []

    # Download the page
    data = scrapertools.anti_cloudflare(item.url, headers)

    # Extract the entries (folders)
    patron = r'<img width=".+?" height=".+?" src="[^"]+" class="[^>]+>\s*</a>'
    patron += r'</td><td class="MvTbTtl"> <a href="([^"]+)" class="MvTbImg"> <strong>(.*?)</strong> </a>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extra
    patronvideos = '<a class="nextpostslink" rel="next" href="([^"]+)">&raquo;</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR orange]Torna Home[/COLOR]",
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/return_home_P.png",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/successivo_P.png",
                 folder=True))

    return itemlist

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

def findvideos(item):

    data = scrapertools.anti_cloudflare(item.url, headers)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR orange][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	
def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand-pureita-master)")

