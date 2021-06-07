import asyncio
import json
import sys
import uuid

from . import Client, Credential, Validator
import logging

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

logger = logging.getLogger("WechatPay")


async def main(conf):
    logger.info("Started")
    credential = Credential(**conf["credential"])
    validationKeys = []
    for key in conf["validation"]:
        validationKeys.append((key, conf["validation"][key]))
    validator = Validator(validationKeys)
    client = Client(credential=credential, validator=validator)

    trade_no = uuid.uuid1().hex
    url = await client.native_prepay(trade_no, "test.000002.0001", 1)
    logger.info("Native pay created NO: %s, url: %s" % (trade_no, url))

    await asyncio.sleep(1)

    info = await client.query_order_by_trade_no(trade_no)
    logger.info("Trading info: %s" % info)

    await client.close()


if __name__ == "__main__":
    try:
        with open("conf/config.json") as fd:
            conf = json.load(fd)
    except:
        print("Please specify a valid config file.")
        sys.exit(1)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(conf))
    loop.run_until_complete(asyncio.sleep(0.250))
