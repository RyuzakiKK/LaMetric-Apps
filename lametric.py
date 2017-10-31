import socket
from enum import Enum
import requests


class Priority(Enum):
    info = "info",
    warning = "warning"
    critical = "critical"


class Sound (dict):
    """ Represents notification sound """
    def __init__(self, sound, repeat=1):
        """
        Constructor
        :param sound: Sound id, full list can be found at
            http://lametric-documentation.readthedocs.io/en/latest/reference-docs/device-notifications.html
        :param repeat: Sound repeat count, if set to 0 sound will be played until notification is dismissed
        """
        dict.__init__({})
        self["category"] = "notifications"
        self["id"] = sound
        self["repeat"] = repeat
        return


class Frame (dict):
    """ Represents single frame. Frame can display icon, text and graph. """

    def __init__(self, icon, text=None, table=None):
        """
        Constructor
        :param icon: icon id in form of "iXXX" for static icons, or "aXXXX" for animated ones.
        :param text: text message to be displayed
        :param chart: graph to display. It needs to be a numeric values list
        """
        dict.__init__({})
        if icon is not None:
            self["icon"] = icon
        if text:
            self["text"] = text
        else:
            self["chartData"] = table


class Notification (dict):
    """ Represents notification message """
    def __init__(self, priority, frames, sound=None):
        """
        Constructor
        :param priority: notification priority, Priority enum.
        :param frames: list of Frame objects
        :param sound: Sound object
        """
        dict.__init__({})
        self["priority"] = priority.name
        if sound:
            self["model"] = {
                "frames": frames,
                "sound": sound
            }
        else:
            self["model"] = {
                "frames": frames
            }
        return


class LaMetricTime:
    """
    Allows to send notification to your LaMetric Time device in local network
    """
    def __init__(self, ip_address, port, api_key):
        """
        Constructor
        :param ip_address: IP address of the LaMetric Time
        :param port: 8080 for insecure connection or 4343 for secure one
        :param api_key: device API key
        """
        self.notifications_url = "https://{0}:{1}/api/v2/device/notifications".format(ip_address, port)
        self._api_key = api_key
        return

    def send(self, notification):
        """
        Sends notification to LaMetric Time
        :param notification: instance of Notification class
        :return: (status_code, body)
        """
        try:
            r = requests.post(self.notifications_url, json=notification, auth=('dev', self._api_key), verify=False)
            return r.status_code, r.text
        except Exception:
            # lametric unreachable
            return 500, "lametric unreachable"


def send_push(ip, api_key, notification):
    # IP address can be found in LaMetric Time app -> Settings -> Wi-Fi
    # API Key can be found in your developer account at https://developer.lametric.com/user/devices
    lametric_time = LaMetricTime(ip, port=4343, api_key=api_key)
    status_code, body = lametric_time.send(notification)
    # print("{0}:{1}".format(status_code, body))


def is_online(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, 22))
    if result == 0:
        return True
    else:
        return False
