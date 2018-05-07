# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale  videotecaproject
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

__channel__ = "videotecaproject"
host = "https://www.videotecaproject.eu"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita.videotecaproject mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Raccomandati[/COLOR]",
                     action="peliculas_list",
                     url="%s/film/versione-temporanea/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Lista A/Z[/COLOR]",
                     action="peliculas_list",
                     url="%s/film/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film [COLOR orange]- Ultimi Aggiornati[/COLOR]",
                     action="peliculas",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                #Item(channel=__channel__,
                     #title="[COLOR azure]Film [COLOR orange]- Categorie[/COLOR]",
                     #action="categorias",
                     #url=host,
                     #thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Ultimi Episodi[/COLOR]",
                     action="peliculas_new",
                     url="%s/serie-tv/" % host,
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV [COLOR orange]- Lista A/Z[/COLOR]",
                     action="serie_az",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Film...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="serie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==================================================================================================================================================

def peliculas_list(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_list")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">([^<]+)</a></h3>\s*<span class="article-date">[^<]+</span>\s*'
    patron += '</header>\s*<div class="article-content">(.*?)<\/div>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedthumbnail = ""
        scrapedplot = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace("https://www.videotecaproject.eu/news/", "")
        scrapedtitle = scrapedtitle.replace(":", " ")
        scrapedtitle = scrapedtitle.replace("/", "")
        scrapedtitle =scrapedtitle.title()


        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima pagina." rel="next">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_new(item):
    logger.info("[streamondemand-pureita videoproject] peliculas_new")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<span style="font-family:tahoma,geneva,sans-serif;".*?'
    patron += '<span style="color:#ff0000;">[^>]+>([^<]+)<[^>]+><\/span>[^>]+>[^>]+><\/p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle in matches:
        scrapetitle=scrapedtitle.replace("°", "")
        #scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 fulltitle=scrapedtitle,
                 action="peliculas_date",
                 title="[COLOR yellow]" + scrapetitle + "[/COLOR]",
                 url=item.url,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png",
                 folder=True))

    itemlist.sort(key=lambda x: x.title)
    itemlist.reverse()
    return itemlist
	
# ==================================================================================================================================================

def serie_az(item):
    logger.info("[streamondemand-pureita videotecaproject] serie_az")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '<li>\s*<a href="[^"]+">\s*Serie Tv(.*?)</li>\s*</ul>')


    # Extrae las entradas (carpetas)
    patron = '<a href="([^"]+)">\s*([^\n]+)\s*<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedthumbnail=""
        scrapedplot =""
        #scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_serie",
                 fulltitle=scrapedtitle,
                 title=scrapedtitle,
                 url="".join([host, scrapedurl]),
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png",
                 folder=True))

    return itemlist
	
# ==========================================================================

def peliculas_serie(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_serie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">([^<]+)</a></h3>.*?'
    patron += '<div class="article-content">(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedthumbnail = ""
        scrapedplot = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace(" Ita", "").replace(" ITA", "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace("-", " ")
        scrapedtitle = scrapedtitle.replace("/", "").replace(":", " ")


        #scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        #scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="tv",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima pagina." rel="next">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_serie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================		
	
def search(item, texto):
    logger.info("[streamondemand-pureita videotecaproject] " + item.url + " search " + texto)
    item.url = host + "/search/?text=" + texto

    try:
        if item.extra == "movie":
            return peliculas_srcmovie(item)
        if item.extra == "serie":
            return peliculas_srcserie(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================

def peliculas_srcmovie(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_srcmovie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	
    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("<strong>", "").replace("</strong>", "")
        scrapedtitle = scrapedtitle.replace(" ITA", "")
        #scrapedtitle = re.sub(r"([0-9])", r" \1", scrapedtitle)

        if "serie" in scrapedurl or "ita" in scrapedurl:
         continue
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos" if not "film" in scrapedurl else "peliculas_list",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima pagina." rel="next">'
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

def peliculas_srcserie(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_srcserie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
	
    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("<strong>", "").replace("</strong>", "")
        scrapetitle = scrapedtitle.replace(" ITA", "")
        if not "ITA" in scrapedtitle or "serie" in scrapedurl:
         continue

        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios" if not "serie" in scrapedurl else "peliculas_serie",
                 fulltitle=scrapetitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapetitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo="tv"))

    # Extrae el paginador
    patronvideos = '<a href="([^"]+)" class="right" title="Vai alla prossima pagina." rel="next">'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_srcserie",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))
   
    return itemlist
	
# ==================================================================================================================================================

def peliculas(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<a\s*href="((http[^"]+))".*?>\s*<img\s*src="([^"]+)"\s*style[^>]+><\/a>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedthumbnail = urlparse.urljoin(item.url, match.group(3))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace("https://www.videotecaproject.eu/news/", "")

        #scrapedtitle = ''.join(' ' + char if char.isupper() else char.strip() for char in text).strip()
        scrapedtitle = scrapedtitle.replace("-", " ")
        scrapedtitle = scrapedtitle.replace(":", " ")
        scrapedtitle = scrapedtitle.replace("/", "")
        scrapedtitle = re.sub(r"([0-9])", r" \1", scrapedtitle)
        scrapedtitle = re.sub('(?<=\d) (?=\d)', '', scrapedtitle)
        scrapedtitle =scrapedtitle.title()
        #scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        #scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    return itemlist

# ==================================================================================================================================================

def peliculas_date(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_date")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '%s(.*?)<p style="text-align: center;">&nbsp;</p>' % item.fulltitle)
				 
    patron = '<a\s*href="([^"]+)".*?img alt=""\s*src="([^"]+)" [^>]+.*?'
    patron += '<\/a>.*?\s.*?'
    patron += '<a\s*href="[^"]+".*?>([^<]+)<'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedplot = ""
        stitle=''.join(i for i in scrapedtitle if not i.isdigit())
        scrapedtitle = scrapedtitle.replace("’", "'")
        scrapedtitle = scrapedtitle.replace("’", "'")

        #scrapedtitle = scrapedtitle.title()
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="serie",
                 fulltitle=stitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='tv'))
				 

    return itemlist	
	
# ==================================================================================================================================================
	
def episodios(item):
    logger.info("[streamondemand-pureita videotecaproject] episodios")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data
    blocco = scrapertools.get_match(data, 'Stagione.*?</span>(.*?)<footer class="widget-footer">')
	
    patron = '<p>(.*?)</span></span>'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for puntata in matches:
        puntata = puntata + '<span style="font-size: 14px;">'

        scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank">([^<]+)<')

        if scrapedtitle=="":
           scrapedtitle=scrapertools.find_single_match(puntata, '<span[^>]+>([^<]+)')

	
        #if '<span style="font-weight: 700;">' in puntata:
          #scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank">([^<]+)<')

        if "Stagione" in puntata:
          scrapedtitle=scrapertools.find_single_match(puntata, '<span style="font-weight: 700;">([^<]+)<')
          if not "Stagione" in scrapedtitle:
            scrapedtitle=scrapertools.find_single_match(puntata, '<span style="font-family: tahoma, geneva, sans-serif;">([^<]+)')
          	  
        if "Stagione" in scrapedtitle:
           scrapedtitle = "[COLOR yellow]" + scrapedtitle + "[/COLOR]"
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=puntata,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
	
    patron = '<div>(.*?)</span></'
    matches = re.compile(patron, re.DOTALL).findall(blocco)
    scrapertools.printMatches(matches)

    for puntata in matches:
        scrapedtitle=scrapertools.find_single_match(puntata, '<a\s*href="http.*?:\/\/.*?\/[^.]+[^\d+]+([^\.]+)[^>]+>')
        scrapedtitle=scrapedtitle.replace("E", "x")
        if not "x" in scrapedtitle:
          scrapedtitle=scrapertools.find_single_match(puntata, 'target="_blank">([^<]+)</a>')
        #if "Stagione" in puntata:
          #scrapedtitle=scrapertools.find_single_match(puntata, '<strong>([^<]+)<\/strong>')
        if scrapedtitle=="":
          continue

        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=item.fulltitle.replace("x ITA", "") + " [[COLOR orange]" +scrapedtitle + "[/COLOR]]",
                 url=puntata,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
			 
    return itemlist
	
# ==================================================================================================================================================
	
def findvideos(item):
    logger.info("[streamondemand-pureita videotecaproject] findvideos")
    itemlist = []

    patron = '<a href="(([^.]+).*?)"\s*target="_blank">'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl,scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("https://", "").replace("http://", "")
        scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.scrapedtitle,
                 show=item.title,
                 title="[COLOR azure]" + item.title + " [[COLOR orange]" + scrapedtitle + "[/COLOR]]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 
    patron = '<a href="([^"]+)\s*" target="_blank">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl,scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("https://", "").replace("http://", "")
        scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.scrapedtitle,
                 show=item.title,
                 title="[COLOR azure]" + item.title + " [[COLOR orange]" + scrapedtitle + "[/COLOR]]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))
				 
    return itemlist

# ==================================================================================================================================================	
	
def play(item):
    itemlist=[]

    data = item.url
    while 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url
		
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join(['[COLOR orange][B]' + videoitem.title + ' [COLOR azure][B]- ' + item.show + '[/B][/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist

# ==================================================================================================================================================
# ==================================================================================================================================================
# ==================================================================================================================================================

	
def peliculas_tv(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas_tv")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '%s.*?<\/span><\/span><\/span><\/p>\s*<p style="text-align: center;">(.*?)<p style="text-align: center;">' % item.title)
	
    # Extrae las entradas (carpetas)
    patron = '<img alt=""\s*src="([^"]+)"\s*style[^>]+><\/span>'
    patron += '<\/span>[^=]+[^>]+>[^>]+[^=]+[^>]+>[^>]+><a\s*href="([^"]+)">([^<]+)<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)

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
    itemlist.reverse()
    # Extrae el paginador
    patronvideos = ''
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

	
# ========================================================================
	
def findvideos_film(item):
    logger.info("[streamondemand-pureita videotecaproject] findvideos_film")
    itemlist = []

    patron = '<a href="(([^.]+).*?)"\s*target="_blank">'
    matches = re.compile(patron, re.DOTALL).findall(item.url)

    for scrapedurl,scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("https://", "")
        scrapedtitle = scrapedtitle.title()

        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 fulltitle=item.scrapedtitle,
                 show=item.title,
                 title="[COLOR azure]" + item.title + " [[COLOR orange]" + scrapedtitle + "[/COLOR]]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

				 
    return itemlist	

# ========================================================================
	
def categorias(item):
    logger.info("[streamondemand-pureita videotecaproject] categorias")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data


    # Extrae las entradas (carpetas)
    patron = '<a href="[^"]+">\s*([^\n]+)\s*<\/a>\s*<ul class="level2">\s*<li class="first">'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle in matches:
        scrapedthumbnail=""
        scrapedplot =""
        scrapedurl =""
        scrapedtitle = scrapedtitle.strip()
        scrapedtitle = scrapedtitle.title()
        itemlist.append(
            Item(channel=__channel__,
                 action="listmovie",
                 fulltitle=scrapedtitle,
                 title=scrapedtitle,
                 url=host,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist
	
# ========================================================================

def listmovie(item):
    logger.info("[streamondemand-pureita videotecaproject] categorias_list")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '%s(.*?)</ul>\s*</li>' % item.fulltitle)
				 
    patron = '<a href="([^"]+)">\s*([^<]+)\s*<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle  in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = scrapedtitle.replace("’", "'")


        #scrapedtitle = scrapedtitle.title()
        #scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        #scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="peliculas_listmovie",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url="".join([host, scrapedurl]),
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))
				 
    return itemlist

# ========================================================================
	
def peliculas_listmovie(item):
    logger.info("[streamondemand-pureita videotecaproject] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<h3><a href="([^"]+)">([^<]+)</a></h3>.*?'
    patron += '<div class="article-content">(.*?)</div>'

    matches = re.compile(patron, re.DOTALL).finditer(data)

    for match in matches:
        scrapedthumbnail = ""
        scrapedplot = scrapertools.unescape(match.group(3))
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = urlparse.urljoin(item.url, match.group(1))
        scrapedtitle = scrapedtitle.replace(" Ita", "").replace(" ITA", "")
        scrapedtitle = scrapedtitle.replace("’", "'").replace("-", " ")
        scrapedtitle = scrapedtitle.replace("/", "").replace(":", " ")

        scrapedtitle =scrapedtitle.strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True), tipo='movie'))

    return itemlist
	
# ==================================================================================================================================================
# ==================================================================================================================================================
# ==================================================================================================================================================
