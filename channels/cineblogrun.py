# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-PureITA / XBMC Plugin
# Canale  cineblogrun
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "cineblogrun"
host = "https://www.cineblog.run"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita.cineblogrun mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
                     action="peliculas",
                     url=host + "/film",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]HD[/COLOR]",
                     action="peliculas",
                     url=host+"/categorie/film-in-altadefinizione",
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

# ===================================================================================================================================================	

def categorias(item):
    logger.info("streamondemand.cineblogrun categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, 'Categorie</a>(.*?)</ul>')

    # The categories are the options for the combo
    patron = '<li id[^>]+"><a href="([^"]+)">(.*?)</a>'
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

# ===================================================================================================================================================
	
def categorias_list(item):
    logger.info("streamondemand.cineblogrun categorias")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<ul class="AZList">(.*?)</ul>')

    # The categories are the options for the combo
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
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
	
# ===================================================================================================================================================	
	
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

# ===================================================================================================================================================
		
def peliculas(item):
    logger.info("streamondemand-pureita.cineblogrun peliculas")
    itemlist = []

    # Download the page
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extract the entries (folders)
    patron = r'<a href="([^"]+)"><div class="Image">\s*<figure clas[^>]+><img[^>]+src="([^"]+)"\s*'
    patron += r'class[^>]+></figure></div><h3 class="Title">(.*?)</h3>\s*'
    patron += r'.*?<p>(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedthumbnail = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
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
    patronvideos = '<a class="next page-numbers" href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ===================================================================================================================================================	

def peliculas_list(item):
    logger.info("streamondemand-pureita.cineblogrun peliculas")
    itemlist = []

    # Download the page
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extract the entries (folders)
    patron = r'<img[^>]+src="([^"]+)"\s*class="[^>]+>\s*</a></td><td[^>]+>\s*'
    patron += r'<a href="([^"]+)"\s*class[^>]+>\s*<strong>([^<]+)</strong>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(2))
        scrapedthumbnail = scrapertools.unescape(match.group(1))
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
    patronvideos = '<a class="next page-numbers" href="([^"]+)">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def findvideos(item):
    logger.info("streamondemand-pureita cineblogrun findvideos")
    data = httptools.downloadpage(item.url, headers=headers).data

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR orange][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist



