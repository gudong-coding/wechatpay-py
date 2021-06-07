class WechatPayError(Exception):
    pass


class APIError(WechatPayError):
    pass


class ValidationError(APIError):
    pass


class AuthenticationError(APIError):
    pass


class RequestFailed(APIError):
    pass
