import asyncio
import platform


def fix_asyncio_for_windows():
    """
    Ensures proper asyncio event loop policy on Windows platforms.
    This is a fix for the 'aiodns needs a SelectorEventLoop on Windows' issue.
    """
    if platform.system() in ["Windows", "win32"]:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
