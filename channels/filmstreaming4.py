# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale filmstreaming4
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import re
import urlparse

from core import httptools
from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod


__channel__ = "filmstreaming4"
host = "https://4filmstreaming.org"
headers = [['Referer', host]]


# ==============================================================================================================================================

def mainlist(item):
    logger.info("[streamondemand-pureita filmstreaming4] mainlist")

    itemlist = [
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Novita'[/COLOR]",
             action="peliculas_new",
             url="%s/genere/al-cinema/" % host,
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Ultimi inseriti[/COLOR]",
             action="peliculas_new",
             url="%s/movies/" % host,
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movies_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Animazione[/COLOR]",
             action="peliculas_new",
             url="%s/genere/animazione/" % host,
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation2_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Film - [COLOR orange]Per Genere[/COLOR]",
             action="genere",
             url=host,
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
        Item(channel=__channel__,
             title="[COLOR azure]Serie TV - [COLOR orange]Lista[/COLOR]",
             action="peliculas_tv",
             url=host + "/series/",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
        Item(channel=__channel__,
             title="[COLOR yellow]Cerca...[/COLOR]",
             action="search",
             thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==============================================================================================================================================

def genere(item):
    logger.info("[streamondemand-pureita filmstreaming4] genere")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = "<ul class='sub-menu'>(.*?)</ul></div>"
    data = scrapertools.find_single_match(data, patron)

    patron = '<a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_new",
                 title="[COLOR azure]" +scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================

def peliculas_new(item):
    logger.info("[streamondemand-pureita filmstreaming4] peliculas_new")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" data-url=""\s*class="[^"]+"\s*data-hasqtip="\d+" oldtitle="([^"]+)"\s*title="">\s*'
    patron += '<img data-original="([^"]+)" class=[^>]+>\s*'
    patron += '<span class="mli-info"><h2>[^<]+</h2></span>\s*</a>\s*' 
    patron += '<div id="hidden_tip">\s*<div id="" class="qtip-title">[^<]+</div>\s*'
    patron += '<div class="jtip-top">\s*<div class="jt-info jt-imdb"> IMDb: ([^<]+)</div>\s*'
    patron += '<div class="jt-info"><a href="[^"]+" rel="tag">([^<]+)</a></div>.*?'
    patron += '<p>(.*?)<\/p>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(6))
        year = scrapertools.unescape(match.group(5))
        rating = scrapertools.unescape(match.group(4))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = scrapertools.unescape(match.group(1))

        if year in scrapedtitle:
          scrapedtitle=scrapedtitle.replace(year, "").replace("(", "").replace(")", "")		  
        if rating:
         rating = " ([COLOR yellow]" + rating + "[/COLOR])"

        scrapetitle=scrapedtitle + " (" + year + ")"
        year = " ([COLOR yellow]" + year + "[/COLOR])"		
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapetitle,
                 show=scrapetitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] " + year + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = "<li class='active'><a class=''>\d+</a></li><li><a rel='nofollow' class='page larger' href='([^']+)'>\d+"
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

def peliculas_tv(item):
    logger.info("[streamondemand-pureita filmstreaming4] peliculas_tv")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" data-url[^>]+>\s*'
    patron += '<img data-original="([^"]+)\s*" class[^>]+>\s*'
    patron += '<span class="mli-info"><h2>([^<]+)</h2></span>\s*</a>.*?' 
    patron += '<div class="jt-info jt-imdb">([^<]+)</div>\s*'
    patron += '<div class="jt-info"><a href="[^"]+" rel="tag">([^<]+)</a></div>.*?'
    patron += '<p>(.*?)<\/p>'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = scrapertools.unescape(match.group(6))
        year = scrapertools.unescape(match.group(5))
        rating = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(2))
        scrapedurl = scrapertools.unescape(match.group(1))

        if year in scrapedtitle:
          scrapedtitle=scrapedtitle.replace(year, "").replace("(", "").replace(")", "")		  
        if rating:
         rating = " ([COLOR yellow]" + rating + "[/COLOR])"

        scrapetitle=scrapedtitle + " (" + year + ")"
        year = " ([COLOR yellow]" + year + "[/COLOR])"		
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tvshow",
                 fulltitle=scrapetitle,
                 show=scrapetitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] " + year + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = "<li class='active'><a class=''>\d+</a></li><li><a rel='nofollow' class='page larger' href='([^']+)'>\d+"
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# ==================================================================================================================================================

def episodios(item):
    logger.info("[streamondemand-pureita filmstreaming4] episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, r'<strong>Season \d+</strong></div>(.*?)</ul>\s*</div>\s*</div>\s*</div>')
	
    patron = r'<a href="([^"]+)">\s*([^<]+)<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="findviodeos",
                 title=scrapedtitle,
                 contentType="tv",
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 show=item.show + " - " + scrapedtitle,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================	
	
def search(item, texto):
    logger.info("[streamondemand-pureita filmstreaming4] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return peliculas_src(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================

def peliculas_src(item):
    logger.info("[streamondemand-pureita filmstreaming4] peliculas_src")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)" data-url[^>]+>\s*'
    patron += '<img data-original="([^"]+)\s*" class[^>]+>\s*'
    patron += '<span class="mli-info"><h2>([^<]+)</h2></span>\s*</a>.*?' 
    patron += '<div class="jt-info jt-imdb">([^<]+)</div>\s*'
    patron += '<div class="jt-info"><a href="[^"]+" rel="tag">([^<]+)</a></div>.*?'
    patron += '<p>(.*?)<\/p>\s*</p>\s*[^>]+>([^<]+)<'
    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        type = scrapertools.unescape(match.group(7))
        scrapedplot = scrapertools.unescape(match.group(6))
        year = scrapertools.unescape(match.group(5))
        rating = scrapertools.unescape(match.group(4))
        scrapedtitle = scrapertools.unescape(match.group(3))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(2))
        scrapedurl = scrapertools.unescape(match.group(1))

        if year in scrapedtitle:
          scrapedtitle=scrapedtitle.replace(year, "").replace("(", "").replace(")", "")		  
        if rating:
         rating = " ([COLOR yellow]" + rating + "[/COLOR])"

        scrapetitle=scrapedtitle + " (" + year + ")"
        year = " ([COLOR yellow]" + year + "[/COLOR])"		
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos" if not "Series" in type else "episodios",
                 contentType="tvshow",
                 fulltitle=scrapetitle,
                 show=scrapetitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] " + year + rating,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie' if not "Series" in type else "tv"))


    return itemlist
	
# ==================================================================================================================================================

def findvideos(item):
    logger.info("[streamondemand-pureita filmstreaming4] findvideos")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = '<div id="list-watch" class="tab-pane">(.*?)</div>\s*</div>'
    data = scrapertools.find_single_match(data, patron)

    patron = '<a href="([^"]+)" class="[^"]+" target="_blank">\s*<span style[^>]+>' \
             '<img style="" src[^>]+>\s*<span[^>]+>([^<]+)<\/span><\/span>\s*' \
			 '<span[^>]+>[^>]+>[^>]+>[^>]+><\/span>\s*<span class[^>]+>([^<]+)<\/span>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedtitle, quality in matches:
        #quality=" ([COLOR yellow]" + quality + "[/COLOR])"
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[[COLOR orange]" +scrapedtitle + "[/COLOR]] - " + item.fulltitle, 
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))


    data = scrapertools.cache_page(item.url)
    patron = '<iframe class="embed-responsive-item" src="([^"]+)" frameborder="\D+" marginwidth="\d+" marginheight="\d+" scrolling="NO" allowfullscreen[^>]+></iframe>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        data += httptools.downloadpage(scrapedurl).data
		
    for videoitem in servertools.find_video_items(data=data):
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.fulltitle])
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)
				 
    return itemlist

# ==================================================================================================================================================

def play(item):
    itemlist=[]
    data = item.url
    if "rapidcrypt" in item.url:
       data = httptools.downloadpage(item.url).data
	  
    while 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url
		
    #logger.debug(data)
    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername + '[/COLOR]] - ', item.fulltitle])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__
    return itemlist