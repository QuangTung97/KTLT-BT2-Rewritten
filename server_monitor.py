import socket
import MySQLdb
import logging
import time
from utils import *


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename="server.log")
    try:
        db = MySQLdb.connect(host="localhost", user="lb",
                             passwd="lb", db="MONITOR")
    except Exception as e:
        print("Can't connect to database")

    hostname = socket.gethostname()

    server_repo = ServerRepository(db)
    ssample_repo = sSampleRepository(db)

    while(True):
        try:
            if not server_repo.exist(hostname):
                server_repo.add(hostname)

            ssample = ServerService.getServerInfo()
            ssample_repo.add(ssample)
        except:
            logging.exception("Error: ")
        time.sleep(60)
