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

headers = [['Referer', host]]


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
                     action="peliculas_serie",
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

    patron = 'Seleziona una categoria</option>(.*?)</select></form>'
    data = scrapertools.find_single_match(data, patron)

    patron = '<option class=".*?" value=".*?">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedtitle in matches:
        if "Anime " in scrapedtitle or "Serie Tv" in scrapedtitle or "Apocalittico" in scrapedtitle:
		   continue
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title=scrapedtitle,
                 url="".join([host, scrapedtitle.lower()]),                 
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
                 action="episodios" if "serie" in scrapedurl or "stagioni" in scrapedurl or "Anime" in scrapedtitle else "findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='tv' if "serie" in scrapedurl or "stagioni" in scrapedurl or "Anime" in scrapedtitle else "movie"))
				 
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
                 action="episodios" if "serie" in scrapedurl or "stagioni" in scrapedurl or "Anime" in scrapedtitle else "findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='tv' if "serie" in scrapedurl or "stagioni" in scrapedurl or "Anime" in scrapedtitle else "movie"))

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

def peliculas_serie(item):
    logger.info("pureita solostreaming_co peliculas")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = '<a\s*href="([^"]+)"[^>]+title="([^"]+)"><img[^>]+src="([^"]+)" alt[^>]+/>'
    matches = re.compile(patron, re.DOTALL).findall(data)
	
    for scrapedurl, scrapedtitle, scrapedthumbnail,    in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("Film Streaming Ita", "")		
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if "serie" in scrapedurl or "stagioni" in scrapedurl or "Anime" in scrapedtitle else "findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='tv' if "serie" in scrapedurl or "stagioni" in scrapedurl or "Anime" in scrapedtitle else "movie"))
				 
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

    patron = '<a\s*href="([^"]+)"><strong>(.*?)<\/strong>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if "Fonte" in scrapedtitle or "Forum" in scrapedtitle:
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
				 
    patron = '<a href="([^"]+)"\s*target[^>]+>.*?([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        if "Fonte" in scrapedtitle or "Forum" in scrapedtitle or "br />" in scrapedtitle: 
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


	




