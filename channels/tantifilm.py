# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-pureita / XBMC Plugin
# Canale Tantifilm
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import base64
import re
import urlparse

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod


__channel__ = "tantifilm"
host = "http://www.tantifilm.uno"

headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Referer', host]]

def isGeneric():
    return True

def mainlist(item):
    logger.info("streamondemand.tantifilm mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Cinema[/COLOR]",
                     action="peliculas",
                     url="%s/watch-genre/al-cinema/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
	            Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),                                    
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Alta Definizione[/COLOR]",
                     action="peliculas",
                     url="%s/watch-genre/altadefinizione/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,	 
                     title="[COLOR azure]Film[COLOR orange] - 3D[/COLOR]",
                     action="peliculas",
                     url=host+"/watch-genre/3d/",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_3D_P.png"),
               Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film ...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Lista[/COLOR]",
                     extra="serie",
                     action="peliculas_tv",
                     url="%s/watch-genre/series-tv-featured/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV [COLOR orange] - Mini Serie[/COLOR]",
                     extra="serie",
                     action="peliculas_tv",
                     url="%s/watch-genre/miniserie/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV ...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist


# ==============================================================================================================================================================================
	
def categorias(item):
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '</span>Anime</a></li>(.*?)</ul>')

    # Extrae las entradas
    patron = "<li><a href='(.*?)'><span></span>(.*?)</a>"
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if "Serie" in scrapedtitle or "Miniserie" in scrapedtitle:
               continue
         
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================

def peliculas(item):
    logger.info("streamondemand-pureita [tantifilm peliculas}")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	

    patron = '<div class="mediaWrap mediaWrapAlt"><a href="([^"]+)">'
    patron += '<img[^>]+src="([^"]+)"\s*class[^>]+[^>]+></a><div[^>]+>[^>]+><p>([^<]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        if not "https:" in scrapedthumbnail:
          scrapedthumbnail = "https:" + scrapedthumbnail
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle=scrapedtitle.replace("streaming", "")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo="movie"))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)">»</a>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist


# ==============================================================================================================================================================================

def peliculas_tv(item):
    logger.info("streamondemand-pureita [tantifilm peliculas}")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	

    patron = '<div class="mediaWrap mediaWrapAlt"><a href="([^"]+)">'
    patron += '<img[^>]+src="([^"]+)"\s*class[^>]+[^>]+></a><div[^>]+>[^>]+><p>([^<]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        if not "https:" in scrapedthumbnail:
          scrapedthumbnail = "https:" + scrapedthumbnail
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle=scrapedtitle.replace("streaming", "")
        scrapedtitle=scrapedtitle.replace("-)", ")")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo="tv"))

    # Paginación
    next_page = scrapertools.find_single_match(data, '<a class="nextpostslink" rel="next" href="([^"]+)">»</a>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist


# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita tantifilm.py] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto

    try:
        if item.extra == "movie":
            return peliculas_search(item)
        else:
            return peliculas_searchtv(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
# ==============================================================================================================================================================================

def peliculas_search(item):
    logger.info("streamondemand-pureita [tantifilm search_peliculas]")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	

    patron = '<div class="image-film image-film-2">\s*'
    patron += '<a href="([^"]+)"\s*title="(.*?)"\s*rel="bookmark">\s*<img[^>]+src="([^"]+)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        if not "http:" in scrapedthumbnail:
         scrapedthumbnail = "http:" + scrapedthumbnail
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle=scrapedtitle.replace("streaming", "")
        scrapedtitle=scrapedtitle.replace("Permalink to", "")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo="movie"))

    return itemlist

# ==============================================================================================================================================================================

def peliculas_searchtv(item):
    logger.info("streamondemand-pureita [tantifilm search_peliculas_tv]")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	

    patron = '<div class="image-film image-film-2">\s*'
    patron += '<a href="([^"]+)"\s*title="(.*?)"\s*rel="bookmark">\s*<img[^>]+src="([^"]+)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        if not "https:" in scrapedthumbnail:
          scrapedthumbnail = "https:" + scrapedthumbnail
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle=scrapedtitle.replace("streaming", "")
        scrapedtitle=scrapedtitle.replace("Permalink to", "")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle), tipo="tv"))

    return itemlist

# ==============================================================================================================================================================================

def episodios(item):
    def load_episodios(html, item, itemlist):
        for data in html.splitlines():
            # Extrae las entradas
            end = data.find('<a ')
            if end > 0:
                scrapedtitle = re.sub(r'<[^>]*>', '', data[:end]).strip()
            else:
                scrapedtitle = ''
            if scrapedtitle == '':
                patron = '<a\s*href="[^"]+"(?:\s*target="_blank")?>([^<]+)</a>'
                scrapedtitle = scrapertools.find_single_match(data, patron).strip()
            title = scrapertools.find_single_match(scrapedtitle, '\d+[^\d]+\d+')
            if title == '':
                title = scrapedtitle
            if title != '':
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos_tv",
                         title=title,
                         url=item.url,
                         thumbnail=item.thumbnail,
                         extra=data,
                         fulltitle=item.fulltitle,
                         show=item.show))

    logger.info("streamondemand.tantifilm episodios")
	

    itemlist = []

    data = scrapertools.cache_page(item.url, headers=headers)
    data = scrapertools.decodeHtmlentities(data)

    start = data.find('<div class="sp-wrap sp-wrap-blue">')
    end = data.find('<div id="disqus_thread">', start)

    data_sub = data[start:end]

    starts = []
    patron = r".*?STAGIONE|MINISERIE|WEBSERIE|SERIE"
    matches = re.compile(patron, re.IGNORECASE).finditer(data_sub)
    for match in matches:
        season_title = match.group()
        if season_title != '':
            starts.append(match.end())

    i = 1
    len_starts = len(starts)

    while i <= len_starts:
        inizio = starts[i - 1]
        fine = starts[i] if i < len_starts else -1

        html = data_sub[inizio:fine]

        load_episodios(html, item, itemlist)

        i += 1

    if len(itemlist) == 0:
        patron = '<a href="(#wpwm-tabs-\d+)">([^<]+)</a></li>'
        seasons_episodes = re.compile(patron, re.DOTALL).findall(data)

        end = None
        for scrapedtag, scrapedtitle in seasons_episodes:
            start = data.find(scrapedtag, end)
            end = data.find('<div class="clearfix"></div>', start)
            html = data[start:end]

            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos_tv",
                     title=scrapedtitle,
                     url=item.url,
                     thumbnail=item.thumbnail,
                     extra=html,
                     fulltitle=item.fulltitle,
                     show=item.show))


    return itemlist

# ==============================================================================================================================================================================	

def findvideos_tv(item):
    logger.info("streamondemand-pureita [tantifilm findvideos_tv]")

    # Descarga la página
    data = item.extra if item.extra != '' else scrapertools.cache_page(item.url, headers=headers)

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    # Extrae las entradas
    patron = r'<a href="([^"]+)" target="_blank" rel="noopener">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = item.title + " " + scrapedtitle
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=title,
                 url=scrapedurl.replace(r'\/', '/').replace('%3B', ';'),
                 thumbnail=item.thumbnail,
                 fulltitle=item.title,
                 show=item.title,
                 server='',
                 folder=False))

    return itemlist

# ==============================================================================================================================================================================	
	
def findvideos(item):
    logger.info("streamondemand-pureita [tantifilm findvideos]")

    # Descarga la página
    data = item.extra if item.extra != '' else httptools.downloadpage(item.url, headers=headers).data

    if 'protectlink.stream' in data:
        urls = scrapertools.find_multiple_matches(data, r'<iframe src=".*?//.*?=([^"]+)"')
        for url in urls:
            url = url.decode('base64')
            data += '\t' + url
			
            url = httptools.downloadpage(url, only_headers=True, follow_redirects=False).headers.get("location", "")
            data += '\t' + url

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
		
    patron = r'\{"file":"([^"]+)","type":"[^"]+","label":"([^"]+)"\}'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        title = item.title + " " + scrapedtitle + " quality"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl.replace(r'\/', '/').replace('%3B', ';'),
                 thumbnail=item.thumbnail,
                 fulltitle=item.title,
                 show=item.title,
                 server='',
                 folder=False))

    return itemlist