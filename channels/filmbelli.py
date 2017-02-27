# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para itafilmtv
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
#  By Costaplus
# ------------------------------------------------------------
import re

import xbmc

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "filmbelli"
__category__ = "F"
__type__ = "generic"
__title__ = "filmbelli.net"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "http://www.filmbelli.gratis"

def isGeneric():
    return True

#-------------------------------------------------------------------------------------------------------------------------------------------
def mainlist(item):
    log("mainlist","init")
    itemlist =[]

    itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR yellow]Novità[/COLOR]"       , url=host                 , thumbnail=NovitaThumbnail, fanart=FilmFanart ))
    itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR azure]Film al Cinema[/COLOR]", url=host+"/genere/cinema", thumbnail=CinemaThumbnail, fanart=FilmFanart ))
    itemlist.append(Item(channel=__channel__, action="genere", title="[COLOR azure]Genere[/COLOR]"       , url=host                  , thumbnail=GenereThumbnail, fanart=FilmFanart ))
    itemlist.append(Item(channel=__channel__, action="search", title="[COLOR orange]Cerca..[/COLOR]"      ,                            thumbnail=CercaThumbnail , fanart=FilmFanart))

    return itemlist
#===========================================================================================================================================

#-------------------------------------------------------------------------------------------------------------------------------------------
def genere(item):
    log("genere","init")
    itemlist = []

    patron ='<a href="(.*?)">(.*?)</a>'
    for scrapedurl, scrapedtitle in scrapedSingle(item.url, '<div class="tag_cloud_post_tag">(.*?)</div>',patron):
        log("genere", "title=[" + scrapedtitle + "] url=[" + scrapedurl + "]")
        itemlist.append(Item(channel=__channel__, action="elenco", title="[COLOR azure]"+ scrapedtitle+"[/COLOR]", url=scrapedurl,thumbnail=GenereThumbnail, fanart=FilmFanart))

    return itemlist
#===========================================================================================================================================

#-------------------------------------------------------------------------------------------------------------------------------------------
def elenco(item):
    log("elenco","init")
    itemlist = []

    patron='class="bottom_line"></div>[^<]+<[^<]+<img.*?src="(.*?)"[^<]+</a>[^>]+<[^<]+<[^<]+<[^<]+<.*?class="movie_title"><a href="(.*?)">(.*?)</a>'
    for scrapedthumbnail,scrapedurl,scrapedtitle in scrapedSingle(item.url,'div id="movie_post_content">(.*?)</ul>',patron):
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle)
        log("elenco","title=["+ scrapedtitle + "] url=["+ scrapedurl +"] thumbnail=["+ scrapedthumbnail +"]")

        itemlist.append(infoSod(Item(channel=__channel__, action="findvideos", title=scrapedtitle, fulltitle=scrapedtitle, url=scrapedurl,thumbnail=scrapedthumbnail), tipo="movie"))

    # Paginazione
    # ===========================================================================================================================
    matches=scrapedSingle(item.url,'class="vh-pages-wrapper span12 body-bg">(.*?)</div>','class="current">.*?</span><.*?href="(.*?)"')
    if len(matches) > 0:
        paginaurl = matches[0]
        itemlist.append(Item(channel=__channel__, action="elenco"  , title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt  , folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title=ListTxt, folder=True))
    # ===========================================================================================================================
    return itemlist
#===========================================================================================================================================


#-------------------------------------------------------------------------------------------------------------------------------------------
def search(item,texto):
    log("search","init texto=["+ texto + "]")
    itemlist = []
    url = host + "/?s="
    url=url+texto+"&search=Cerca+un+film"

    patron='class="bottom_line"></div>[^<]+<[^<]+<img.*?src="(.*?)"[^<]+</a>[^>]+<[^<]+<[^<]+<[^<]+<.*?class="movie_title"><a href="(.*?)">(.*?)</a>'
    for scrapedthumbnail,scrapedurl,scrapedtitle in scrapedSingle(url,'div id="movie_post_content">(.*?)</ul>',patron):
        scrapedtitle=scrapertools.decodeHtmlentities(scrapedtitle)
        log("novita","title=["+ scrapedtitle + "] url=["+ scrapedurl +"] thumbnail=["+ scrapedthumbnail +"]")

        itemlist.append(infoSod(Item(channel=__channel__, action="findvideos", title=scrapedtitle, fulltitle=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail), tipo="movie"))

    # Paginazione
    # ===========================================================================================================================
    matches=scrapedSingle(url,'class="vh-pages-wrapper span12 body-bg">(.*?)</div>','class="current">.*?</span><.*?href="(.*?)"')
    if len(matches) > 0:
        paginaurl = scrapertools.decodeHtmlentities(matches[0])
        itemlist.append(Item(channel=__channel__, action="elenco"  , title=AvantiTxt, url=paginaurl, thumbnail=AvantiImg))
        itemlist.append(Item(channel=__channel__, action="HomePage", title=HomeTxt  , folder=True))
    else:
        itemlist.append(Item(channel=__channel__, action="mainlist", title= ListTxt, folder=True))
    # ============================================================================================================================
    return itemlist

#=================================================================
# Funzioni di servizio
#-----------------------------------------------------------------
def scrapedAll(url="",patron=""):
    matches = []
    data = scrapertools.cache_page(url)
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches
#=================================================================

#-----------------------------------------------------------------
def scrapedSingle(url="",single="",patron=""):
    matches =[]
    data = scrapertools.cache_page(url)
    elemento = scrapertools.find_single_match(data, single)
    log("scrapedSingle", "elemento:" + elemento)
    matches = re.compile(patron, re.DOTALL).findall(elemento)
    scrapertools.printMatches(matches)

    return matches
#=================================================================

#-----------------------------------------------------------------
def log(funzione="",stringa="",canale=__channel__):
       logger.info("[" + canale + "].[" + funzione + "] " + stringa)
#=================================================================

#-----------------------------------------------------------------
def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand-pureita-master)")
#=================================================================

#=================================================================
# riferimenti di servizio
#---------------------------------------------------------------------------------------------------------------------------------
NovitaThumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"
CinemaThumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movies_P.png"
GenereThumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png"
FilmFanart="https://superrepo.org/static/images/fanart/original/script.artwork.downloader.jpg"
CercaThumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"
CercaFanart="https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
ListTxt = "[COLOR orange]Torna a elenco principale [/COLOR]"
AvantiTxt="[COLOR orange]Successivo>>[/COLOR]"
AvantiImg="https://raw.githubusercontent.com/orione7/Pelis_images/master/vari/successivo_P.png"
thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"
#----------------------------------------------------------------------------------------------------------------------------------#----------------------------------------------------------------------------------------------------------------------------------
