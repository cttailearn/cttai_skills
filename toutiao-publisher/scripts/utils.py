"""
Utility functions for Toutiao Publisher
Provides smart wait, retry mechanisms, and structured logging
"""

import logging
import random
import time
from functools import wraps
from typing import Callable, Optional, Any, List

from patchright.sync_api import Page

from exceptions import (
    SelectorError,
    AllSelectorsFailedError,
    NetworkError,
    PageLoadTimeoutError,
)


# Configure logger
def setup_logger(name: str = "toutiao-publisher", level: int = logging.DEBUG):
    """Setup structured logger for the module"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()


# Smart delay with normal distribution
def smart_delay(mean: float = 2.0, std: float = 0.5, min_delay: float = 0.1) -> float:
    """
    Generate a delay based on normal distribution for human-like behavior.

    Args:
        mean: Mean delay in seconds
        std: Standard deviation
        min_delay: Minimum delay cap

    Returns:
        Actual delay used
    """
    delay = random.gauss(mean, std)
    delay = max(min_delay, delay)  # Ensure minimum
    time.sleep(delay)
    return delay


def random_delay(min_ms: int = 100, max_ms: int = 500):
    """Legacy random delay function"""
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


# Wait mechanisms
def wait_for_element(
    page: Page,
    selector: str,
    timeout: float = 30,
    state: str = "visible",
    raise_on_fail: bool = True,
) -> Optional[Any]:
    """
    Smart wait for element with specified state.

    Args:
        page: Playwright page object
        selector: CSS selector or text
        timeout: Maximum wait time in seconds
        state: Element state - "attached", "detached", "visible", "hidden"
        raise_on_fail: Whether to raise SelectorError on failure

    Returns:
        Element if found, None otherwise
    """
    try:
        return page.wait_for_selector(selector, timeout=timeout * 1000, state=state)
    except Exception as e:
        if raise_on_fail:
            raise SelectorError(f"元素未找到: {selector}", details={"selector": selector})
        return None


def wait_for_condition(
    page: Page,
    condition_func: Callable[[], bool],
    timeout: float = 30,
    interval: float = 0.5,
    raise_on_fail: bool = False,
) -> bool:
    """
    Wait for a condition function to return True.

    Args:
        page: Playwright page object (unused but kept for API consistency)
        condition_func: Function that returns bool
        timeout: Maximum wait time in seconds
        interval: Check interval in seconds
        raise_on_fail: Whether to raise error on timeout

    Returns:
        True if condition met, False otherwise
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            if condition_func():
                return True
        except Exception:
            pass
        time.sleep(interval)

    if raise_on_fail:
        raise TimeoutError(f"Condition not met within {timeout} seconds")

    return False


def wait_for_url_change(page: Page, expected_url: str = None, timeout: float = 30):
    """
    Wait for URL to change or contain expected substring.

    Args:
        page: Playwright page object
        expected_url: Expected substring in URL (None = any change)
        timeout: Maximum wait time

    Returns:
        True if URL changed as expected
    """
    start = page.url
    start_time = time.time()

    while time.time() - start_time < timeout:
        current_url = page.url
        if current_url != start:
            if expected_url is None or expected_url in current_url:
                return True
        time.sleep(0.5)

    return False


# Retry mechanism
def retry_on_failure(
    func: Callable = None,
    max_attempts: int = 3,
    delay: float = 2,
    backoff: float = 2,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function or decorator
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(
                            f"[{f.__name__}] Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"[{f.__name__}] All {max_attempts} attempts failed")
            raise last_exception
        return wrapper

    if func is None:
        return decorator
    return decorator(func)


# Selector fallback mechanism
def find_element_with_fallback(
    page: Page,
    selectors_config: List[dict],
    required: bool = True,
) -> Optional[Any]:
    """
    Try multiple selectors in order until one works.

    Args:
        page: Playwright page object
        selectors_config: List of selector configs with 'type' and 'value'
        required: Whether to raise error if all fail

    Returns:
        First matching element or None
    """
    tried = []

    for selector in selectors_config:
        selector_type = selector.get("type")
        value = selector.get("value")

        try:
            if selector_type == "css":
                elem = page.locator(value).first
            elif selector_type == "text":
                elem = page.get_by_text(value, exact=False)
            elif selector_type == "placeholder":
                elem = page.get_by_placeholder(value, exact=False)
            elif selector_type == "role":
                elem = page.get_by_role(**selector.get("kwargs", {}))
            else:
                continue

            match_count = elem.count()
            for index in range(min(match_count, 5)):
                candidate = elem.nth(index)
                if candidate.is_visible():
                    logger.debug(f"Selector succeeded: {selector_type}={value} [index={index}]")
                    return candidate

        except Exception as e:
            err_str = str(e)
            logger.debug(f"Selector failed: {selector_type}={value}, error: {err_str}")
            tried.append({"type": selector_type, "value": value, "error": err_str})

    if required:
        raise AllSelectorsFailedError(selectors_tried=tried)

    return None


def click_element_with_fallback(
    page: Page,
    selectors_config: List[dict],
) -> bool:
    """
    Click element using fallback selectors.

    Args:
        page: Playwright page object
        selectors_config: List of selector configs

    Returns:
        True if click successful
    """
    elem = find_element_with_fallback(page, selectors_config)
    if elem:
        elem.click()
        return True
    return False


# Safe navigation
def safe_goto(page: Page, url: str, timeout: float = 60, retry: int = 3):
    """
    Navigate to URL with retry on failure.

    Args:
        page: Playwright page object
        url: Target URL
        timeout: Navigation timeout
        retry: Number of retries

    Raises:
        PageLoadTimeoutError: If all attempts fail
    """
    for attempt in range(retry):
        try:
            page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
            return
        except Exception as e:
            if attempt == retry - 1:
                raise PageLoadTimeoutError(url=url, details={"error": str(e)})
            logger.warning(f"Navigation attempt {attempt + 1} failed: {e}. Retrying...")
            time.sleep(2)


# Verify publish success
def verify_publish_success(page: Page, timeout: float = 10) -> bool:
    """
    Verify that article was published successfully.

    Args:
        page: Playwright page object
        timeout: Time to wait for success indicators

    Returns:
        True if success indicators found
    """
    success_indicators = [
        "发布成功",
        "主页查看",
        "查看已发布",
        "已发布",
        "查看作品",
        "作品管理",
    ]

    published_indicators = ["published", "success", "published_v4", "article/manage"]
    deadline = time.time() + timeout

    while time.time() < deadline:
        for text in success_indicators:
            try:
                locator = page.get_by_text(text, exact=False).first
                if locator.count() > 0 and locator.is_visible():
                    logger.info(f"Publish success verified: found '{text}'")
                    return True
            except Exception:
                continue

        current_url = page.url
        for indicator in published_indicators:
            if indicator in current_url.lower():
                logger.info(f"Publish success verified: URL contains '{indicator}'")
                return True

        time.sleep(0.5)

    logger.warning("Publish success could not be verified")
    return False
