import logging
from urllib.parse import urlencode

import aiohttp
import orjson

from .credential import Credential
from .errors import APIError, ValidationError
from .validator import Validator
from collections import namedtuple

logger = logging.getLogger("WechatPay")


ApiResponse = namedtuple("ApiResonse", ["status", "content"])


class Client:
    base_url = "https://api.mch.weixin.qq.com"

    def __init__(self, credential: Credential, validator: Validator) -> None:
        """
        One session is created and use accrose the client, according to aiohttp documentation
        see
        """
        self.credential = credential
        self.validator = validator
        self.session = aiohttp.ClientSession(
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    async def close(self):
        await self.session.close()

    async def request_pay_v3(
        self,
        url: str,
        method: str = "POST",
        *,
        params: dict = None,
        data: dict = None,
    ) -> ApiResponse:
        """Low level request, you should use high level request instead"""
        desturl = url
        databytes = b""
        if method == "GET":
            if params:
                desturl = desturl + "?" + urlencode(params)
        elif method == "POST":
            if data:
                databytes = orjson.dumps(data)

        headers = {
            "Authorization": self.credential.build_authorization(
                method, desturl, databytes
            ),
        }

        async with self.session.request(
            method, self.base_url + desturl, headers=headers, data=databytes
        ) as resp:
            status = resp.status
            data = await resp.read()
            content = orjson.loads(data)

            # check this before verify signature
            if status >= 400:
                raise APIError(status, content, resp.headers)

            self.validator.verify(
                resp.headers["Wechatpay-Serial"],
                resp.headers["Wechatpay-Timestamp"],
                resp.headers["Wechatpay-Nonce"],
                data,
                resp.headers["Wechatpay-Signature"],
            )

            return ApiResponse(status, content)

    async def query_order_by_transaction_id(self, transaction_id):
        method = "GET"
        url = f"/v3/pay/transactions/id/{transaction_id}"
        params = {"mchid": self.credential.mch_id}
        status, content = await self.request_pay_v3(url, method, params=params)
        return content

    async def query_order_by_trade_no(self, trade_no):
        method = "GET"
        url = f"/v3/pay/transactions/out-trade-no/{trade_no}"
        params = {"mchid": self.credential.mch_id}

        status, content = await self.request_pay_v3(url, method, params=params)
        return content

    async def native_prepay(self, trade_no: str, desp: str, price: int) -> str:
        """
        params:
            price: price in cents
        Returns: wechat pay url, eg. weixin://wxpay/bizpayurl/up?pr=NwY5Mz9&groupid=00
        """
        method = "POST"
        url = "/v3/pay/transactions/native"
        data = {
            "appid": self.credential.app_id,
            "mchid": self.credential.mch_id,
            "out_trade_no": trade_no,
            "notify_url": self.credential.notify_url,
            "description": desp,
            "amount": {"total": price},
        }

        status, content = await self.request_pay_v3(url, method, data=data)
        return content["code_url"]
