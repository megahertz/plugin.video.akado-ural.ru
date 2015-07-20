import sys
import traceback
import urllib
import urllib2
import ssl
import xml.etree.ElementTree as ET

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

CHANNELS_URL = 'https://wintray.akado-ural.ru/wintray.php?action=media'


def get_params(url):
    parameters = {}
    p1 = url.find('?')
    if p1 >= 0:
        split_params = url[p1 + 1:].split('&')
        for pair in split_params:
            if (len(pair) > 0):
                pair = pair.split('=')
                key = pair[0]
                value = urllib.unquote(urllib.unquote_plus(pair[1])).decode('utf-8')
                parameters[key] = value
    return parameters


def get_channels():
    channels = []
    try:
        if hasattr(ssl, '_create_unverified_context'):
            response = urllib2.urlopen(CHANNELS_URL, context=ssl._create_unverified_context())
        else:
            response = urllib2.urlopen(CHANNELS_URL)

        if not response or response.getcode() != 200:
            raise IOError('Wrong response code')

        root = ET.fromstring(response.read())
        for stream in root.findall('./streams/stream'):
            channels.append({
                'title': stream.attrib['title'].replace('[TV] ', '').encode('utf-8'),
                'uri':   stream.attrib['uri'],
                'desc':  stream.find('descr').text.encode('utf-8')
            })
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        exception = ''.join(lines)
        xbmc.log(exception, xbmc.LOGERROR)
        raise IOError("Service is not available")

    return channels


def make_list_item(stream):
    item = xbmcgui.ListItem(label=stream['title'], path=stream['uri'])
    item.setInfo(type='Video', infoLabels={'Title': stream['title'], 'Plot': stream['desc']})
    return item


def main(params):
    try:
        if 'uri' in params:
            xbmc.Player().play(item=params['uri'], listitem=make_list_item(params))
        else:
            for channel in get_channels():
                link = sys.argv[0] + '?' + urllib.urlencode(channel.items())
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=make_list_item(channel))
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
    except IOError as e:
        addon = xbmcaddon.Addon('plugin.video.akado-ural.ru')
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'
                            % (addon.getAddonInfo('name'), str(e), 5000, addon.getAddonInfo('icon')))

main(get_params(sys.argv[2]))
