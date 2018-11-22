# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale  eurostreaming_video
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ============================================================
import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "eurostreaming_video"
host = "https://www.eurostreaming.band"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita.eurostreaming_video mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Novita[/COLOR]",
                     action="peliculas_new",
                     extra='movie',
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Lista[/COLOR]",
                     action="peliculas",
                     extra='movie',
                     url="%s/category/films/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movies_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Aggiornate[/COLOR]",
                     action="serietv_new",
                     extra='serie',
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Lista[/COLOR]",
                     action="serietv",
                     extra='serie',
                     url="%s/category/serie/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Animazione[/COLOR]",
                     action="animation_new",
                     extra='serie',
                     url="%s/category/anime-cartoni-animati/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Richieste[/COLOR]",
                     action="peliculas_requested",
                     extra='serie',
                     url="%s/category/serie/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     extra='serie',
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================
	
def peliculas(item):
    logger.info("[streamondemand-pureita.eurostreaming_video] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a\s*[^>]+ href="([^"]+)">\s*<img\s*class="img-responsive " title="([^"]+)" alt=".*?" src="([^<]+)" />'
    patron += '<div\s*class="boxinfolocand"><h2>[^<]+</h2>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedtitle = scrapedtitle.replace("locandina film", "")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<a\s*class="nextpostslink" rel="next" href="([^"]+)">Avanti »</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_new(item):
    logger.info("[streamondemand-pureita.eurostreaming_video] peliculas_new")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	
    # Narrow search by selecting only the combo
    bloque = scrapertools.get_match(data, '<h2>Ultimi Film inseriti</h2>([^+]+)<div\s*class="w-sidebar-container">')

    # Extrae las entradas (carpetas)
    patron = '<a\s*[^>]+ href="([^"]+)">\s*<img\s*class="img-responsive " title="([^"]+)" alt=".*?" src="([^<]+)" />'
    patron += '<div\s*class="boxinfolocand"><h2>[^<]+</h2>'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("locandina film", "")
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='movie'))

    return itemlist
# ==================================================================================================================================================
	
def serietv(item):
    logger.info("[streamondemand-pureita.eurostreaming_video] serietv")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<h2>Archivio SERIE TV</h2>(.*?)<div\s*class="w-sidebar-container">')

    # Extrae las entradas (carpetas)
    patron = '<a\s*[^>]+[^>][^>]href="([^"]+)">\s*[^>]+ alt="([^>]+)"\s*src="([^>]+)" />'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("locandina", "")
        scrapedtitle = scrapedtitle.replace("serie tv", "")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="cat_ep",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a\s*class="nextpostslink" rel="next" href="([^"]+)">Avanti »</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="serietv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def serietv_new(item):
    logger.info("[streamondemand-pureita.eurostreaming_video] serietv_new")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, 'Ultimi aggiornamenti Serie TV([^+]+)<a\s*href="[^"]+"> Tutte le Serie TV >> </a>')

    # Extrae las entradas (carpetas)
    patron = '<a\s*[^>]+[^>][^>]href="([^"]+)">\s*[^>]+ alt="([^>]+)"\s*src="([^>]+)" />'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("locandina", "")
        scrapedtitle = scrapedtitle.replace("serie tv", "")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="cat_ep",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    return itemlist

# ==================================================================================================================================================

def animation_new(item):
    logger.info("[streamondemand-pureita.eurostreaming_video] animation_new")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    bloque = scrapertools.get_match(data, '<h2>Archivio ANIME E CARTONI<\/h2>([^+]+)')

    # Extrae las entradas (carpetas)
    patron = '<a\s*[^>]+[^>][^>]href="([^"]+)">\s*[^>]+ alt="([^>]+)"\s*src="([^>]+)" />'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("locandina", "")
        scrapedtitle = scrapedtitle.replace("serie tv", "")
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="cat_ep",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a\s*class="nextpostslink" rel="next" href="([^"]+)">Avanti »</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="animation_new",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 extra=item.extra,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_requested(item):
    logger.info("[streamondemand-pureita.eurostreaming_video] peliculas_requested")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, 'Le serie più viste di questo mese:</h3>(.*?)<div\s*class="container-fluid wrap-cont-footer">')

    # Extrae las entradas (carpetas)
    patron = '<a\s*[^>]+[^>][^>]href="([^"]+)">\s*[^>]+ alt="([^>]+)"\s*src="([^>]+)" />'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("locandina", "")
        scrapedtitle = scrapedtitle.replace("serie tv", "")
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="cat_ep",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    return itemlist
	
# ==================================================================================================================================================	
	
def cat_ep(item):
    logger.info("[streamondemand-pureita.eurostreaming_video] cat_ep")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<div\s*class="su-link-ep">\s*<a\s*rel="nofo[^>]+\s*'
    patron += 'href="[^>]+" newlink="([^"]+)" class="green-link">\s*([^<]+)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("locandina film", "")
        scrapedtitle = scrapedtitle.replace("          ", "")
        scrapedtitle = scrapedtitle.replace("<strong>", "")
        scrapedtitle = scrapedtitle.replace("</strong>", "")		
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange][B]" + item.fulltitle + "[/B][/COLOR] " + item.plot,
                 extra=item.extra,
                 folder=True))

    patron = '<div\s*class="su-link-ep">\s*<a\s*rel[^>]+  href="[^>]+" newlink="([^"]+)" class="green-link">\s*'
    patron += '<strong>\s*([^<]+)</strong>([^<]+)</a> '

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedep, scrapedepi in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedtitle = scrapedep + scrapedepi
        scrapedtitle = scrapedtitle.replace("locandina film", "")
        scrapedtitle = scrapedtitle.replace("          ", "")
        scrapedtitle = scrapedtitle.replace("<strong>", "")
        scrapedtitle = scrapedtitle.replace("</strong>", "")		
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange][B]" + item.fulltitle + "[/B][/COLOR] " + item.plot,
                 extra=item.extra,
                 folder=True))
				 
				 
    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita.eurostreaming_video ] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        if item.extra == "serie":
            return peliculas_search(item)
        if item.extra == "movie":
            return peliculas_search(item)			
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
		
# ==================================================================================================================================================		

def peliculas_search(item):
    logger.info("[streamondemand-pureita.eurostreaming_video] peliculas_search")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<a\s*href="([^>]+)"> <img\s*class="img-responsive "\s*'
    patron += 'title="([^>]+)"\s*alt="[^>]+" src="([^"]+)" />'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapedtitle.replace("locandina", "")
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="cat_ep" if "serie tv" in scrapedtitle else "findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv' if "serie tv" in scrapedtitle else "movie"))

    return itemlist


