# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale solostreaming_co
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import base64
import re
import urlparse

from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "solostreaming_co"

host = "https://www.solostreaming.co/"

headers = [['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
           ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Referer', host],
           ['Cache-Control', 'max-age=0']]


def isGeneric():
    return True


def mainlist(item):
    logger.info("pureita solostreaming_co mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Consigliati[/COLOR]",
                     action="peliculas",
                     url="%s/featured/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Per Genere[/COLOR]",
                     action="genere",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Aggiornati[/COLOR]",
                     action="peliculas_update",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film - [COLOR orange]Animazione[/COLOR]",
                     action="peliculas",
                     url="%s/animazione/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animated_movie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="peliculas",
                     url="%s/serietv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==============================================================================================================================================

def genere(item):
    logger.info("pureita solostreaming_co genere")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    patron = '<a href="[^"]+">Home</a>(.*?)<a href="[^"]+">Serie Tv</a>'
    data = scrapertools.find_single_match(data, patron)

    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================

def peliculas(item):
    logger.info("pureita solostreaming_co peliculas")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<div class="td-module-image">\s*<div class="td-module-thumb"><a\s*href="([^"]+)" rel="bookmark" title=".*?">'
    patron += '<img width=".*?" height=".*?"\s*class="entry-thumb"[^>]+src="(.*?)"[^>]+alt=".*?" title="([^<]+)"\s*\/>'
    matches = re.compile(patron, re.DOTALL).findall(data)
	
    for scrapedurl, scrapedthumbnail, scrapedtitle   in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("Film Streaming Ita", "")
		
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if "serie" in scrapedurl else "findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='tv' if "serie" in scrapedurl else "movie"))
				 
    # Paginación
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"><i class="td-icon-menu-right"></i>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==============================================================================================================================================================================

def peliculas_update(item):
    logger.info("pureita solostreaming_co peliculas_update")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	
    patron = '<div class="td_module_16 td_module_wrap td-animation-stack">\s*<div class="td-module-thumb">'
    patron += '<a href="([^"]+)" rel="bookmark" title="([^<]+)">[^>]+class="entry-thumb"\s*[^>]+src="([^<]+)" alt[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)
	
    for scrapedurl, scrapedtitle, scrapedthumbnail  in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("Film Streaming Ita", "")
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if "serie" in scrapedurl or "stagioni" in scrapedurl else "findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='tv' if "serie" in scrapedurl else "movie"))
				 
    # Paginación
    next_page = scrapertools.find_single_match(data, '<a href="([^"]+)"><i class="td-icon-menu-right"></i>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==============================================================================================================================================================================
	
def episodios(item):
    logger.info("pureita solostreaming_co episodios")

    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data


    patron = '<a\s*href="([^"]+)" target="_blank" rel="noopener">([^>]+>[^>]+)>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if "Fonte" in scrapedtitle: 
		    continue
        scrapedtitle = scrapedtitle.replace("/", "")
        scrapedtitle = scrapedtitle.replace(">", "")
        scrapedtitle = scrapedtitle.replace("strong", "")
        scrapedtitle = scrapedtitle.replace("<a", "")
        scrapedtitle = scrapedtitle.replace("<", "")
        scrapedtitle = scrapedtitle.replace("Cassetta", "")
        scrapedtitle = scrapedtitle.replace("span style=", "")
        scrapedtitle = scrapedtitle.replace("color:", "")
        scrapedtitle = scrapedtitle.replace("#ff0000;", "")
        scrapedtitle = scrapedtitle.replace('"', "")			
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    patron = '<a\s*href="([^"]+)"><strong>(.*?)<\/strong>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if "Fonte" in scrapedtitle: 
		    continue
        scrapedtitle = scrapedtitle.replace("/", "")
        scrapedtitle = scrapedtitle.replace(">", "")
        scrapedtitle = scrapedtitle.replace("strong", "")
        scrapedtitle = scrapedtitle.replace("<a", "")
        scrapedtitle = scrapedtitle.replace("<", "")
        scrapedtitle = scrapedtitle.replace("Cassetta", "")
        scrapedtitle = scrapedtitle.replace("span style=", "")
        scrapedtitle = scrapedtitle.replace("color:", "")
        scrapedtitle = scrapedtitle.replace("#ff0000;", "")
        scrapedtitle = scrapedtitle.replace('"', "")			
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 

    return itemlist


# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("[pureita solostreaming_co] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return peliculas_update(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


	




