from flask import Flask, request

from crypto.crypto_api import CryptoApi

app = Flask(__name__)

# Delay in minutes for poll the server in order to get the price info
delay = 3
crypto = CryptoApi(delay)


@app.route('/api/v1.0/crypto/price', methods=['GET'])
def get_price():
    # If currencies not set, we use ETH-USD as placeholder
    curr1 = request.args.get('curr1', 'ETH')
    curr2 = request.args.get('curr2', 'USD')
    return crypto.get_price(curr1, curr2)


if __name__ == '__main__':
    app.run(debug=True, host='192.168.2.3', port=9020)
