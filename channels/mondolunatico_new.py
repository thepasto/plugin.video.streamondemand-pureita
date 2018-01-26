# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale mondolunatico_new
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import os
import re
import time
import urllib
import urlparse

from core import httptools
from core import config 
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "mondolunatico_new"
host = "http://mondolunatico.org/stream/"

captcha_url = '%s/pass/CaptchaSecurityImages.php?width=100&height=40&characters=5' % host

PERPAGE = 14


def mainlist(item):
    logger.info("streamondemand-pureita.mondolunatico_new mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Cinema[/COLOR]",
                     action="peliculas",
                     url="%s/genre/al-cinema/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png"),
	            Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas",
                     url="%s/movies/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/hd_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film & Serie TV[COLOR orange] - Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film -[COLOR orange]Anno[/COLOR]",
                     action="years",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Aggiornate[/COLOR]",
                     action="peliculas_tv",
                     extra="serie",
                     url="%s/tvshows/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/new_tvshows_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Lista[/COLOR]",
                     action="peliculas_list",
                     extra="serie",
                     url="%s/lista-serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_serie_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca ...[/COLOR]",
                     action="search",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist


# ==============================================================================================================================================================================
	
def categorias(item):
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '<h2>Film Per Genere</h2>(.*?)</li></ul></nav></div>')

    # Extrae las entradas
    patron = '<li[^>]+><a href="([^"]+)"[^>]>([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        if "Download" in scrapedtitle or "Al Cinema" in scrapedtitle:
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
	
def years(item):
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data
    bloque = scrapertools.get_match(data, '<h2>Release year</h2>(.*?)</li></ul></nav></div>')

    # Extrae las entradas 
    patron = '<li><a href="([^"]+)">(.*?)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
         
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita.mondolunatico_new] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        if item.extra == "movie":
            return pelis_src(item)
    # Continua la ricerca in caso di errore 
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==============================================================================================================================================================================
		
def pelis_src(item):
    logger.info("streamondemand-pureita.mondolunatico_new peliculas")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = '<div class="thumbnail animation-2">\s*<a href="([^"]+)">\s*<img src="([^"]+)" alt="(.*?)" />.*?'
    patron += '<div class="contenido">\s*<p>([^"]+)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios" if "tvshows" in scrapedurl else "findvideos",
                 title=title,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 fulltitle=title,
                 show=title,
                 folder=True), tipo="serie" if "tvshows" in scrapedurl else "movie"))

    return itemlist

# ==============================================================================================================================================================================

def peliculas(item):
    logger.info("streamondemand-pureita.mondolunatico_new peliculas")

    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas
    patron = '<div class="poster">\s*<img src="([^"]+)" \s*alt="([^"]+)">\s*'
    patron += '<div[^>]+>[^>]+></span>(.*?)<\/div>\s*[^>]+>\s*[^>]+>.*?'
    patron += '<a href="([^"]+)">[^>]+></div></a>.*?'
    patron += '<div class="texto">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)


    for i, (scrapedthumbnail, scrapedtitle, rating, scrapedurl, scrapedplot ) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios" if "tvshows" in scrapedurl else "findvideos",
                 contentType="serie" if "tvshows" in scrapedurl else "movie",
                 title=title + "[COLOR orange]" + rating + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo="serie" if "tvshows" in scrapedurl else "movie"))
				 


    # Extrae el paginador
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist
	
# ==============================================================================================================================================================================	

def peliculas_list(item):
    logger.info("streamondemand-pureita.mondolunatico_new peliculas")

    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina

    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = '<b><a href="([^"]+)">([^<]+)<\/a></li></b><br>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    scrapedthumbnail = ""
    scrapedplot = ""
    for i, (scrapedurl, scrapedtitle) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 contentType="tv",
                 title=title,
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
                 action="peliculas_list",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================	

def peliculas_tv(item):
    logger.info("streamondemand-pureita.mondolunatico_new peliculas_tv")

    itemlist = []

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas
    patron = '<div class="poster">\s*<img src="([^"]+)" \s*'
    patron += 'alt="([^"]+)">\s*<div[^>]+>[^>]+><\/span>(.*?)<\/div>\s*'
    patron += '[^>]+>\s*<\/div>\s*<a href="([^"]+)">.*?'
    patron += '<div class="texto">(.*?)</div>'
    matches = re.compile(patron, re.DOTALL).findall(data)


    for i, (scrapedthumbnail, scrapedtitle, rating, scrapedurl, scrapedplot ) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="episodios",
                 contentType="serie",
                 title=title + "[COLOR orange]" + rating + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=title,
                 show=title,
                 plot=scrapedplot,
                 folder=True), tipo='serie'))
				 


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
	
def episodios(item):
    logger.info("streamondemand.mondolunatico episodios")

    itemlist = []

    # Descarga la pagina # https://www.keeplinks.co/p92/59510018b8fc7
    data = httptools.downloadpage(item.url).data

    html = []

    for i in range(2):
        patron = 'href="(https?://www\.keeplinks\.co/p92/([^"]+))'
        matches = re.compile(patron, re.DOTALL).findall(data)
        for keeplinks, id in matches:
            _headers = [['Cookie', 'flag[' + id + ']=1; defaults=1; nopopatall=' + str(int(time.time()))],
                        ['Referer', keeplinks]]

            html.append(httptools.downloadpage(keeplinks, headers=_headers).data)

        patron = r'="(%s/pass/index\.php\?ID=[^"]+)"' % host
        matches = re.compile(patron, re.DOTALL).findall(data)
        for scrapedurl in matches:
            tmp = httptools.downloadpage(scrapedurl).data

            if 'CaptchaSecurityImages.php' in tmp:
                # Descarga el captcha
                img_content = httptools.downloadpage(captcha_url).data

                captcha_fname = os.path.join(config.get_data_path(), __channel__ + "captcha.img")
                with open(captcha_fname, 'wb') as ff:
                    ff.write(img_content)

                from platformcode import captcha

                keyb = captcha.Keyboard(heading='', captcha=captcha_fname)
                keyb.doModal()
                if keyb.isConfirmed():
                    captcha_text = keyb.getText()
                    post_data = urllib.urlencode({'submit1': 'Invia', 'security_code': captcha_text})
                    tmp = httptools.downloadpage(scrapedurl, post=post_data).data

                try:
                    os.remove(captcha_fname)
                except:
                    pass

            html.append(tmp)

        data = '\n'.join(html)

    encontrados = set()

    patron = '<a href="([^"]+)"\s*target="_blank"\s*class="selecttext\s*live">([^<]+)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.split('/')[-1]
        if not scrapedtitle or scrapedtitle in encontrados: continue
        encontrados.add(scrapedtitle)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos_tv",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 fulltitle=item.fulltitle,
                 show=item.show))

    patron = '<p><a href="([^"]+?)">([^<]+?)</a></p>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.split('/')[-1]
        if not scrapedtitle or scrapedtitle in encontrados: continue
        encontrados.add(scrapedtitle)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="findvideos",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 fulltitle=item.fulltitle,
                 show=item.show))

    return itemlist


def findvideos_tv(item):
    logger.info("streamondemand.mondolunatico findvideos")

    itemlist = []

    # Descarga la pagina 
    data = item.url if item.extra == 'serie' else httptools.downloadpage(item.url).data

    # Estrae i contenuti 
    patron = r'noshade>(.*?)<br>.*?<a href="(%s/pass/index\.php\?ID=[^"]+)"' % host
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapedtitle.replace('*', '').replace('Streaming', '').strip()
        title = '%s - [%s]' % (item.title, scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 title=title,
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 fulltitle=item.fulltitle,
                 show=item.show,
                 server='captcha',
                 folder=False))

    patron = 'href="(%s/stream/links/\d+/)"' % host
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        data += httptools.downloadpage(scrapedurl).data

    ### robalo fix obfuscator - start ####

    patron = 'href="(https?://www\.keeplinks\.(?:co|eu)/p92/([^"]+))"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for keeplinks, id in matches:
        headers = [['Cookie', 'flag[' + id + ']=1; defaults=1; nopopatall=' + str(int(time.time()))],
                   ['Referer', keeplinks]]

        html = httptools.downloadpage(keeplinks, headers=headers).data
        data += str(scrapertools.find_multiple_matches(html, '</lable><a href="([^"]+)" target="_blank"'))

    ### robalo fix obfuscator - end ####

    patron = 'src="([^"]+)" frameborder="0"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        data += httptools.downloadpage(scrapedurl).data

    for videoitem in servertools.find_video_items(data=data):
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)

    return itemlist


def play(item):
    logger.info("streamondemand-pureita.mondolunatico play")

    itemlist = []

    if item.server == 'captcha':
        headers = [['Referer', item.url]]

        # Descarga la pagina 
        data = httptools.downloadpage(item.url, headers=headers).data

        if 'CaptchaSecurityImages.php' in data:
            # Descarga el captcha
            img_content = httptools.downloadpage(captcha_url, headers=headers).data

            captcha_fname = os.path.join(config.get_data_path(), __channel__ + "captcha.img")
            with open(captcha_fname, 'wb') as ff:
                ff.write(img_content)

            from platformcode import captcha

            keyb = captcha.Keyboard(heading='', captcha=captcha_fname)
            keyb.doModal()
            if keyb.isConfirmed():
                captcha_text = keyb.getText()
                post_data = urllib.urlencode({'submit1': 'Invia', 'security_code': captcha_text})
                data = httptools.downloadpage(item.url, post=post_data, headers=headers).data

            try:
                os.remove(captcha_fname)
            except:
                pass

        itemlist.extend(servertools.find_video_items(data=data))

        for videoitem in itemlist:
            videoitem.title = item.title
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.show = item.show
            videoitem.plot = item.plot
            videoitem.channel = __channel__
    else:
        itemlist.append(item)

    return itemlist

# =============================================================================================================================================================================	
	
def findvideos_x(item):
    logger.info("streamondemand-pureita.mondolunatico_new findvideos")

    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data

    # Estrae i contenuti 
    patron = 'src="([^"]+)" frameborder="0"'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
        if "dir?" in scrapedurl:
            data += httptools.downloadpage(scrapedurl).url
        else:
            data += httptools.downloadpage(scrapedurl).data

    for videoitem in servertools.find_video_items(data=data):
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)

    return itemlist

	
