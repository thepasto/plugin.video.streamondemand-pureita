# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-pureita / XBMC Plugin
# Canal majintoon
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import re
import urlparse

from core import config
from core import logger
from core import servertools
from core import httptools
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "majintoon"
host = "https://majintoon.wordpress.com"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita majintoon mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Anime [COLOR orange]- Lista[/COLOR]",
                     action="lista_animation",
                     url=host + "/category/anime/",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime [COLOR orange]- Sub-ITA[/COLOR]",
                     action="lista_animation",
                     url=host + "/category/anime-sub-ita/",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_sub_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Animazione [COLOR orange]- Bambini[/COLOR]",
                     action="lista_animation",
                     url=host + "/category/per-tutti/",
                     extra="tv",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation_P.png"),
	            Item(channel=__channel__,
                     action="categorie",
                     title="[COLOR azure]Anime & Serie TV [COLOR orange]- Cetegorie[/COLOR]",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_genre_P.png"),              
                Item(channel=__channel__,
                     title="[COLOR azure]Anime [COLOR orange]- Film Animation[/COLOR]",
                     action="lista_animation",
                     extra="movie",
                     url="%s/category/film-animazione/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animated_movie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="lista_animation",
                     url=host + "/category/serie-tv/",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca ...[/COLOR]",
                     action="search",
                     extra="anime",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ===================================================================================================================================================

def search(item, texto):
    logger.info("streamondemand-pureita majintoon " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        return lista_animation(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ===================================================================================================================================================

def categorie(item):
    logger.info("streamondemand-pureita majintoon categorie")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
	
    blocco = scrapertools.get_match(data, r'Categorie</a>\s*<ul\s*class="sub-menu">(.*?)</ul>\s*</li>')
    patron = r'<li[^>]+><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
                Item(channel=__channel__,
                     action="lista_animation",
                     title=scrapedtitle,
                     url=scrapedurl,
                     extra="tv",
                     thumbnail=item.thumbnail,
                     folder=True))

    return itemlist

# ===================================================================================================================================================

def lista_animation(item):
    logger.info("streamondemand-pureita majintoon lista_animation")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<figure class="post-image">\s*<a title="([^"]+)" href="([^"]+)">'
    patron += r'\s*<img.*?src="([^"]*)".*?/>\s*</a>\s*</figure>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl, scrapedthumbnail in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="peliculas_server",
                 contentType="tv",
                 title=scrapedtitle,
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 extra="tv",
                 thumbnail=scrapedthumbnail,
                 folder=True), tipo="tv"))
				 
    # Extrae el paginador
    patron = '<div class="nav-previous"><a href="([^"]+)" >'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = matches[0]
        itemlist.append(
            Item(channel=__channel__,
                 action="lista_animation",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# ===================================================================================================================================================

def peliculas_server(item):
    logger.info("streamondemand-pureita majintoon peliculas_server")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    patron = r'Link?\s*([^<]+)"><\/.*?><br \/>\s*(.*?)<\/p>'
    list = scrapertools.find_multiple_matches(data, patron)
    if not len(list) > 0:
        patron = r'<span style="[^"]+">Link\s*([^<]+)</span><br />(.*?)<\/p>'
        list = scrapertools.find_multiple_matches(data, patron)
    for scrapedtitle, link in list:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("0", "[COLOR yellow] - [/COLOR]")
        itemlist.append(
            Item(channel=__channel__,
                 action="episodes",
                 title="[COLOR azure]Riproduci con " + "[COLOR orange]" + scrapedtitle + "[/COLOR]",
                 url=link,
                 extra=scrapedtitle,
                 thumbnail=item.thumbnail,
                 folder=True))

    return itemlist

# ===================================================================================================================================================

def episodes(item):
    logger.info("streamondemand-pureita majintoon episodes")
    itemlist = []
	
    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<a href="([^"]+)"\s*target="_blank"\s*rel[^>]+>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedtitle in matches:
        if 'Wikipedia' not in scrapedurl:
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).replace("×", "x")
            scrapedtitle = scrapedtitle.replace("_", " ")
            scrapedtitle = scrapedtitle.replace(".mp4", "")
            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     contentType="tv",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     thumbnail=item.thumbnail,
                     fulltitle=scrapedtitle,
                     url=scrapedurl,
                     show=item.show,
                     extra="tv",
                     folder=True))
	
    patron = r'<a href="([^"]+)"\s*target="_blank"[^>]+>[^>]+>[^>]+>[^>]+>\s*[^>]+>([^<]+)[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl, scrapedtitle in matches:
        if 'Wikipedia' not in scrapedurl:
            scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).replace("×", "x")
            scrapedtitle = scrapedtitle.replace("_", " ")
            scrapedtitle = scrapedtitle.replace(".mp4", "")
            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     contentType="tv",
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     fulltitle=scrapedtitle,
                     url=scrapedurl,
                     extra="tv",
                     show=item.show,
                     thumbnail=item.thumbnail,
                     folder=True))
	
    return itemlist

# ===================================================================================================================================================

def findvideos(item):
    logger.info("streamondemand-pureita majintoon findvideos")
    itemlist = servertools.find_video_items(data=item.url)
    
    for videoitem in itemlist:
        videoitem.channel = __channel__
        server = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR orange] ' + "[[B]" + server + "[/B]] " + item.title + '[/COLOR]'])
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show

    return itemlist





