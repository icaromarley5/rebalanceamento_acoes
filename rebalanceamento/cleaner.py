"""
Creates watchers that remove unused elements from objects after some time
"""

import threading
import time

waitTime = 60 * 5

def _cleanObject(toWatchDict, element):
    """
    Waits for a specified time and removes the element
    """
    time.sleep(waitTime)
    toWatchDict.pop(element, None)
    return None
    
def createCleaner(toWatchDict, element):
    """
    Starts a watcher thread
    """
    threading.Thread(
        target=_cleanObject,
        args=[toWatchDict,element],
        daemon=True).start()
    return None