# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale  AnimeForce
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urllib
import urlparse
import xbmc

from core import config
from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod
from servers import adfly

__channel__ = "animeforce"
host = "https://ww1.animeforce.org"
headers = [['Referer', host]]


def mainlist(item):
    log("mainlist", "mainlist")
    itemlist = [Item(channel=__channel__,
                     action="lista_anime",
                     title="[COLOR azure]Anime - [COLOR orange]Lista Completa[/COLOR]",
                     url=host + "/lista-anime/",
                     thumbnail=ThumbnailLista,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="animeaggiornati",
                     title="[COLOR azure]Anime - [COLOR orange]Aggiornate[/COLOR]",
                     url=host,
                     thumbnail=CategoriaThumbnail,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="ultimiep",
                     title="[COLOR azure]Anime - [COLOR orange]Ultimi Episodi[/COLOR]",
                     url=host,
                     thumbnail=ThumbnailNew,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="animeaggiornati",
                     title="[COLOR azure]Anime - [COLOR orange]Ultime Serie[/COLOR]",
                     url=host + "/category/anime/articoli-principali/",
                     thumbnail=ThumbnailNew,
                     fanart=CategoriaFanart),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR yellow]Cerca ...[/COLOR]",
                     thumbnail=CercaThumbnail)]

    return itemlist

# ==================================================================================================================================================

def newest(categoria):
    log("newest", "newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "anime":
            item.url = host
            item.action = "ultimiep"
            itemlist = ultimiep(item)

            if itemlist[-1].action == "ultimiep":
                itemlist.pop()
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    log("search", "search")
    item.url = host + "/?s=" + texto
    try:
        return animeaggiornati(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================

def search_anime(item):
    log("search_anime", "search_anime")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<a href="([^"]+)"><img.*?src="([^"]+)".*?title="([^"]+)".*?/>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedurl = re.sub(r'episodio?-?\d+-?(?:\d+-|)[oav]*', '', scrapedurl)
        scrapedurl=re.sub('final-season*', 's3', scrapedurl)
        if "Sub Ita Download & Streaming" in scrapedtitle or "Sub Ita Streaming":
            itemlist.append(
                Item(channel=__channel__,
                     action="episodios",
                     title=scrapedtitle,
                     url=scrapedurl,
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     thumbnail=scrapedthumbnail))

    return itemlist

# ==================================================================================================================================================

def animeaggiornati(item):
    log("animeaggiornati", "animeaggiornati")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<img.*?src="([^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if 'Streaming' in scrapedtitle:
            # Pulizia titolo
            cleantitle = scrapedtitle.replace("Streaming", "").replace("&", "")
            cleantitle = cleantitle.replace("Download", "")
            cleantitle = cleantitle.replace("Sub Ita", "")
            cleantitle = re.sub(r'Episodio?\s*\d+\s*(?:\(\d+\)|)\s*[\(OAV\)]*', '', cleantitle)
            # Creazione URL
            scrapedurl = re.sub(r'episodio?-?\d+-?(?:\d+-\d+-||)(?:\d+-|)[oav]*', '', scrapedurl)
            scrapedurl=re.sub('oav-?(?:\d+-\d+-|)(?:(\d+-?)|)', '', scrapedurl).replace("-ova", "")
            scrapedurl=re.sub('final-season*', 's3', scrapedurl).replace('-fine', '').replace("-oav","")
            itemlist.append(infoSod(
                Item(channel=__channel__,
                     action="episodios",
                     title=cleantitle,
                     url=scrapedurl,
                     fulltitle=cleantitle,
                     show=cleantitle,
                     thumbnail=scrapedthumbnail), tipo="tv"))
					 

    # Extrae el paginador
    next_page = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)" />')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="animeaggiornati",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==================================================================================================================================================

def ultimiep(item):
    log("ultimiep", "ultimiep")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data

    patron = r'<img.*?src="([^"]+)"[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+>[^>]+><a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        if 'Streaming' in scrapedtitle:
            # Pulizia titolo
            scrapedtitle = scrapedtitle.replace("Streaming", "").replace("&", "")
            scrapedtitle = scrapedtitle.replace("Download", "")
            scrapedtitle = scrapedtitle.replace("Sub Ita", "").strip()
            eptype = scrapertools.find_single_match(scrapedtitle, "((?:Episodio?|OAV))")
            cleantitle = re.sub(r'%s\s*\d*\s*(?:\(\d+\)|)' % eptype, '', scrapedtitle).strip()
            if '(Fine)' in scrapedtitle:
                scrapedtitle = scrapedtitle.replace('(Fine)', ' ').strip() + " (Fine)"
                cleantitle = cleantitle.replace('(Fine)', '')
            # Creazione URL
            if 'download' not in scrapedurl:
                scrapedurl = scrapedurl.replace('-streaming', '-download-streaming')
            scrapedurl = re.sub(r'episodio?-?\d+-?(?:\d+-\d+-||)(?:\d+-|)[oav]*', '', scrapedurl)
            scrapedurl=re.sub('oav-?(?:\d+-\d+-|)(?:(\d+-?)|)', '', scrapedurl).replace("-ova", "")
            scrapedurl=re.sub('final-season*', 's3', scrapedurl).replace('-fine', '').replace("-oav","")
            epnumber = ""
            if 'episodio' in eptype.lower():
                epnumber = scrapertools.find_single_match(scrapedtitle.lower(), r'episodio?\s*(\d+)')
                eptype += ":? " + epnumber
                
            extra = "<tr>\s*<td[^>]+><strong>(?:[^>]+>|)%s(?:[^>]+>[^>]+>|[^<]*|[^>]+>)</strong>" % eptype
            itemlist.append(infoSod(
                Item(channel=__channel__,
                     action="episodios",
                     title=scrapedtitle,
                     url=scrapedurl,
                     fulltitle=cleantitle,
                     extra=extra,
                     show=re.sub(r'Episodio\s*', '', scrapedtitle),
                     thumbnail=scrapedthumbnail), tipo="tv"))
					 
    # Extrae el paginador
    next_page = scrapertools.find_single_match(data, '<link rel="next" href="([^"]+)" />')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="ultimiep",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==================================================================================================================================================

def lista_anime(item):
    log("lista_anime", "lista_anime")

    itemlist = []
    mumpage = 30
    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Carica la pagina 
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = r'<li>\s*<strong>\s*<a\s*href="([^"]+?)">([^<]+?)</a>\s*</strong>\s*</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    scrapedplot = ""
    scrapedthumbnail = ""
    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * mumpage > i: continue
        if i >= p * mumpage: break
        title = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        title=title.replace("Download & Streaming", "")
        title=title.replace("Sub Ita", "").replace("Streaming", "").strip()
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 title=title,
                 url=scrapedurl,
                 thumbnail=AnimeThumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True))

    if len(matches) >= p * mumpage:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="lista_anime",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail=AvantiImg,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def episodios(item):
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = '<td style="[^"]*?">\s*.*?<strong>(.*?)</strong>.*?\s*</td>\s*<td style="[^"]*?">\s*<a href="([^"]+?)"[^>]+>\s*<img.*?src="([^"]+?)".*?/>\s*</a>\s*</td>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl, scrapedimg in matches:
        if 'nodownload' in scrapedimg or 'nostreaming' in scrapedimg:
            continue

        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = re.sub(r'<[^>]*?>', '', scrapedtitle)
        scrapedtitle = '[COLOR azure][B]' + scrapedtitle + '[/B][/COLOR]'
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="episode",
                 title=scrapedtitle,
                 url=urlparse.urljoin(host, scrapedurl),
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 plot=item.plot,
                 fanart=item.thumbnail,
                 thumbnail=item.thumbnail))

    return itemlist

# ==================================================================================================================================================

def findvideos(item):
    logger.info("streamondemand.animeforce findvideos")

    itemlist = []

    if item.extra:
        data = httptools.downloadpage(item.url, headers=headers).data

        blocco = scrapertools.get_match(data, r'%s(.*?)</tr>' % item.extra)
        scrapedurl = scrapertools.find_single_match(blocco, r'<a href="([^"]+)"[^>]+>')
        url = scrapedurl
    else:
        url = item.url

    if 'adf.ly' in url:
        url = adfly.get_long_url(url)
    elif 'bit.ly' in url:
        url = httptools.downloadpage(url, only_headers=True, follow_redirects=False).headers.get("location")

    if 'animeforce' in url:
        headers.append(['Referer', item.url])
        data = httptools.downloadpage(url, headers=headers).data
        itemlist.extend(servertools.find_video_items(data=data))

        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__

        url = url.split('&')[0]
        data = httptools.downloadpage(url, headers=headers).data
        patron = """<source\s*src=(?:"|')([^"']+?)(?:"|')\s*type=(?:"|')video/mp4(?:"|')>"""
        matches = re.compile(patron, re.DOTALL).findall(data)
        headers.append(['Referer', url])
        for video in matches:
            itemlist.append(Item(channel=__channel__, action="play", title=item.title, thumbnail=item.thumbnail,
                                 url=video + '|' + urllib.urlencode(dict(headers)), folder=False))
    else:
        itemlist.extend(servertools.find_video_items(data=url))

        for videoitem in itemlist:
            videoitem.title = item.title + videoitem.title
            videoitem.fulltitle = item.fulltitle
            videoitem.show = item.show
            videoitem.thumbnail = item.thumbnail
            videoitem.channel = __channel__

    return itemlist


# ==================================================================================================================================================

# ==================================================================================================================================================
def scrapedAll(url="", patron=""):
    data = httptools.downloadpage(url).data
    MyPatron = patron
    matches = re.compile(MyPatron, re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    return matches


# ==================================================================================================================================================

def scrapedSingle(url="", single="", patron=""):
    data = httptools.downloadpage(url).data
    paginazione = scrapertools.find_single_match(data, single)
    matches = re.compile(patron, re.DOTALL).findall(paginazione)
    scrapertools.printMatches(matches)

    return matches


# ==================================================================================================================================================

def Crea_Url(pagina="1", azione="ricerca", categoria="", nome=""):
    # esempio
    # chiamate.php?azione=ricerca&cat=&nome=&pag=
    Stringa = host + "chiamate.php?azione=" + azione + "&cat=" + categoria + "&nome=" + nome + "&pag=" + pagina
    log("crea_Url", Stringa)
    return Stringa

# ==================================================================================================================================================

def log(funzione="", stringa="", canale=__channel__):
    logger.debug("[" + canale + "].[" + funzione + "] " + stringa)

# ==================================================================================================================================================

def HomePage(item):
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand)")

# ==================================================================================================================================================

# ==================================================================================================================================================
AnimeThumbnail = "http://img15.deviantart.net/f81c/i/2011/173/7/6/cursed_candies_anime_poster_by_careko-d3jnzg9.jpg"
AnimeFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
AnimeAz = "https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/a-z_P.png"
ThumbnailNew = "https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_new_P.png"
ThumbnailLista = "https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_lista_P.png"
CategoriaThumbnail = "https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/anime_P.png"
CategoriaFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
CercaThumbnail = "https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png"
CercaFanart = "https://i.ytimg.com/vi/IAlbvyBdYdY/maxresdefault.jpg"
HomeTxt = "[COLOR yellow]Torna Home[/COLOR]"
AvantiTxt = "[COLOR orange]Successivi >>[/COLOR]"
AvantiImg = "https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"
