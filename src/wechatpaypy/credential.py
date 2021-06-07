import logging
import secrets
import time

import pybase64
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

logger = logging.getLogger("WechatPay")


class Credential:
    """Merchant credential which could sign a request"""

    def __init__(
        self,
        *,
        mch_id: str,
        app_id: str,
        cert_serial: str,
        cert_key_file: str,
        notify_url: str,
    ) -> None:
        self.mch_id = mch_id
        self.app_id = app_id
        self.cert_serial = cert_serial
        self.cert_key_file = cert_key_file
        self.notify_url = notify_url

        self.priv_key = RSA.importKey(open(cert_key_file).read())
        self.signer = pkcs1_15.new(self.priv_key)

    @staticmethod
    def get_timestamp() -> str:
        return str(int(time.time()))

    @staticmethod
    def get_nonce() -> str:
        return secrets.token_hex(16)

    def sign(self, method: str, url: str, body: bytes = b"") -> str:
        timestamp = self.get_timestamp()
        nonce = self.get_nonce()

        message = (
            f"{method}\n{url}\n{timestamp}\n{nonce}\n".encode(encoding="ascii")
            + body
            + b"\n"
        )

        signature = self.signer.sign(SHA256.new((message)))
        b64sig = pybase64.b64encode(signature).decode("ascii")
        logger.debug("Signed:\n\tmessage: %s\n\tsignature: %s" % (message, b64sig))

        return timestamp, nonce, b64sig

    def build_authorization(self, method: str, url: str, body: bytes = b"") -> str:
        logger.debug("Building Auth: %s, %s, %s", method, url, body)
        timestamp, nonce, signature = self.sign(method, url, body)
        auth = f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",serial_no="{self.cert_serial}",timestamp="{timestamp}",nonce_str="{nonce}",signature="{signature}"'
        logger.debug("Authentication:\n\t%s" % auth)
        return auth
