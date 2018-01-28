# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale itflix_stream
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

__channel__ = "itflix_stream"
host = "https://www.itflix.stream"
headers = [['Referer', host]]

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand-pureita [itflix_stream mainlist]")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas_list",
                     url="%s/film/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Categorie[/COLOR]",
                     action="genere",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Anno[/COLOR]",
                     action="year",
                     url="%s/film/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png"),
	            Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Popolari[/COLOR]",
                     action="peliculas",
                     url="%s//piu-popolari/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Raccomandati[/COLOR]",
                     action="peliculas",
                     url="%s/i-piu-votati/" %host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita itflix_stream] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return peliculas_search(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==============================================================================================================================================================================

def peliculas_search(item):
    logger.info("streamondemand-pureita [itflix_stream peliculas_search]")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	
    patron = '<div class="thumbnail animation-2"><a href="([^"]+)">\s*'
    patron += '<img src="([^"]+)"\s*alt="([^<]+)">.*?'
    patron += '<p>(.*?)</p>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot  in matches:
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=host+scrapedurl,
                 thumbnail=host+scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle), tipo='movie'))

    return itemlist		

# ==============================================================================================================================================================================		

def genere(item):
    logger.info("streamondemand-pureita [itflix_stream genere]")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<li id="menu-item-.*?" class="menu-item menu-item-type-taxonomy menu-item-object-genres menu-item-.*?">'
    patron += '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=host+scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================

def year(item):
    logger.info("streamondemand-pureita [itflix_stream genere]")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<h2>Anno di rilascio</h2>(.*?)</ul>')
	
    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=host+scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================

def peliculas(item):
    logger.info("streamondemand-pureita [itflix_stream peliculas]")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	
    patron = '<img src="([^"]+)"\s*alt="[^>]+"><div class="rating">[^>]+><\/span>\s*([^"]+)<\/div>'
    patron += '<div class="mepo"><span class="quality">[^>]+<\/span><\/div><a href="[^>]+>'
    patron += '<div class="see"><\/div><\/a><\/div><div class="data"><h3>'
    patron += '<a href="([^"]+)">([^>]+)<\/a><\/h3>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapedplot=""
    for scrapedthumbnail, rating, scrapedurl, scrapedtitle in matches:
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=host+scrapedurl,
                 thumbnail=host+scrapedthumbnail,
                 plot=scrapedplot,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo='movie'))

    # Extrae el paginador
    paginador = scrapertools.find_single_match(data, '<a href="([^"]+)"><span class="icon-chevron-right">')
    if paginador != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=host+paginador,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==============================================================================================================================================================================

def peliculas_list(item):
    logger.info("streamondemand-pureita [itflix_stream peliculas_list]")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	
    patron = '<img src="([^"]+)"\s*alt="[^>]+"><div class="rating">[^>]+><\/span>\s*([^"]+)<\/div><div class="mepo">.*?'
    patron += '<div class="data"><h3><a href="([^"]+)">[^>]+<\/a><\/h3><span>.*?'
    patron += '<\/span><\/div><div class=".*?"><div class="title"><h4>([^<]+)<\/h4>.*?'
    patron += '<div class="texto">([^<]+)<\/div>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, rating, scrapedurl, scrapedtitle, scrapedplot in matches:
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle + " [[COLOR yellow]" + rating + "[/COLOR]]",
                 thumbnail=host+scrapedthumbnail,
                 url=host+scrapedurl,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle), tipo='movie'))

    # Extrae el paginador
    paginador = scrapertools.find_single_match(data, '<a href="([^"]+)"><span class="icon-chevron-right">')
    if paginador != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=host+paginador,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==============================================================================================================================================================================

		
def findvideos(item):
    logger.info("streamondemand-pureita [itflix_stream  findvideos]")
    data = httptools.downloadpage(item.url, headers=headers).data

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR orange]' + videoitem.title + '[/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist



