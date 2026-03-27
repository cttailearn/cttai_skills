#!/usr/bin/env python3
"""
Publisher script for Toutiao
Navigates to the publish page with authenticated session.
Enhanced with structured error handling, logging, and selector fallback.
"""

import sys
import argparse
import time
import os
import html
import re
from html.parser import HTMLParser
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from patchright.sync_api import sync_playwright

from config import PUBLISH_URL
from auth_manager import AuthManager
from browser_utils import BrowserFactory, StealthUtils
from md2html import convert as md_to_html
from exceptions import (
    ToutiaoPublisherError,
    AuthenticationError,
    LoginTimeoutError,
    TitleInputError,
    ContentInjectError,
    CoverUploadError,
    PublishButtonError,
    SelectorError,
    AllSelectorsFailedError,
    PublishError,
)
from utils import (
    logger,
    smart_delay,
    wait_for_element,
    wait_for_condition,
    safe_goto,
    find_element_with_fallback,
    click_element_with_fallback,
    verify_publish_success,
    retry_on_failure,
)
import selectors as sel


class _TypableTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.list_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.parts.append("\n")
        elif tag == "li":
            if self.parts and not self.parts[-1].endswith("\n"):
                self.parts.append("\n")
            prefix = "  " * max(0, self.list_depth - 1)
            self.parts.append(f"{prefix}- ")
        elif tag in {"ul", "ol"}:
            self.list_depth += 1
            if self.parts and not self.parts[-1].endswith("\n"):
                self.parts.append("\n")
        elif tag in {"p", "div", "section", "article", "pre", "blockquote"}:
            if self.parts and not self.parts[-1].endswith("\n\n"):
                self.parts.append("\n\n")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if self.parts and not self.parts[-1].endswith("\n\n"):
                self.parts.append("\n\n")

    def handle_endtag(self, tag):
        if tag in {"ul", "ol"} and self.list_depth > 0:
            self.list_depth -= 1
        if tag in {"p", "div", "section", "article", "pre", "blockquote", "li"}:
            if not self.parts or not self.parts[-1].endswith("\n"):
                self.parts.append("\n")
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if not self.parts or not self.parts[-1].endswith("\n\n"):
                self.parts.append("\n\n")

    def handle_data(self, data):
        text = html.unescape(data.replace("\xa0", " "))
        if text:
            self.parts.append(text)

    def get_text(self):
        text = "".join(self.parts)
        text = re.sub(r"\n{3,}", "\n\n", text)
        lines = [line.rstrip() for line in text.splitlines()]
        return "\n".join(lines).strip()


def _html_to_typable_text(html_content: str) -> str:
    parser = _TypableTextParser()
    parser.feed(html_content or "")
    plain_text = parser.get_text()
    return plain_text or re.sub(r"<[^>]+>", "", html_content or "").strip()


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _read_editor_state(page):
    return page.evaluate(
        r"""() => {
            const editor = document.querySelector('.ProseMirror');
            if (!editor) {
                return { text: '', html: '', empty: true };
            }
            const text = (editor.innerText || editor.textContent || '').replace(/\u00a0/g, ' ');
            const html = editor.innerHTML || '';
            const meaningful = text.replace(/\s+/g, '').length === 0 && html.replace(/<[^>]+>/g, '').replace(/\s+/g, '').length === 0;
            return { text, html, empty: meaningful };
        }"""
    )


def _editor_has_meaningful_content(page, expected_text: str = "") -> bool:
    state = _read_editor_state(page)
    actual_text = _normalize_text(state.get("text", ""))
    if not actual_text:
        return False
    if not expected_text:
        return len(actual_text) >= 8
    expected_normalized = _normalize_text(expected_text)
    if not expected_normalized:
        return len(actual_text) >= 8
    if expected_normalized[:40] and expected_normalized[:40] in actual_text:
        return True
    return len(actual_text) >= max(20, int(len(expected_normalized) * 0.6))


def _wait_for_editor_content(page, expected_text: str, timeout: float = 15) -> bool:
    return wait_for_condition(
        page,
        lambda: _editor_has_meaningful_content(page, expected_text),
        timeout=timeout,
        interval=0.5,
        raise_on_fail=False,
    )


def _clear_editor(page, editor):
    editor.click()
    page.keyboard.press("Control+A")
    smart_delay(mean=0.3, std=0.05)
    page.keyboard.press("Backspace")
    wait_for_condition(
        page,
        lambda: not _editor_has_meaningful_content(page),
        timeout=5,
        interval=0.3,
        raise_on_fail=False,
    )


def _paste_html_with_clipboard(page, editor, html_content: str, plain_text: str) -> bool:
    wrote_clipboard = page.evaluate(
        """async ({ html, text }) => {
            try {
                if (!navigator.clipboard || !window.ClipboardItem || !window.Blob) {
                    return false;
                }
                const item = new ClipboardItem({
                    'text/html': new Blob([html], { type: 'text/html' }),
                    'text/plain': new Blob([text], { type: 'text/plain' }),
                });
                await navigator.clipboard.write([item]);
                return true;
            } catch (error) {
                return false;
            }
        }""",
        {"html": html_content, "text": plain_text},
    )
    if not wrote_clipboard:
        return False
    editor.click()
    smart_delay(mean=0.5, std=0.1)
    page.keyboard.press("Control+V")
    return _wait_for_editor_content(page, plain_text, timeout=8)


def _type_content_human_like(page, editor, plain_text: str) -> bool:
    editor.click()
    paragraphs = [paragraph for paragraph in re.split(r"\n{2,}", plain_text) if paragraph.strip()]
    if not paragraphs and plain_text.strip():
        paragraphs = [plain_text.strip()]
    for index, paragraph in enumerate(paragraphs):
        lines = paragraph.splitlines() or [paragraph]
        for line_index, line in enumerate(lines):
            if line:
                page.keyboard.type(line, delay=18)
            if line_index < len(lines) - 1:
                page.keyboard.press("Shift+Enter")
        if index < len(paragraphs) - 1:
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
        if index and index % 4 == 0:
            smart_delay(mean=0.35, std=0.08)
    return _wait_for_editor_content(page, plain_text, timeout=10)


def _has_visible_text(page, texts) -> str:
    for text in texts:
        try:
            locator = page.get_by_text(text, exact=False).first
            if locator.count() > 0 and locator.is_visible():
                return text
        except Exception:
            continue
    return ""


def _wait_for_save_success(page, timeout: float = 12) -> bool:
    success_texts = ["草稿已保存", "保存成功", "已保存"]
    return wait_for_condition(
        page,
        lambda: bool(_has_visible_text(page, success_texts)),
        timeout=timeout,
        interval=0.5,
        raise_on_fail=False,
    )


def _trigger_manual_save(page):
    save_btn = find_element_with_fallback(page, sel.SAVE_DRAFT_SELECTORS, required=False)
    if save_btn:
        try:
            if save_btn.is_visible() and save_btn.is_enabled():
                logger.info("Clicking Save Draft button...")
                save_btn.click()
                return
        except Exception:
            pass
    editor = page.locator(".ProseMirror").first
    editor.click()
    page.keyboard.type(" ", delay=20)
    page.keyboard.press("Backspace")


def _detect_publish_error(page) -> str:
    return _has_visible_text(
        page,
        [
            "保存失败",
            "发布失败",
            "内容不能为空",
            "标题不能为空",
            "请先保存",
            "请完善文章内容",
            "请稍后重试",
        ],
    )


def publish(
    title=None,
    content_html=None,
    cover_image_path=None,
    dry_run=False,
    headless=False,
    no_cover=False,
    raw=False,
):
    """
    Launches a browser to the Toutiao publishing page and automates the posting process.

    Args:
        title: Article title
        content_html: Article content (markdown or HTML)
        cover_image_path: Path to cover image
        dry_run: If True, fill fields but don't publish
        headless: Run in headless mode
        no_cover: Select 'No Cover' option
        raw: If True, paste content as raw text without HTML conversion

    Returns:
        True if publish successful, False otherwise
    """
    # Optimize title
    if title:
        original_title = title
        if len(title) > 30:
            title = title[:30]
            logger.warning(f"Title truncated to 30 chars: '{original_title}' -> '{title}'")
        elif len(title) < 2:
            title = f"{title}..."
            logger.warning(f"Title extended to min 2 chars: '{original_title}' -> '{title}'")

    # Convert Markdown to HTML if needed
    final_html = content_html or ""
    if content_html and not raw:
        logger.info("Converting Markdown to HTML...")
        try:
            final_html = md_to_html(content_html)
            logger.debug(f"HTML preview: {final_html[:100]}...")
        except Exception as e:
            logger.warning(f"Conversion failed, using raw text: {e}")
            final_html = content_html

    logger.info(f"Launching Toutiao Publisher (Headless: {headless})...")

    context = None
    playwright = None
    try:
        playwright = sync_playwright().start()
        context = BrowserFactory.launch_persistent_context(playwright, headless=headless)
        page = context.pages[0] if context.pages else context.new_page()

        # Inject stealth scripts manually as extra measure
        StealthUtils.inject_stealth_scripts(page)

        # Navigate to publishing page
        logger.info(f"Navigating to publish page...")
        safe_goto(page, PUBLISH_URL, timeout=60)

        # Handle login redirect
        if not _handle_login_redirect(page, context, headless):
            if headless:
                logger.warning("Cannot proceed in headless mode without valid authentication")
            logger.error("Login redirect handling failed")
            return False

        logger.info("Publishing page loaded")
        smart_delay(mean=2.5, std=0.5)

        # Handle overlays
        _handle_overlays(page)

        # 1. Fill Title
        if title:
            _fill_title(page, title)

        # 2. Fill Content
        if content_html:
            _fill_content(page, final_html)

        # 3. Handle Cover
        if cover_image_path:
            _upload_cover(page, cover_image_path)
        elif no_cover:
            _select_no_cover(page)

        # 4. Publish
        if not dry_run:
            success = _execute_publish(page)
        else:
            logger.info("Dry run: skipping final publish")
            smart_delay(5)
            success = True

        # Keep browser open for inspection in non-headless mode
        if not headless and success:
            logger.info("Browser open for inspection. Closing in 60s...")
            time.sleep(60)

        return success

    except AllSelectorsFailedError as e:
        logger.error(f"Element selection failed: {e}")
        return False
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        return False
    except PublishError as e:
        logger.error(f"Publish error: {e}")
        return False
    except ToutiaoPublisherError as e:
        logger.error(f"Publisher error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up browser resources
        if context:
            try:
                context.close()
            except Exception:
                pass
        if playwright:
            try:
                playwright.stop()
            except Exception:
                pass


def _handle_login_redirect(page, context, headless) -> bool:
    """Handle redirect to login page.

    In headless mode (Linux servers, CI/CD), we rely on pre-saved cookies
    and cannot perform interactive login. If cookies are valid, the page
    should not redirect to login.

    Args:
        page: Playwright page object
        context: Browser context with cookies
        headless: Whether running in headless mode

    Returns:
        True if authenticated and can continue, False otherwise
    """
    current_url = page.url
    login_patterns = ["auth/page/login", "sso.toutiao.com"]

    if not any(pattern in current_url for pattern in login_patterns):
        return True

    # Already on login page - cookies may be invalid or expired
    if headless:
        logger.warning("Redirected to login page in headless mode.")
        logger.warning("Cannot perform interactive login in headless mode.")
        logger.warning("Please ensure cookies are valid and not expired.")
        return False

    # Non-headless mode: wait for user to login manually
    logger.warning("Redirected to login page, waiting for user login...")
    logger.info("Please scan QR code in the browser window")

    start_time = time.time()
    timeout = 300  # 5 minutes

    while time.time() - start_time < timeout:
        try:
            current_url = page.url
            if "profile_v4" in current_url or "graphic/publish" in current_url:
                logger.info("Login detected!")
                _save_state(context)
                return True

            if PUBLISH_URL in current_url:
                return True
        except Exception:
            pass
        time.sleep(1)

    logger.error("Login timeout")
    raise LoginTimeoutError("Login timeout", details={"timeout": timeout})


def _save_state(context):
    """Save browser state."""
    try:
        state_path = Path("data/browser_state/state.json")
        state_path.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(state_path))
        logger.info("Browser state saved")
    except Exception as e:
        logger.warning(f"Could not save state: {e}")


def _handle_overlays(page):
    """Handle obstructing overlays."""
    logger.debug("Checking for overlays...")

    for selector in sel.OVERLAY_SELECTORS:
        try:
            elem = page.locator(selector["value"]).first
            if elem.count() > 0 and elem.is_visible():
                logger.info(f"Found overlay: {selector['value']}")
                elem.click(force=True, position={"x": 10, "y": 10})
                page.evaluate(f"document.querySelector('{selector['value']}')?.remove()")
                smart_delay(mean=1, std=0.3)
        except Exception:
            pass


def _fill_title(page, title) -> bool:
    """Fill the title input field."""
    logger.info(f"Filling title: {title[:20]}...")

    try:
        elem = find_element_with_fallback(page, sel.TITLE_INPUT_SELECTORS)
        elem.fill(title)
        logger.info("Title filled successfully")
        return True
    except AllSelectorsFailedError as ex:
        logger.error("Failed to fill title - all selectors failed")
        raise TitleInputError("Failed to fill title", details={"title": title}) from ex
    except Exception:
        import traceback
        logger.error(f"Failed to fill title. Traceback: {traceback.format_exc()}")
        raise TitleInputError("Failed to fill title", details={"title": title})


def _fill_content(page, html_content) -> bool:
    """Fill the content editor."""
    logger.info("Filling article content...")

    try:
        wait_for_element(page, ".ProseMirror", timeout=10, state="attached")
        elem = find_element_with_fallback(page, sel.CONTENT_EDITOR_SELECTORS)
        plain_text = _html_to_typable_text(html_content)
        strategies = [
            ("clipboard paste", lambda: _paste_html_with_clipboard(page, elem, html_content, plain_text)),
            ("human typing", lambda: _type_content_human_like(page, elem, plain_text)),
        ]

        for strategy_name, strategy in strategies:
            logger.info(f"Trying content input strategy: {strategy_name}")
            _clear_editor(page, elem)
            if strategy():
                logger.info(f"Editor accepted content via {strategy_name}")
                smart_delay(mean=4, std=0.6)
                _verify_draft_saved(page, plain_text)
                return True
            logger.warning(f"Content input strategy failed: {strategy_name}")

        raise ContentInjectError("Editor did not accept article content")

    except AllSelectorsFailedError:
        logger.error("Failed to fill content - editor not found")
        raise ContentInjectError("Content editor not found")
    except Exception as ex:
        err_msg = str(ex)
        logger.error(f"Failed to fill content: {err_msg}")
        raise ContentInjectError(err_msg)


def _verify_draft_saved(page, expected_text: str):
    """Verify that draft was saved."""
    logger.debug("Checking draft save status...")

    if not _wait_for_editor_content(page, expected_text, timeout=10):
        raise ContentInjectError("Editor did not retain the article content")

    for _ in range(3):
        if _wait_for_save_success(page, timeout=12):
            logger.info("Draft saved successfully")
            return True

        logger.warning("Save not confirmed, attempting recovery...")
        _recover_from_save_failure(page, expected_text)

        if _wait_for_save_success(page, timeout=12):
            logger.info("Draft saved successfully after recovery")
            return True

    raise ContentInjectError("Draft save could not be confirmed")


def _recover_from_save_failure(page, expected_text: str):
    """Recover from save failure."""
    try:
        if not _wait_for_editor_content(page, expected_text, timeout=5):
            raise ContentInjectError("Article content disappeared before draft save")
        _trigger_manual_save(page)
        smart_delay(mean=4, std=0.6)
    except Exception as e:
        logger.warning(f"Recovery failed: {e}")


def _upload_cover(page, image_path) -> bool:
    """Upload cover image."""
    logger.info(f"Uploading cover: {image_path}")

    if not os.path.exists(image_path):
        logger.error(f"Cover image not found: {image_path}")
        raise CoverUploadError(f"File not found: {image_path}")

    try:
        # Click Add Cover
        elem = find_element_with_fallback(page, sel.ADD_COVER_SELECTORS)
        elem.click()
        smart_delay(1)

        # Click Upload Local
        elem = find_element_with_fallback(page, sel.UPLOAD_LOCAL_SELECTORS)
        elem.click()
        smart_delay(1)

        # Upload file
        file_input = page.locator("input[type='file']").first
        file_input.set_input_files(image_path)
        logger.info("File sent to input")

        # Confirm upload
        smart_delay(2)
        try:
            confirm_btn = page.locator("button[data-e2e='imageUploadConfirm-btn']")
            if confirm_btn.is_visible(timeout=30000):
                confirm_btn.click()
        except Exception:
            # Fallback
            page.locator(".byte-btn-primary").filter(has_text="确定").last.click()

        logger.info("Cover uploaded")
        smart_delay(2)
        return True

    except AllSelectorsFailedError:
        logger.error("Cover upload UI elements not found")
        raise CoverUploadError("Cover upload UI not found")
    except Exception as ex:
        err_msg = str(ex)
        logger.error(f"Cover upload failed: {err_msg}")
        raise CoverUploadError(err_msg)


def _select_no_cover(page) -> bool:
    """Select no cover option."""
    logger.info("Selecting 'No Cover' option...")

    try:
        elem = find_element_with_fallback(page, sel.NO_COVER_SELECTORS)
        elem.click()
        logger.info("No cover selected")
        smart_delay(2)
        return True
    except AllSelectorsFailedError:
        logger.warning("Could not select no cover option")
        return False


def _execute_publish(page) -> bool:
    """Execute the publish sequence."""
    logger.info("Starting publish sequence...")

    try:
        if _has_visible_text(page, ["保存失败", "保存草稿失败"]):
            raise PublishError("Draft save failed, publish aborted")

        initial_btn = _find_publish_button(page)
        if initial_btn:
            logger.info("Clicking initial publish button...")
            initial_btn.click()
        else:
            logger.warning("Publish button not found, attempting JS click")
            page.evaluate("document.querySelector('.publish-btn')?.click()")

        logger.info("Waiting for interface response...")
        smart_delay(mean=5, std=1)

        publish_error = _detect_publish_error(page)
        if publish_error:
            raise PublishError(f"Publish blocked by page validation: {publish_error}")

        if verify_publish_success(page, timeout=8):
            logger.info("✨ Publish successful!")
            return True

        if not _click_final_confirm(page):
            logger.error("Could not find final confirm button")
            raise PublishButtonError("Final confirm button not found")

        logger.info("Final button clicked, verifying success...")
        smart_delay(mean=3, std=0.5)

        publish_error = _detect_publish_error(page)
        if publish_error:
            raise PublishError(f"Publish blocked by page validation: {publish_error}")

        if verify_publish_success(page, timeout=20):
            logger.info("✨ Publish successful!")
            return True

        raise PublishError("Publish success could not be verified")

    except PublishButtonError:
        raise
    except Exception as ex:
        err_msg = str(ex)
        logger.error(f"Publish sequence failed: {err_msg}")
        raise PublishError(err_msg)


def _find_publish_button(page):
    """Find the publish button with fallback."""
    for selector in sel.PUBLISH_BUTTON_SELECTORS:
        try:
            if selector["type"] == "text":
                elem = page.locator("button").filter(has_text=selector["value"]).last
            else:
                elem = page.locator(selector["value"]).first

            if elem.count() > 0 and elem.is_visible() and elem.is_enabled():
                return elem
        except Exception:
            continue
    return None


def _click_final_confirm(page) -> bool:
    """Click the final confirmation button."""
    deadline = time.time() + 12
    while time.time() < deadline:
        for selector in sel.FINAL_CONFIRM_BUTTON_SELECTORS:
            try:
                if selector["type"] == "css":
                    elem = page.locator(selector["value"]).first
                elif selector["type"] == "text":
                    elem = page.get_by_text(selector["value"], exact=False).first
                else:
                    continue

                if elem.count() > 0 and elem.is_visible():
                    elem.click()
                    logger.info(f"Clicked final button: {selector['value']}")
                    return True
            except Exception:
                continue

        if verify_publish_success(page, timeout=1):
            return True

        time.sleep(0.5)

    return False


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(description="Toutiao Article Publisher")
    parser.add_argument("--title", help="Article title")
    parser.add_argument("--content", help="Article content (string or file path)")
    parser.add_argument("--cover", help="Path to cover image")
    parser.add_argument("--dry-run", action="store_true", help="Fill but don't publish")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--no-cover", action="store_true", help="No cover")
    parser.add_argument("--raw", action="store_true", help="Raw text content")

    args = parser.parse_args()

    content = args.content
    if content and os.path.exists(content):
        with open(content, "r", encoding="utf-8") as f:
            content = f.read()

    success = publish(
        title=args.title,
        content_html=content,
        cover_image_path=args.cover,
        dry_run=args.dry_run,
        headless=args.headless,
        no_cover=args.no_cover,
        raw=args.raw,
    )

    if success:
        logger.info("Operation completed successfully")
    else:
        logger.error("Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
