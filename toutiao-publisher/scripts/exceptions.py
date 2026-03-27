"""
Custom Exceptions and Error Codes for Toutiao Publisher
Provides structured error handling with error codes for easy debugging
"""

from typing import Optional


# Error Code Definitions
ERROR_CODES = {
    # Authentication errors (AUTH_xxx)
    "AUTH_001": "认证状态无效或已过期",
    "AUTH_002": "登录超时",
    "AUTH_003": "登录页面重定向失败",
    "AUTH_004": "无法保存认证状态",

    # Publish errors (PUB_xxx)
    "PUB_001": "标题输入失败",
    "PUB_002": "内容注入失败",
    "PUB_003": "封面上传失败",
    "PUB_004": "发布按钮未找到",
    "PUB_005": "发布确认失败",
    "PUB_006": "发布成功验证失败",

    # Selector errors (SEL_xxx)
    "SEL_001": "元素未找到",
    "SEL_002": "元素不可见",
    "SEL_003": "所有选择器都失败",

    # Network errors (NET_xxx)
    "NET_001": "页面加载超时",
    "NET_002": "网络请求失败",
    "NET_003": "重试次数耗尽",

    # General errors (SYS_xxx)
    "SYS_001": "浏览器上下文错误",
    "SYS_002": "文件操作失败",
}


class ToutiaoPublisherError(Exception):
    """Base exception for all Toutiao Publisher errors"""

    def __init__(self, message: str = None, code: str = None, details: dict = None):
        self.message = message or ERROR_CODES.get(code, "Unknown error")
        self.code = code or "SYS_000"
        self.details = details or {}
        super().__init__(f"[{self.code}] {self.message}")

    def to_dict(self):
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class AuthenticationError(ToutiaoPublisherError):
    """Raised when authentication fails"""

    def __init__(self, message: str = None, code: str = "AUTH_001", details: dict = None):
        super().__init__(message, code, details)


class LoginTimeoutError(AuthenticationError):
    """Raised when login times out"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(message, "AUTH_002", details)


class PublishError(ToutiaoPublisherError):
    """Raised when publishing fails"""

    def __init__(self, message: str = None, code: str = "PUB_001", details: dict = None):
        super().__init__(message, code, details)


class TitleInputError(PublishError):
    """Raised when title input fails"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(message, "PUB_001", details)


class ContentInjectError(PublishError):
    """Raised when content injection fails"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(message, "PUB_002", details)


class CoverUploadError(PublishError):
    """Raised when cover upload fails"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(message, "PUB_003", details)


class PublishButtonError(PublishError):
    """Raised when publish button cannot be found"""

    def __init__(self, message: str = None, details: dict = None):
        super().__init__(message, "PUB_004", details)


class SelectorError(ToutiaoPublisherError):
    """Raised when element selection fails"""

    def __init__(self, message: str = None, code: str = "SEL_001", details: dict = None):
        super().__init__(message, code, details)


class AllSelectorsFailedError(SelectorError):
    """Raised when all fallback selectors fail"""

    def __init__(self, selectors_tried: list = None, details: dict = None):
        details = details or {}
        if selectors_tried:
            details["selectors_tried"] = selectors_tried
        super().__init__("所有选择器都失败", "SEL_003", details)


class NetworkError(ToutiaoPublisherError):
    """Raised for network-related errors"""

    def __init__(self, message: str = None, code: str = "NET_001", details: dict = None):
        super().__init__(message, code, details)


class PageLoadTimeoutError(NetworkError):
    """Raised when page load times out"""

    def __init__(self, url: str = None, details: dict = None):
        details = details or {}
        if url:
            details["url"] = url
        super().__init__(f"页面加载超时: {url}" if url else None, "NET_001", details)
