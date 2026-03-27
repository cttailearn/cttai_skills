"""
Browser Utilities for Toutiao Publisher Skill
Handles browser launching, stealth features, and common interactions
"""

import json
import time
import random
from pathlib import Path
from typing import Optional, List

from patchright.sync_api import Playwright, BrowserContext, Page
from config import BROWSER_PROFILE_DIR, STATE_FILE, BROWSER_ARGS, USER_AGENT, STEALTH_SCRIPTS_DIR


class BrowserFactory:
    """Factory for creating configured browser contexts"""

    @staticmethod
    def launch_persistent_context(
        playwright: Playwright,
        headless: bool = True,
        user_data_dir: str = str(BROWSER_PROFILE_DIR),
    ) -> BrowserContext:
        """
        Launch a persistent browser context with anti-detection features
        and cookie support.
        Tries Chrome first, falls back to Edge if Chrome is not available.
        """
        # Try Chrome first, then Edge as fallback
        channels = ["chrome", "msedge", "chromium"]

        # Prepare storage_state if state file exists
        storage_state = None
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
                    if "cookies" in state and len(state["cookies"]) > 0:
                        storage_state = str(STATE_FILE)
            except Exception as e:
                print(f"  ⚠️  Could not load state.json: {e}")

        context = None
        for channel in channels:
            try:
                # Use storage_state to load cookies directly
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    channel=channel,
                    headless=headless,
                    no_viewport=True,
                    ignore_default_args=["--enable-automation"],
                    user_agent=USER_AGENT,
                    args=BROWSER_ARGS,
                    storage_state=storage_state,  # Load cookies from state file
                )
                break
            except TypeError:
                # Some versions don't support storage_state parameter
                try:
                    context = playwright.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        channel=channel,
                        headless=headless,
                        no_viewport=True,
                        ignore_default_args=["--enable-automation"],
                        user_agent=USER_AGENT,
                        args=BROWSER_ARGS,
                    )
                    break
                except Exception as e:
                    if channel == channels[-1]:
                        raise Exception(f"Failed to launch browser (tried {', '.join(channels)}): {e}")
                    continue
            except Exception as e:
                if channel == channels[-1]:
                    raise Exception(f"Failed to launch browser (tried {', '.join(channels)}): {e}")
                continue

        # Inject stealth scripts
        StealthUtils.apply_stealth(context)

        return context


class StealthUtils:
    """Human-like interaction utilities with enhanced anti-detection"""

    # Stealth script paths
    STEALTH_SCRIPTS = [
        "stealth-core.js",
        "stealth-timing.js",
        "stealth-mouse.js",
        "stealth-scroll.js",
    ]

    @staticmethod
    def apply_stealth(context: BrowserContext):
        """
        Inject all stealth JavaScript scripts into the browser context.

        Args:
            context: Playwright browser context
        """
        for script_name in StealthUtils.STEALTH_SCRIPTS:
            script_path = STEALTH_SCRIPTS_DIR / script_name
            if script_path.exists():
                try:
                    with open(script_path, "r", encoding="utf-8") as f:
                        script_content = f.read()
                    # Inject into all existing pages
                    for page in context.pages:
                        page.evaluate(script_content)
                except Exception as e:
                    print(f"  ⚠️  Failed to inject {script_name}: {e}")

        # Also inject into new pages via route
        def handle_route(route):
            """Intercept responses to inject stealth scripts"""
            response = route.fetch()
            # Let the original request go through
            route.continue_()

        # Inject on new page creation
        context.on("page", lambda page: StealthUtils._inject_stealth_on_page(page))

    @staticmethod
    def _inject_stealth_on_page(page: Page):
        """Inject stealth scripts into a new page"""
        for script_name in StealthUtils.STEALTH_SCRIPTS:
            script_path = STEALTH_SCRIPTS_DIR / script_name
            if script_path.exists():
                try:
                    with open(script_path, "r", encoding="utf-8") as f:
                        script_content = f.read()
                    page.evaluate(script_content)
                except Exception:
                    pass

    @staticmethod
    def random_delay(min_ms: int = 100, max_ms: int = 500):
        """Add random delay"""
        time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

    @staticmethod
    def smart_delay(mean: float = 2.0, std: float = 0.5):
        """
        Generate a delay based on normal distribution for human-like behavior.

        Args:
            mean: Mean delay in seconds
            std: Standard deviation
        """
        delay = random.gauss(mean, std)
        time.sleep(max(0.1, delay))

    @staticmethod
    def human_type(
        page: Page, selector: str, text: str, wpm_min: int = 320, wpm_max: int = 480
    ):
        """Type with human-like speed"""
        element = page.query_selector(selector)
        if not element:
            try:
                element = page.wait_for_selector(selector, timeout=2000)
            except:
                pass

        if not element:
            print(f"⚠️ Element not found for typing: {selector}")
            return

        element.click()
        for char in text:
            element.type(char, delay=random.uniform(25, 75))
            if random.random() < 0.05:
                time.sleep(random.uniform(0.15, 0.4))

    @staticmethod
    def realistic_click(page: Page, selector: str):
        """Click with realistic mouse movement"""
        element = page.query_selector(selector)
        if not element:
            return

        box = element.bounding_box()
        if box:
            x = box["x"] + box["width"] / 2
            y = box["y"] + box["height"] / 2
            # Use multi-step mouse movement
            StealthUtils._human_mouse_move(page, x, y)

        StealthUtils.random_delay(100, 300)
        element.click()
        StealthUtils.random_delay(100, 300)

    @staticmethod
    def _human_mouse_move(page: Page, target_x: float, target_y: float):
        """
        Move mouse with human-like trajectory using Bezier curves.

        Args:
            page: Playwright page
            target_x: Target X coordinate
            target_y: Target Y coordinate
        """
        # Get current mouse position (estimate from page center if unknown)
        current_x = target_x - 200 + random.randint(0, 400)
        current_y = target_y - 200 + random.randint(0, 400)

        # Calculate distance
        distance = ((target_x - current_x) ** 2 + (target_y - current_y) ** 2) ** 0.5

        # Number of steps based on distance
        num_steps = max(8, min(25, int(distance / 20)))

        # Generate control points for Bezier curve
        dx = target_x - current_x
        dy = target_y - current_y
        dist = max(1, ((dx) ** 2 + (dy) ** 2) ** 0.5)
        perp_x = -dy / dist
        perp_y = dx / dist
        sign = 1 if random.random() > 0.5 else -1
        offset = dist * 0.25 * random.random()

        cp1_x = current_x + dx * 0.33 + perp_x * offset * sign
        cp1_y = current_y + dy * 0.33 + perp_y * offset * sign
        cp2_x = current_x + dx * 0.66 + perp_x * offset * sign
        cp2_y = current_y + dy * 0.66 + perp_y * offset * sign

        # Cubic Bezier interpolation
        def cubic_bezier(t, p0, p1, p2, p3):
            return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

        # Execute movement
        for i in range(1, num_steps + 1):
            t = i / num_steps
            x = cubic_bezier(t, current_x, cp1_x, cp2_x, target_x)
            y = cubic_bezier(t, current_y, cp1_y, cp2_y, target_y)

            page.mouse.move(int(x), int(y))

            # Variable speed - slower at start and end
            base_delay = distance / num_steps / 800 * 1000
            if t < 0.2:
                delay = base_delay * (1 + (0.2 - t) * 2)
            elif t > 0.8:
                delay = base_delay * (1 + (t - 0.8) * 2)
            else:
                delay = base_delay * (0.8 + random.random() * 0.4)

            time.sleep(delay / 1000)

        # Ensure final position is exact
        page.mouse.move(int(target_x), int(target_y))

    @staticmethod
    def human_scroll(page: Page, y: int):
        """
        Scroll to a position with human-like behavior.

        Args:
            page: Playwright page
            y: Target Y scroll position
        """
        current_y = page.evaluate("() => window.scrollY || window.pageYOffset")
        distance = abs(y - current_y)

        if distance < 10:
            return

        # Duration based on distance
        duration = min(2, max(0.3, distance / 800))

        # Add some randomness
        if random.random() < 0.15:
            # Occasional pause during scroll
            time.sleep(random.uniform(0.1, 0.3))

        page.mouse.wheel(0, y - current_y)
        time.sleep(duration)

    @staticmethod
    def random_mouse_move(page: Page):
        """
        Perform a random mouse movement to simulate human behavior.

        Args:
            page: Playwright page
        """
        viewport = page.viewport_size or {"width": 1920, "height": 1080}
        x = random.randint(100, viewport["width"] - 100)
        y = random.randint(100, viewport["height"] - 100)
        StealthUtils._human_mouse_move(page, x, y)

    @staticmethod
    def fake_viewport_size(page: Page):
        """
        Set a fake viewport size with slight randomization.

        Args:
            page: Playwright page
        """
        base_width = 1920
        base_height = 1080
        width = base_width + random.randint(-20, 20)
        height = base_height + random.randint(-15, 15)
        page.set_viewport_size({"width": width, "height": height})

    @staticmethod
    def add_viewport_jitter(page: Page):
        """
        Occasionally adjust viewport slightly to vary fingerprint.

        Args:
            page: Playwright page
        """
        if random.random() < 0.1:  # 10% chance
            StealthUtils.fake_viewport_size(page)

    @staticmethod
    def inject_stealth_scripts(page: Page):
        """
        Manually inject stealth scripts into a page.

        Args:
            page: Playwright page
        """
        StealthUtils._inject_stealth_on_page(page)
