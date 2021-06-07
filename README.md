# wechatpay-py

This is a python implementation of wechatpay apiv3. Implemented with aiohttp for now. The project is now at alpha state, some features are still missing, use at your own risk.

## Install
```sh
pip install wechatpay-py
```

## Usage
```py
credential = WechatPayCredential(
    mch_id='123456',
    app_id='',
    mch_certificateSerialNumber='asdfasdfadfasdfasdfasdf',
    mch_priv_key_file='path to the key file'
)
validator = WechatPayValidator(
    *, **kwargs
)
client = AsyncWechatPayClient(
    credential,
    validator
)

# get certificates
client.get_certificates()

# create order
# create jsapi order
client.jsapi_prepay(
    description='description of the order',
    out_trade_NO='side'
    notify_url='url of the notification'
    amount=100,
    payer=xyz
)

# create native order
client.native_prepay(
    description='description of the order',
    out_trade_NO='side'
    notify_url='url of the notification'
    amount=100,
    payer=xyz
)

# querys
client.get_order_by_transaction_id(

)
client.get_order_by_out-trade-no(

)
```
