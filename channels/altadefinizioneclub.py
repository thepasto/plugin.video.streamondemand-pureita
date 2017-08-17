# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand-pureita.- XBMC Plugin
# Canal para altadefinizione01
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse
import xbmc

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "altadefinizioneclub"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "AltaDefinizioneclub"
__language__ = "IT"

host = "http://altadefinizione.bid"



DEBUG = config.get_setting("debug")

def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.altadefinizione01 mainlist")
    itemlist = []
    itemlist.append(Item(channel=__channel__,title="[COLOR azure]Prime visioni[/COLOR]",action="peliculas",url="%s/prime-visioni/" % host,thumbnail=ThumbPrimavisione,fanart=fanart))
    itemlist.append(Item(channel=__channel__,title="[COLOR azure]Film[/COLOR]",action="peliculas",url="%s/genere/film/" % host,thumbnail=ThumbNovita,fanart=fanart))
    itemlist.append(Item(channel=__channel__,title="[COLOR azure]Film in HD[/COLOR]",action="peliculas", url="http://altadefinizione.bid/?s=[HD]",thumbnail=ThumbFilmHD, fanart=fanart))
    itemlist.append(Item(channel=__channel__,title="[COLOR azure]Serie TV - [COLOR orange]Nuove[/COLOR]",action="peliculas",url=host+"/genere/serie-tv/", thumbnail=ThumbTVShow, fanart=fanart))
    itemlist.append(Item(channel=__channel__,title="[COLOR azure]Serie TV - [COLOR orange]Aggiornate[/COLOR]",action="peliculas",url=host+"/aggiornamenti-serie-tv/", thumbnail=ThumbTVShowNew, fanart=fanart))
    itemlist.append(Item(channel=__channel__,title="[COLOR yellow]Cerca...[/COLOR]",action="search", thumbnail=ThumbSearch, fanart=fanart))


    return itemlist


def peliculas(item):
    logger.info("streamondemand.altadefinizioneclub peliculas")
    itemlist = []

    patron = '<li><a href="([^"]+)" data-thumbnail="([^"]+)"><div>\s*<div class="title">(.*?)</div>'
    for scrapedurl,scrapedthumbnail,scrapedtitle  in scrapedAll(item.url,patron):
        logger.info("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        xbmc.log(("title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]"))
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.replace("[HD]","")
        itemlist.append(infoSod(
                        Item(channel=__channel__,
                              action="findvideos",
                               title=scrapedtitle,
                           fulltitle=scrapedtitle,
                                 url=scrapedurl,
                           thumbnail=scrapedthumbnail,
                            viewmode="movie"),
                                tipo="movie",))

    # Paginazione
    # ===========================================================================================================================
    matches = scrapedSingle(item.url, '<span class=\'pages\'>(.*?)class="clearfix"',"class='current'>.*?</span>.*?href=\"(.*?)\">.*?</a>")
    if len(matches) > 0:
        paginaurl = scrapertools.decodeHtmlentities(matches[0])
        itemlist.append(Item(channel=__channel__, action="peliculas", title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt, thumbnail=ThumbnailHome, folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title=ListTxt, thumbnail=ThumbnailHome,folder=True))
    # ===========================================================================================================================
    return itemlist

def search(item, texto):
    logger.info("[altadefinizioneclub.py] " + item.url + " search " + texto)
    itemlist=[]
    item.url = "http://altadefinizione.bid/?s=%s" % texto

    return peliculas(item)


def genere(item):
    itemlist=[]

    patron='<li class="cat-item.*?"[^<]+<.*?href="(.*?)".*?>(.*?)</a>'
    single='class="box-sidebar-header">[^C]+Categorie(.*?)class="box-sidebar general">'
    for scrapedurl,scrapedtitle in scrapedSingle(item.url,single,patron):

        itemlist.append(Item(channel=__channel__,
                              action="peliculas",
                               title=scrapedtitle,
                           fulltitle=scrapedtitle,
                                 url=scrapedurl,
                           thumbnail=""))

    return itemlist


def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand-pureita-master)")

# =================================================================
# Funzioni di servizio
# -----------------------------------------------------------------
def scrapedAll(url="", patron=""):
    matches = []
    headers = [
        ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
        ['Referer',url]
    ]
    data = scrapertools.cache_page(url)
    data=data.replace('<span class="hdbox">HD</span>',"")
    #logger.info("data->"+data)
    xbmc.log("ok"+data)
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    return matches
# =================================================================

# -----------------------------------------------------------------
def scrapedSingle(url="", single="", patron=""):
    matches = []
    data = scrapertools.cache_page(url)
    elemento = scrapertools.find_single_match(data, single)
    logger.info("elemento ->" + elemento)
    xbmc.log("elemento ->" + elemento)
    matches = re.compile(patron, re.DOTALL).findall(elemento)
    scrapertools.printMatches(matches)
    return matches
# =================================================================

HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
ThumbnailHome="https://raw.githubusercontent.com/orione7/Pelis_images/master/vari/return_home2_P.png"
ListTxt = "[COLOR orange]Torna a elenco principale [/COLOR]"
AvantiTxt = "[COLOR orange]Successivo>>[/COLOR]"
AvantiImg = "https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/successivo_P.png"
ThumbPrimavisione="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"
ThumbNovita="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"
ThumbFilmHD="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"
ThumbTVShow="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"
ThumbTVShowNew="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"
ThumbSearch="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"
FilmFanart="https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
fanart="http://www.virgilioweb.it/wp-content/uploads/2015/06/film-streaming.jpg"
