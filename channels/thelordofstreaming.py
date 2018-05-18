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
host = "http://www.thelordofstreaming.it"
headers = [['Referer', host]]

def isGeneric():
    return True

def mainlist(item):
    logger.info("[streamondemand-pureita TheLordOfStreaming] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure][B]Film[COLOR orange][B] - Novita'[/B][/COLOR]",
                     action="peliculas",
                     url="%s/category/movie/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure][B]Wrestling[COLOR orange][B] - Novita'[/B][/COLOR]",
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
                     title="[COLOR azure][B]Serie TV[COLOR orange][B] - Lista[/B][/COLOR]",
                     action="peliculas_tv",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure][B]Serie TV[COLOR orange][B] - Archivio[/B][/COLOR]",
                     action="peliculas_list",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure][B]Serie TV[COLOR orange][B] - Ultimi Episodi[/B][/COLOR]",
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

# ==================================================================================================================================================
	
def search(item, texto):
    logger.info("[streamondemand-pureita TheLordOfStreaming] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto + "&submit=Cerca"
    try:
        if item.extra == "serie":
            return peliculas_srctv(item)
        else:
            return peliculas_srcmovie(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================		
		
def peliculas(item):
    logger.info("[streamondemand-pureita TheLordOfStreaming] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h1 class="entry-title"><a href="([^"]+)"\s*rel="bookmark">([^<]+)<\/a><\/h1>.*?'
    patron += '<img class=".*?"\s*src="([^"]+)" alt[^>]+[^A-Z]+(.*?)<\/'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(4))
        scrapedthumbnail = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedthumbnail = scrapedthumbnail.replace("-–-", "-%E2%80%93-")
        scrapedthumbnail = scrapedthumbnail.replace("’", "%E2%80%99")
        scrapedthumbnail = scrapedthumbnail.replace("à", "%C3%A0")
        scrapedtitle = scrapedtitle.replace("’", "").replace(" & ", " e ")
        scrapedplot = scrapedplot.replace("/", "").replace("<em>", "")
        scrapedplot = scrapedplot.replace("<h1>", "").replace("<a>", "")
        scrapedplot = scrapedplot.replace("<p>", "").replace("a>", "")

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
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_srcmovie(item):
    logger.info("[streamondemand-pureita TheLordOfStreaming] peliculas_srcmovie")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = '<h1 class="entry-title"><a href="([^"]+)" rel="bookmark">(.*?)</a></h1>.*?<p>(.*?)<'
    patron += '.*?rel="category tag">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle, scrapedplot, category in matches:
        if not "Movie" in category:
          continue

        scrapedthumbnail=""
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 fulltitle=title,
                 show=title,
                 folder=True), tipo="movie"))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" ><span class="meta-nav">&larr;</span> Articoli più vecchi</a></div>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_srcmovie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================

def peliculas_srctv(item):
    logger.info("[streamondemand-pureita TheLordOfStreaming] peliculas_srctv")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = '<h1 class="entry-title"><a href="([^"]+)" rel="bookmark">(.*?)</a></h1>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        if not "Serie TV" in scrapedtitle:
          continue
        scrapedplot=""
        scrapedthumbnail=""
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 fulltitle=title,
                 show=title,
                 folder=True), tipo="tv"))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" ><span class="meta-nav">&larr;</span> Articoli più vecchi</a></div>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_srctv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
# ==================================================================================================================================================

def peliculas_new(item):
    logger.info("[streamondemand-pureita TheLordOfStreaming] peliculas_new")
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
        if "Girada" in scrapedtitle or "WWE" in scrapedtitle:
		    continue
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle+"[COLOR aquamarine]"+ scrapedep + " - [COLOR yellow]" + scrapeddata + "[/COLOR]",
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
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_list(item):
    logger.info("[streamondemand-pureita TheLordOfStreaming] peliculas_list")
    itemlist = []	
    PERPAGE = 300
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<h1 class="entry-title">Serie TV</h1>(.*?)<h2 id="comments-title">')

    # Estrae i contenuti 
    patron = '<[^<]+href="([^>]+)">([^<]+)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)
    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break

        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 title=title,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png",
                 fulltitle=title,
                 show=title,
                 folder=True))

    # Extrae el paginador
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
# ==================================================================================================================================================

def peliculas_tv(item):
    logger.info("[streamondemand-pureita TheLordOfStreaming] peliculas_tv]")
    itemlist = []
    PERPAGE = 14
	
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<h1 class="entry-title">Serie TV</h1>(.*?)<h2 id="comments-title">')
    # Extrae las entradas
    patron = '<[^<]+href="([^>]+)">([^<]+)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for i, (scrapedurl, scrapedtitle ) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedtitle = scrapedtitle.replace("&#8211;", "-")
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
	
# ==================================================================================================================================================

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
                         title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " [" + lang_title + "]"),
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         fulltitle=scrapedtitle + " (" + lang_title + ")" + ' &#8212;' + item.show,
                         show=item.show))

    logger.info("[streamondemand-pureita TheLordOfStreaming] episodios")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data
    data = scrapertools.decodeHtmlentities(data)

    lang_titles = []
    starts = []
    patron = r'Stagione'
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

# ==================================================================================================================================================
		
def findvideos(item):
    logger.info("[streamondemand-pureita TheLordOfStreaming] findvideos")
	
    # Descarga la pagina 
    data = item.url if item.extra == 'serie' else httptools.downloadpage(item.url).data

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join(['[COLOR orange][B]' + videoitem.title, '[COLOR azure] - ' + item.title + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
