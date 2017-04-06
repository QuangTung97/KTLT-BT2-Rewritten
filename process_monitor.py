from utils import *
import time
import socket
import MySQLdb
import logging


if __name__ == '__main__':
    try:
        db = MySQLdb.connect(host="10.0.2.2", user="lb",
                             passwd="lb", db="MONITOR")
    except Exception as e:
        print("Can't connect to DB")
        exit(0)

    excludeProcess = ['sshd', '(sd-pam)']
    hostname = socket.gethostname()

    userRepo = UserRepository(db)
    serverRepo = ServerRepository(db)
    jobRepo = JobRepository(db, hostname)
    jsampleRepo = jSampleRepository(db)

    if not serverRepo.exist(hostname):
        serverRepo.add(hostname)

    logging.basicConfig(level=logging.DEBUG, filename='process.log')

    while(True):
        try:
            processes = ProcessService.getAll(excludeProcess, minUID=1000)
            for proc in processes:
                if not userRepo.exist(proc.uid):
                    userRepo.add(User(proc.uid, proc.username, hostname))

                job = Job(proc)
                if not jobRepo.exist(job):
                    jobRepo.add(job)

                jsampleRepo.add(jSample(proc))
        except:
            logging.exception("Error: ")
        time.sleep(10)
