import asyncio
import glob
import os
import subprocess
from pathlib import Path

import aiohttp
from playwright.async_api import Page, async_playwright

from metrics.metrics import metrics_counter_inc
from neo.utils import logger

_BEDROCK_PROJECT = os.environ.get("BEDROCK_PROJECT", "")


def is_bedrock_env() -> bool:
    return _BEDROCK_PROJECT != ""


def find_chromium_executable() -> str:
    """
    Auto-detect Chromium executable file path.
    Priority:
    1. Environment variable CHROMIUM_PATH
    2. Playwright installed Chromium
    3. System installed Chromium/Chrome
    """
    # 1. Check environment variable
    chromium_path = os.environ.get("CHROMIUM_PATH")
    if chromium_path and os.path.isfile(chromium_path):
        logger.info(f"[GlobalBrowser] Using Chromium from environment variable: {chromium_path}")
        return chromium_path

    # 2. Search for Playwright installed Chromium
    # Playwright default installation paths
    playwright_paths = [
        os.path.expanduser("~/.cache/ms-playwright"),  # Linux user directory
        "/root/.cache/ms-playwright",  # Linux root user
        "/home/minimax/.cache/ms-playwright",  # minimax user
        os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""),  # Custom path
    ]

    for base_path in playwright_paths:
        if not base_path or not os.path.isdir(base_path):
            continue
        # Playwright Chromium 路径模式: chromium-*/chrome-linux/chrome
        pattern = os.path.join(base_path, "chromium-*", "chrome-linux", "chrome")
        matches = glob.glob(pattern)
        if matches:
            # Select latest version (take last one by alphabetical sorting)
            chromium_path = sorted(matches)[-1]
            if os.path.isfile(chromium_path):
                logger.info(f"[GlobalBrowser] Found Playwright installed Chromium: {chromium_path}")
                return chromium_path

    # 3. System installed browsers
    system_browsers = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/opt/google/chrome/chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
    ]

    for browser_path in system_browsers:
        if os.path.isfile(browser_path):
            logger.info(f"[GlobalBrowser] Found system browser: {browser_path}")
            return browser_path

    # Browser not found
    raise FileNotFoundError(
        "Chromium browser not found. Please ensure Playwright Chromium is installed (npx playwright install chromium) "
        "or set CHROMIUM_PATH environment variable pointing to the Chromium executable."
    )


async def handle_new_page(page: Page):
    """
    Handle new page events and execute custom logic
    """
    print(f"New page created: {page.url}")


async def launch_chrome_debug(use_chrome_channel: bool = False, headless: bool = False):
    """
    Launch Chrome browser with remote debugging enabled on port 9222
    Returns the browser instance when launched successfully
    """
    try:
        extension_path = Path(os.path.dirname(__file__)).joinpath("browser_extension/error_capture")  # type: ignore
        playwright = await async_playwright().start()

        workspace = "/workspace" if is_bedrock_env() else "./workspace"
        user_data_dir = os.path.join(workspace, "browser", "user_data")

        # Delete browser singleton lock files (if they exist) to avoid conflicts from old lock files restored from NAS
        # Use lexists instead of exists because these files may be symbolic links to non-existent targets
        singleton_files = ["SingletonLock", "SingletonSocket", "SingletonCookie"]
        for filename in singleton_files:
            file_path = os.path.join(user_data_dir, filename)
            try:
                if os.path.lexists(file_path):
                    os.remove(file_path)
                    logger.info(f"Browser singleton file deleted: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete browser singleton file {file_path}: {str(e)}")

        # Check if there's already a Chrome instance running on port 9222
        logger.info("[GlobalBrowser] Checking if Chrome is already running on port 9222...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:9222/json/version", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        logger.info("[GlobalBrowser] Chrome is already running on port 9222, reusing existing instance")
                        browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
                        context = browser.contexts[0] if browser.contexts else await browser.new_context()
                        metrics_counter_inc("agent_browser_launch", {"status": "success"})

                        # Listen for new page events
                        context.on("page", handle_new_page)
                        for page in context.pages:
                            await handle_new_page(page)

                        # Keep browser process alive
                        while True:
                            await asyncio.sleep(1000)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            logger.info("[GlobalBrowser] No existing Chrome instance found, starting a new one...")

        # Prepare Chrome startup parameters
        chrome_args = [
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-background-timer-throttling",
            "--disable-popup-blocking",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-window-activation",
            "--disable-focus-on-load",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-position=0,0",
            "--disable-web-security",
            "--disable-site-isolation-trials",
            "--disable-features=IsolateOrigins,site-per-process",
            f"--disable-extensions-except={extension_path}",
            f"--load-extension={extension_path}",
            "--remote-debugging-port=9222",
            "--remote-debugging-address=127.0.0.1",  # Only allow local access, prevent external connections
        ]

        # Start Chrome using subprocess.Popen
        chromium_path = find_chromium_executable()
        logger.info(f"[GlobalBrowser] Starting Chrome ({chromium_path}) with remote debugging on port 9222...")
        subprocess.Popen(
            [chromium_path] + chrome_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=workspace,
        )

        # Wait for Chrome to start and expose CDP port
        logger.info("[GlobalBrowser] Waiting for Chrome to be ready...")
        max_wait_time = 30
        poll_interval = 1
        waited = 0
        chrome_ready = False

        while waited < max_wait_time:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:9222/json/version", timeout=aiohttp.ClientTimeout(total=2)) as response:
                        if response.status == 200:
                            logger.info(f"[GlobalBrowser] Chrome is ready after {waited} seconds ✓")
                            chrome_ready = True
                            break
            except (aiohttp.ClientError, asyncio.TimeoutError):
                pass

            waited += poll_interval
            logger.debug(f"[GlobalBrowser] Still waiting for Chrome... ({waited}/{max_wait_time}s)")

        if not chrome_ready:
            logger.warning(f"[GlobalBrowser] Chrome may not be ready after {max_wait_time} seconds, proceeding anyway...")

        # Connect to Chrome
        logger.info("[GlobalBrowser] Connecting to Chrome via CDP...")
        browser = await playwright.chromium.connect_over_cdp(
            "http://localhost:9222",
            timeout=30000,  # 30 second timeout for connection
        )
        logger.info("[GlobalBrowser] Successfully connected to Chrome ✓")

        # Create or get browser context
        if browser.contexts:
            context = browser.contexts[0]
        else:
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_data_dir=user_data_dir,
            )

        metrics_counter_inc("agent_browser_launch", {"status": "success"})

        # Listen for new page events
        context.on("page", handle_new_page)

        # Handle already opened pages
        for page in context.pages:
            await handle_new_page(page)

        # Keep browser process alive
        while True:
            await asyncio.sleep(1000)

    except Exception as e:
        logger.exception(f"Failed to launch Chrome browser: {str(e)}")
        metrics_counter_inc("agent_browser_launch", {"status": "failed"})
        raise


if __name__ == "__main__":
    asyncio.run(launch_chrome_debug())
