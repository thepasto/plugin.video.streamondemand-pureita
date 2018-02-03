# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale  TheLordOfStreaming
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

__channel__ = "thelordofstreaming"
host = "http://www.thelordofstreaming.it/"
headers = [['Referer', host]]

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand-pureita [TheLordOfStreaming mainlist]")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas",
                     url="%s/category/movie/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Wrestling[COLOR orange] - Novita[/COLOR]",
                     action="peliculas",
                     url="%s/category/wrestling/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Lista[/COLOR]",
                     action="peliculas_tv",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Ultimi Episodi[/COLOR]",
                     action="peliculas_new",
                     url=host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]


    return itemlist

# ==============================================================================================================================================================================
	
def search(item, texto):
    logger.info("[streamondemand-pureita TheLordOfStreaming] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto + "&submit=Cerca"
    try:
        if item.extra == "movie":
            return peliculas(item)
        if item.extra == "serie":
            return peliculas_search(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==============================================================================================================================================================================		
		
def peliculas(item):
    logger.info("streamondemand-pureita [TheLordOfStreaming peliculas]")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h1 class="entry-title"><a href="([^"]+)"\s*rel="bookmark">([^<]+)<\/a><\/h1>.*?'
    patron += '<img class=".*?"\s*src="([^"]+)"[^>]+>([^"]+)>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:

        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedplot = scrapedplot.replace("/", "")
        scrapedplot = scrapedplot.replace("<em>", "")
        scrapedplot = scrapedplot.replace("<h1>", "")
        scrapedplot = scrapedplot.replace("<a>", "")
        scrapedplot = scrapedplot.replace("<p>", "")
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

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" ><span class="meta-nav">&larr;</span> Articoli più vecchi</a></div>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================

def peliculas_new(item):
    logger.info("streamondemand-pureita [TheLordOfStreaming peliculas]")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h1 class="entry-title"><a href="([^"]+)" rel="bookmark">([^&]+)([^<]+)</a></h1>\s*'
    patron += '<div class=".*?">\s*<.*?<time class[^>]+>(.*?)</time>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:

        scrapeddata = scrapertools.unescape(match.group(4))
        scrapedep = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedep = scrapedep.replace('SUBITA', 'SUB')
        scrapedplot = ""
        scrapedthumbnail = ""
        if "Girada" in scrapedtitle:
		    continue
        if "WWE" in scrapedtitle:
		    continue
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle+"[COLOR aquamarine]"+scrapedep+" &#8211; "+"[COLOR yellow]"+scrapeddata+"[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" ><span class="meta-nav">&larr;</span> Articoli più vecchi</a></div>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_new",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================		

def peliculas_tv(item):
    logger.info("streamondemand-pureita [TheLordOfStreaming peliculas_tv]")
    itemlist = []
    PERPAGE = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas
    patron = '<li><a href="([^"]+)">([^<]+)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedurl, scrapedtitle ) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail=""
        scrapedplot=""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 contentType="tv",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
				 
    # Extrae el paginador 
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# ==============================================================================================================================================================================

def peliculas_search(item):
    logger.info("streamondemand-pureita [TheLordOfStreaming peliculas]")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h1 class="entry-title"><a href="([^"]+)" rel="bookmark">([^&]+)([^<]+)</a></h1>\s*'
    patron += '<div class=".*?">\s*<.*?<time class[^>]+>.*?</time>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedep = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedep = scrapedep.replace('SUBITA', 'SUB')
        scrapedplot = ""
        scrapedthumbnail = ""
        if "Girada" in scrapedtitle:
		    continue
        if "Serie TV" not in scrapedep:
		   continue
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle+"[COLOR aquamarine]"+scrapedep+"&#8211;"+"[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
    return itemlist

# ==============================================================================================================================================================================

def episodios(item):
    def load_episodios(html, item, itemlist, lang_title):
        patron = '((?:.*?<a href="[^"]+" class="external" rel="nofollow" target="_blank">[^<]+</a>)+)'
        matches = re.compile(patron).findall(html)

        for data in matches:
            scrapedtitle = data.split('<a ')[0]
            scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle).strip()
            if scrapedtitle != 'Film':
                scrapedtitle = scrapedtitle.replace('&#215;', ' X ')
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos",
                         contentType="episode",
                         title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " (" + lang_title + ")"),
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         fulltitle=scrapedtitle + " (" + lang_title + ")" + ' &#8212;' + item.show,
                         show=item.show))

    logger.info("streamondemand-pureita [TheLordOfStreaming episodios]")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data
    data = scrapertools.decodeHtmlentities(data)

    lang_titles = []
    starts = []
    patron = r'.*?Stagione</em></strong> <span style=".*?">.*?</span><br />'
    matches = re.compile(patron, re.IGNORECASE).finditer(data)
    for match in matches:
        season_title = match.group()
        if season_title != '':
            lang_titles.append('SUBITA' if 'SUB' in season_title.upper() else 'ITA')
            starts.append(match.end())

    i = 1
    len_lang_titles = len(lang_titles)

    while i <= len_lang_titles:
        inizio = starts[i - 1]
        fine = starts[i] if i < len_lang_titles else -1

        html = data[inizio:fine]
        lang_title = lang_titles[i - 1]

        load_episodios(html, item, itemlist, lang_title)

        i += 1

    return itemlist

# ==============================================================================================================================================================================
		
def findvideos(item):
    logger.info("streamondemand-pureita.altadefinizioneclub findvideos")
	
    # Descarga la pagina 
    data = item.url if item.extra == 'serie' else httptools.downloadpage(item.url).data

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join([item.title, '[COLOR orange][B]' + videoitem.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist


