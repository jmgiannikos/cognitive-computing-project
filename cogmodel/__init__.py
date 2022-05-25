__version__ = 1.0

import os
import time
import threading
import queue

log_queue = queue.Queue()


def _write_log():
    r"""
        Function running in a thread which will continue to read  the log_queue
        for new data to write to a file. Items in the log_queue are expected
        to be triples:

        (path, timestamp, message) = item

        This function should usually not be called manually, as the function
        ``log`` will already create suitable items and place them into the 
        queue to be processed when the thread wakes up next.

        The path should specify the file to be written into. Any folders 
        specified along the way, will be created if they are not already 
        present.
        If the file does not exist, it will be created, otherwise the message
        will simple be appended to the file and an additional ``\n`` will be
        put behind each message.
    """
    while True:
        item = log_queue.get()
        if item is None:
            time.sleep(0.1)
            continue
        path, timestamp, msg = item
        dir_path = os.path.dirname(path)
        # Check if there already is a directory for this user:
        if dir_path and not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(path, "a") as f:
            if timestamp:
                f.write("{}: {}\n".format(timestamp, msg))
            elif msg:
                f.write("{}\n".format(msg))
            else:
                f.write("\n")


log_thread = threading.Thread(target=_write_log)
log_thread.setDaemon(True)
log_thread.start()


def log(path, timestamp=None, msg=None):
    r""" 
        Function providing logging capabilities to the GridEnvironment (or any)
        other class importing the cogmodel module. This function will place
        a new item to be logged into the queue which is being processed by the
        ``_write_log`` function in its own thread.

        Parameters
        ---------
        path: str
            The path (relative to the current working directory or absolute) of
            the file into which the message should be logged.
        timestamp: datetime.time, str, number
            A string formatable timestamp of when the message was to be logged.
            This will be appended to each message in the resulting log-file.
        msg: string-formatable
            The actual message to be logged. Can be any string formatable 
            object. A ``\n`` will be placed behind the message automatically 
            when writing to the file.
    """
    log_queue.put((path, timestamp, msg))
    # Add a microsleep so that the other thread can write to the file
    time.sleep(0.001)


# Import some modules and classes for easier import on user-level code
