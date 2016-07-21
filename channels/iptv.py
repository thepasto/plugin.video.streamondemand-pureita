# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand - XBMC Plugin
# Canal para filmontv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------
import base64
import re

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "iptv"
__category__ = "B,F"
__type__ = "generic"
__title__ = "iptv (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.iptv mainlist")

    itemlist = []

    enckey = False
    data = scrapertools.cache_page('http://www.filmphp.com/Kodi/Protected/index.txt')
    patron = '<externallink>([^<]+)</externallink>'
    url = scrapertools.find_single_match(data, patron)
    if '$$LSProEncKey=' in url:
        enckey = url.split('$$LSProEncKey=')[1].split('$$')[0]
        rp = '$$LSProEncKey=%s$$' % enckey
        url = url.replace(rp, "")

    data = scrapertools.cache_page(url)
    if enckey:
        from core import aes
        enckey = enckey.encode("ascii")
        missingbytes = 16 - len(enckey)
        enckey += chr(0) * missingbytes
        data = base64.b64decode(data)
        decryptor = aes.new(enckey, aes.MODE_ECB, IV=None)
        data = decryptor.decrypt(data).split('\0')[0]

        patron = '<title>([^<]+)</title>\s*<link>([^<]+)</link>'
        matches = re.compile(patron, re.DOTALL).findall(data)
        for scrapedtitle, scrapedurl in matches:
            itemlist.append(
                Item(channel=__channel__,
                     action='play',
                     title=scrapedtitle,
                     url=scrapedurl,
                     fulltitle=scrapedtitle,
                     show=scrapedtitle))

    return itemlist
