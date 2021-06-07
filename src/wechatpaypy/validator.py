import logging
from typing import List, Tuple

import pybase64
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from .errors import ValidationError

logger = logging.getLogger("WechatPay")


class Validator:
    def __init__(self, certs: List[Tuple]) -> None:
        self.serial2Validator = {}

        for serial, cert_file in certs:
            validator = pkcs1_15.new(RSA.importKey(open(cert_file).read()))
            self.serial2Validator[serial] = validator

    def verify(
        self, serial: str, timestamp: str, nonce: str, data: bytes, signature: str
    ) -> None:
        """
        Raises:
            KeyError: the given serial does not exists
            ValueError: verify failed
        """
        try:
            validator = self.serial2Validator[serial]
        except KeyError:
            raise ValidationError("SERIAL_NOT_FOUND", serial)
        message = f"{timestamp}\n{nonce}\n".encode(encoding="ascii") + data + b"\n"
        sig_bin = pybase64.b64decode(signature.encode("ascii"), validate=True)
        logger.debug(
            "Validating Response:\n\tmessage: %s\n\tsignature: %s" % (message, sig_bin)
        )
        try:
            validator.verify(SHA256.new(message), sig_bin)
        except ValueError:
            raise ValidationError("VALIDATION_FAILED")
