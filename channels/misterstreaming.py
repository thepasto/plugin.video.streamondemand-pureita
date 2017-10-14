# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale misterstreaming
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse

from core import config, httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod


__channel__ = "misterstreaming"
__category__ = "F,S"
__type__ = "generic"
__title__ = "misterstreaming (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.misterstreaming.click/"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host],
    ['Cache-Control', 'max-age=0']
]

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.istreaming mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film -[COLOR orange] Ultimi Inseriti[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%s/category/film/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film -[COLOR orange] Al Cinema[/COLOR]",
                     extra="movie",
                     action="peliculas",
                     url="%s/category/film/al-cinema/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film -[COLOR orange] Altadefinizione[/COLOR]",
                     extra="movie",
                     action="peliculas",
                     url="%s/category/film/altadefinizione/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Fiction[/COLOR]",
                     extra="movie",
                     action="peliculas_fiction",
                     url="%s/category/fiction/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                #Item(channel=__channel__,
                     #title="[COLOR azure]Film Per Categoria[/COLOR]",
                     #action="categorias",
                     #url=host,
                     #thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     extra="serie",
                     action="peliculas_fiction",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==============================================================================================================================================

def categorias(item):
    itemlist = []

    # Descarga la pagina
    data = scrapertools.anti_cloudflare(item.url, headers)
    bloque = scrapertools.get_match(data, '<div id="categories-2" class="widget widget_categories">(.*?)</ul>')

    # Extrae las entradas (carpetas)
    patron = '<li[^>]+><a href="([^"]+)"[^>]+>(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if (DEBUG): logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================

def search(item, texto):
    logger.info("streamondemand.misterstreaming " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        if item.extra == "movie":
            return peliculas(item)
        if item.extra == "serie":
            return peliculas_fiction(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==============================================================================================================================================
		

def peliculas(item):
    logger.info("streamondemand.misterstreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.anti_cloudflare(item.url, headers)

    # Extrae las entradas (carpetas)
    patron = '<figure class="post-image ">\s*<a href="(.*?)"><img src="(.*?)" class=[^=]+=[^=]+="(.*?)" /></a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedplot = ""
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos_movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<span class="number current">[^<]+</span>[^<]+<a href="(.*?)" class="number">'
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

# ==============================================================================================================================================
	
def peliculas_fiction(item):
    logger.info("streamondemand.misterstreaming peliculas_tv")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.anti_cloudflare(item.url, headers)

    # Extrae las entradas (carpetas)
    patron = '<figure class="post-image ">\s*<a href="(.*?)"><img src="(.*?)" class=[^=]+=[^=]+="(.*?)" /></a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedplot = ""
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<span class="number current">[^<]+</span>[^<]+<a href="(.*?)" class="number">'
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
                 action="peliculas_fiction",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/successivo_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================

def peliculas_tv(item):
    logger.info("streamondemand.misterstreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<div id="text-2" class="widget widget_text">(.*?)<div id="footerwrap">')

    # Extrae las entradas (carpetas) 
    patron = '<a href="(.*?)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<span class="number current">[^<]+</span>[^<]+<a href="(.*?)" class="number">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist	
	
# ==============================================================================================================================================	

def episodios(item):
    def load_episodios(html, item, itemlist, lang_title):
        patron = '.*?<a href="[^"]+"[^o]+o[^>]+>[^<]+<\/a><(?:b|\/)[^>]+>'
        matches = re.compile(patron).findall(html)
        for data in matches:
            # Contenuti 
            scrapedtitle = data.split('<a ')[0]
            scrapedtitle = re.sub(r'<[^>]*>', '', scrapedtitle).strip()
            if scrapedtitle != 'Categorie':
                scrapedtitle = scrapedtitle.replace('&#215;', 'x')
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos_tv",
                         contentType="episode",
                         title="[COLOR azure]%s[/COLOR]" % (scrapedtitle + " (" + lang_title + ")"),
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         fulltitle=scrapedtitle + " (" + lang_title + ")" + ' - ' + item.show,
                         show=item.show))

    logger.info("[misterstreaming.py] episodios")

    itemlist = []

    # Pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    data = scrapertools.decodeHtmlentities(data)
    data = scrapertools.get_match(data, '<div class="entry-content">(.*?)<p class="post-meta entry-meta">')

    lang_titles = []
    starts = []
    patron = r"Stagione.*?ITA"
    matches = re.compile(patron, re.IGNORECASE).finditer(data)
    for match in matches:
        season_title = match.group()
        if season_title != '':
            lang_titles.append('SUB ITA' if 'SUB' in season_title.upper() else 'ITA')
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

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))

    return itemlist

# ==============================================================================================================================================	
	
def findvideos_tv(item):
    logger.info("streamondemand.misterstreaming findvideos_tv")

    data = item.url

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

# ==============================================================================================================================================
	
def findvideos_movie(item):
    logger.info("streamondemand.misterstreaming findvideos_movie")

    data = scrapertools.anti_cloudflare(item.url, headers)

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

# ==============================================================================================================================================
	
def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand-pureita-master)")

