import requests
from datetime import datetime, timedelta

from flask import jsonify

from ..lametric import Frame


class CryptoApi:
    def __init__(self, delay):
        self.delay = delay
        self.root_url = "https://min-api.cryptocompare.com/data"
        self.doge_icon = "a12356"
        self.bitcoin_icon = "i10814"
        self.last_value_time = {}
        self.last_value = {}
        self.history = {}
        self.history_date = {}

    def get_price(self, curr1, curr2):
        try:
            currs = curr1 + curr2
            h_date = self.history_date.get(currs)

            # If the history is not available or is old
            if not h_date or datetime.now().day != h_date.day:
                self._update_history(curr1, curr2)

            last_time = self.last_value_time.get(currs)

            # If cache is old
            if not last_time or (last_time + timedelta(minutes=self.delay)) < datetime.now():
                self.last_value_time[currs] = datetime.now()
                self.last_value[currs] = self._update_price(curr1, curr2)

            normalized_history = self._normalize_history(self.history[currs])
            frame = self._create_frame(curr1, curr2, self.last_value[currs], normalized_history)
            frame = {
                "frames": frame
            }
            return jsonify(frame)

        except Exception as e:
            print("Something went wrong: %s", e)

    def _update_price(self, curr1, curr2):
        url = self.root_url + "/price?fsym=" + curr1 + "&tsyms=" + curr2
        response = requests.get(url)
        data = response.json()
        return data[curr2]

    def _create_frame(self, curr1, curr2, price, history):
        if curr1 == "BTC" or curr1 == "BCH":
            icon = self.bitcoin_icon
        else:
            icon = self.doge_icon

        if curr2 == "USD":
            symbol = "$"
        elif curr2 == "EUR":
            symbol = "€"
        elif curr2 == "GBP":
            symbol = "£"
        else:
            symbol = ""
        return [Frame(icon=icon, text=curr1),
                Frame(icon=icon, text=str(price) + symbol),
                Frame(None, table=history)]

    def _update_history(self, curr1, curr2):
        self.history_date[curr1 + curr2] = datetime.now()
        self.history[curr1 + curr2] = []
        day = 60 * 60 * 24
        for i in reversed(range(14)):
            delay = day * (i + 1)
            unix_time = int(datetime.now().timestamp()) - delay
            url = self.root_url + "/pricehistorical?fsym=" + curr1 + "&tsyms=" + curr2 + "&ts=" + str(unix_time)
            response = requests.get(url)
            data = response.json()
            price = data[curr1][curr2]
            self.history[curr1 + curr2].append(price)

    @staticmethod
    def _normalize_history(history):
        mx = max(history) * 100
        mn = min(history) * 100
        max_delta = mx - mn
        normalized = []
        for i in history:
            i = i * 100
            delta = i - mn
            value = delta * 16 / max_delta
            normalized.append(value)
        return normalized
