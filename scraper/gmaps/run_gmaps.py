from concurrent.futures.thread import ThreadPoolExecutor
import csv
import logging
from queue import Queue
from threading import Event
import traceback
from .gmaps import GoogleMaps
from ..config import ROOT_FOLDER
from ..output import get_encoding, Output


logger = logging.getLogger(__name__)


def run_gmaps(file_path, size):
    try:
        int(size)
    except:
        print(f"{size} not valid integer. Please enter a whole number. i.e. -s 100")
        return
    
    event = Event()
    _queue = Queue(maxsize=size)
    gmaps = GoogleMaps(q=_queue)
    output = Output(event)

    if not file_path:
        print("Please enter a file path for queries. i.e. -f example_lb_queries.csv")
        return
    output.encoding = get_encoding(file_path)
    try:
        with open(file_path, "r", encoding=output.encoding) as file:
            queries = csv.reader(file)
            next(queries) # Skip header in file           
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(gmaps.scrape_queries, queries)
                executor.submit(output.run, gmaps.queue)
            output.event.set()
            gmaps.queue.join()
    except KeyboardInterrupt as e:
        output.event.set()
        logger.error(str(e), exc_info=e)
    except Exception as e:
        output.event.set()
        logger.error(str(e), exc_info=e)

