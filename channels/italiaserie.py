# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para piratestreaming
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod
from servers import servertools

__channel__ = "italiaserie"
__category__ = "S,A"
__type__ = "generic"
__title__ = "italiaserie"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.italiaserie.news"


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.filmpertutti mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Aggiornamenti Serie TV[/COLOR]",
                     action="peliculas",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/General_Popular/series/New%20TV%20Shows.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     action="peliculas",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/General_Popular/most%20used/tv_series.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime e Cartoon[/COLOR]",
                     action="peliculas",
                     url="%s/category/anime-e-cartoon/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/General_Popular/anime/Anime.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Lista Completa[/COLOR]",
                     action="lista",
                     url="%s/lista-completa/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/General_Popular/anime/anime_all.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]
    return itemlist


def peliculas(item):
    logger.info("streamondemand.italiaserie peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="post-thumb">\s*<a href="([^"]+)" title="([^"]+)">\s*<img src="([^"]+)"[^>]+>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        html = scrapertools.cache_page(scrapedurl)
        start = html.find("<div class=\"entry-content\">")
        end = html.find("</p>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a class="next page-numbers" href="(.*?)">Next'
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
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 folder=True))

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand-pureita-master)")


def lista(item):
    logger.info("streamondemand.italiaserie peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)".*?>([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        if scrapedtitle.startswith("Link to "):
            scrapedtitle = scrapedtitle[8:]
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 plot=scrapedplot,
                 folder=True))

    return itemlist


def anime(item):
    itemlist = []
    data = scrapertools.cache_page(item.url)

    patron = '</h2><ul><li><strong>Categoria:</strong>(.*?)</ul></li><li>'
    data = scrapertools.find_single_match(data, patron)

    patron = '<li><a href="([^"]+)" title="([^"]+)">.*?</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
            Item(channel=__channel__,
                 action="animelink",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist


def search(item, texto):
    logger.info("[italiaserie.py] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        return peliculas(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def findvid_serie(item):
    logger.info("[eurostreaming.py] findvideos")

    ## Descarga la página
    data = scrapertools.cache_page(item.url)

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
