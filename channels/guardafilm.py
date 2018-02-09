# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-PureITA / XBMC Plugin
# Canale GuardaFilm
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import re

from core import logger
from core import httptools
from core import servertools
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "guardafilm"
host = "http://www.guardafilm.site/"

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Referer', host]]

def isGeneric():
    return True

def mainlist(item):
    logger.info("[StreamOnDemand-PureITA GuardaFilm] mainlist")
    itemlist = [Item(channel=__channel__,
                     action="film",
                     title="Film [COLOR orange] - Novita [/COLOR]",
                     url="%s/movies/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     action="genere",
                     title="Film [COLOR orange] - Generi [/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     action="film",
                     title="Film [COLOR orange] - Alta Definizione [/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca ...[/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("[StreamOnDemand-PureITA GuardaFilm] search")

    item.url = host + "/?s=" + texto

    try:
        return film(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==============================================================================================================================================================================

def genere(item):
    logger.info("[StreamOnDemand-PureITA GuardaFilm] genere")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, r'<a>Scegli per Genere</a>(.*?)</ul></div>')
	
    patron = r'<a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="film",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist
	
# ==============================================================================================================================================================================

def film(item):
    logger.info("[StreamOnDemand-PureITA GuardaFilm] film")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<div data-movie-id=".*?" class="ml-item">\s*'
    patron += '<a href="([^"]+)" data-url="" class="ml-mask jt" data-hasqtip=".*?" oldtitle=".*?" title="">\s*'
    patron += '<img data-original="([^"]+)" class="lazy thumb mli-thumb" alt="([^<]+)">'
    matches = re.compile(patron, re.DOTALL).findall(data)
	
    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:	
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo="movie"))
				 
    next_page = scrapertools.find_single_match(data, "<li class='active'><a class=''>[^>]+</a></li><li><a rel='nofollow'\s*class='page larger'\s*href='(.*?)'>[^>]+</a></li>")
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="film",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist


# ==============================================================================================================================================================================
"""
def findvideos(item):
    logger.info("StreamOnDemand-PureITA GuardaFilm findvideos")
    itemlist = []
	
    data = httptools.downloadpage(item.url, headers=headers).data 
    patron = 'src="([^"]+)" frameborder="0"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        if "dir?" in scrapedurl:
            data += httptools.downloadpage(scrapedurl).url
        else:
            data += httptools.downloadpage(scrapedurl).data

    for videoitem in servertools.find_video_items(data=data):
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)

    return itemlist
"""




