import psutil
import datetime
import socket


# Convert Bytes to MiB
def bytesToMegabytes(n):
    return n / 1024 / 1024


##############################
#       Control Process      #
##############################
class Process:
    def __init__(self, process):
        # basic information of process
        self.pid = process.pid
        self.ppid = process.ppid()
        self.name = process.name()
        self.username = process.username()
        self.timestamp = datetime.datetime              \
            .fromtimestamp(process.create_time())       \
            .strftime("%Y-%m-%d %H:%M:%S")

        real, effective, saved = process.uids()
        self.uid = real
        self.cmd = ' '.join(process.cmdline())

        # List of Process
        self.childs = []
        self.descendants = []

        # Process class in psutil
        self.psutil_process = process

        # Process resources
        self.__getProcessResources(process)

    def __getProcessResources(self, process):
        rIO, wIO, rB, wB, read_chars, write_chars       \
            = process.io_counters()
        rss, vms, shared, text, lib, data, dirty        \
            = process.memory_info()
        self.cpu = process.cpu_percent()
        self.ram = process.memory_percent()

        self.rss = bytesToMegabytes(rss)
        self.vms = bytesToMegabytes(vms)
        self.read_io = bytesToMegabytes(rIO)
        self.write_io = bytesToMegabytes(wIO)

    # Total resource of its and its descendants
    def calculateTotalResources(self):
        self.total_cpu = self.cpu
        self.total_ram = self.ram
        self.total_rss = self.rss
        self.total_vms = self.vms
        self.total_read_io = self.read_io
        self.total_write_io = self.write_io

        for descendant in self.descendants:
            if descendant.psutil_process.is_running():
                self.total_cpu += descendant.cpu
                self.total_ram += descendant.ram
                self.total_rss += descendant.rss
                self.total_vms += descendant.vms
                self.total_read_io                      \
                    += descendant.read_io
                self.total_write_io                     \
                    += descendant.write_io

        self.total_cpu = self.total_cpu / psutil.cpu_count()
        self.total_cpu = round(self.total_cpu, 3)
        self.total_ram = round(self.total_ram, 3)

    # recursive buiding
    def __buildDescendantList(self, childs):
        for child in childs:
            self.descendants.append(child)
            # get childs of child
            self.__buildDescendantList(child.childs)

    def buildDescendantList(self):
            self.__buildDescendantList(self.childs)


class ProcessService:
    @staticmethod
    def getAll(excludeProcess=[], minUID=1000):
        processList = []
        for proc in psutil.process_iter():
            real, effective, saved = proc.uids()
            if real >= minUID:
                p = Process(proc)
                if p.name not in excludeProcess:
                    processList.append(p)

        # Construct parent-child relationship
        for parent in processList:
            for child in processList:
                if parent.pid == child.ppid:
                    parent.childs.append(child)

        for p in processList:
            p.buildDescendantList()
            p.calculateTotalResources()

        return processList


##############################
#       Control User         #
##############################
class User:
    def __init__(self, uid, name, last_used_server):
        self.uid = uid
        self.name = name
        self.last_used_server = last_used_server


class UserRepository:
    def __init__(self, db):
        self.db = db

    def add(self, user):
        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO USER(UID, NAME, SERVER) "
                           "VALUES(%s, %s, %s)",
                           (user.uid, user.name, user.last_used_server))
        except Exception as e:
            print("UserRepository: add()")
            print(e)
        cursor.close()
        self.db.commit()

    def exist(self, uid):
        cursor = self.db.cursor()
        user_exist = False
        try:
            cursor.execute("SELECT `UID` FROM `USER` WHERE "
                           "UID = %s", (uid, ))
            for row in cursor:
                user_exist = True
        except Exception as e:
            print("UserRepository: exist()")
            print(e)
        cursor.close()
        return user_exist

    def update(self, user):
        cursor = self.db.cursor()
        try:
            cursor.execute("UPDATE USER SET SERVER = %s "
                           "WHERE UID = %s AND NAME = %s",
                           (user.last_used_server,
                            user.uid, user.name))
        except Exception as e:
            print("UserRepository: update()")
            print(e)
        cursor.close()
        self.db.commit()

    def get(self, uid):
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT NAME, SERVER FROM USER WHERE "
                           "UID = %s", (uid, ))
        except Exception as e:
            print("UserRepository: get_username()")
            print(e)
        name = None
        last_used_server = None
        for row in cursor:
            name, last_used_server = row
        cursor.close()
        if name is None:
            uid = None
        return User(uid, name, last_used_server)

    def getAll(self):
        cursor = self.db.cursor()
        users = []
        try:
            cursor.execute("SELECT UID, NAME, SERVER "
                           "FROM USER", None)
            for row in cursor:
                uid, name, last_used_server = row
                users.append(User(uid, name, last_used_server))

        except Exception as e:
            print("UserRepository: getAll()")
            print(e)
        return users


##############################
#       Control Server       #
##############################
class ServerRepository:
    def __init__(self, db):
        self.db = db

    def add(self, name):
        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO SERVER(NAME) VALUES(%s)", (name, ))
        except Exception as e:
            print("ServerRepository: add()")
            print(e)
        cursor.close()
        self.db.commit()

    def exist(self, name):
        cursor = self.db.cursor()
        try:
            server = 0
            cursor.execute("SELECT NAME FROM SERVER WHERE NAME = %s", (name, ))
            for row in cursor:
                server = row[0]
        except Exception as e:
            print("ServerRepository: exist()")
            print(e)
        cursor.close()
        return server != 0

    def getAll(self):
        cursor = self.db.cursor()
        try:
            servers = []
            cursor.execute("SELECT NAME FROM SERVER")
            for row in cursor:
                servers.append(row[0])
        except Exception as e:
            print("ServerRepository: getAll()")
            print(e)
        cursor.close()
        return servers


##############################
#        Control Jobs        #
##############################
class Job:
    def __init__(self, proc):
        self.pid = proc.pid
        self.uid = proc.uid
        self.timestamp = proc.timestamp
        self.name = proc.name
        self.cmd = proc.cmd


class JobRepository:
    def __init__(self, db, hostname):
        self.db = db
        self.hostname = hostname

    def add(self, job):
        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO JOB(PID, UID, START_TIME, "
                           "CMD_NAME, COMMAND, SERVER) "
                           "VALUES(%s, %s, %s, %s, %s, %s)",
                           (job.pid, job.uid, job.timestamp,
                            job.name, job.cmd, self.hostname))
        except Exception as e:
            print("JobRepository: add()")
            print(e)
        cursor.close()
        self.db.commit()

    def exist(self, job):
        cursor = self.db.cursor()
        try:
            isRunning = 0
            cursor.execute("SELECT PID FROM JOB WHERE UID = %s "
                           "AND PID = %s AND START_TIME = %s",
                           (job.uid, job.pid, job.timestamp))
            for row in cursor:
                isRunning = row[0]
        except Exception as e:
            print("JobRepository: exist()")
            print(e)
        cursor.close()
        return isRunning != 0


##############################
#       Control jSample      #
##############################
class jSample:
    def __init__(self, proc):
        self.pid = proc.pid
        self.uid = proc.uid
        self.timestamp = proc.timestamp
        self.cpu = proc.total_cpu
        self.ram = proc.total_ram
        self.rss = proc.total_rss
        self.vms = proc.total_vms
        self.read_io = proc.total_read_io
        self.write_io = proc.total_write_io


class jSampleStatistic:
    def __init__(self, avg_cpu, max_cpu, avg_ram, max_ram, run_time):
        self.avg_cpu = round(avg_cpu, 3)
        self.max_cpu = round(max_cpu, 3)
        self.avg_ram = round(avg_ram, 3)
        self.max_ram = round(max_ram, 3)
        self.run_time = run_time


class jSampleRepository:
    def __init__(self, db):
        self.db = db

    def add(self, jsample):
        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO jSAMPLE (PID, UID, START_TIME, CPU, "
                           "RAM, RAM_RSS, RAM_VMS, DISK_IN, DISK_OUT) VALUES "
                           "(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (jsample.pid, jsample.uid, jsample.timestamp,
                            jsample.cpu, jsample.ram, jsample.rss,
                            jsample.vms, jsample.read_io, jsample.write_io))
        except Exception as e:
            print("jSampleRepository: add()")
            print(e)
        cursor.close()
        self.db.commit()

    def statistic(self, uid):
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT AVG(CPU), MAX(CPU), AVG(RAM), MAX(RAM), "
                           "MAX(RUN_TIME) FROM jSAMPLE "
                           "WHERE UID = %s", (uid, ))
        except Exception as e:
            print("jSampleRepository: statistic()")
            print(e)
        for row in cursor:
            avg_cpu, max_cpu, avg_ram, max_ram, run_time = row
        cursor.close()
        return jSampleStatistic(avg_cpu, max_cpu, avg_ram, max_ram, run_time)

    def deleteUidsEarlierThan(self, uid, time):
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM jSAMPLE "
                           "WHERE UID = %s AND RUN_TIME < %s",
                           (uid, time))
            self.db.commit()
            cursor.close()
        except Exception as e:
            print("jSampleRepository: delete_uids_earlier_than()")
            print(e)


##############################
#       Control sSample      #
##############################
class sSample:
    def __init__(self, name, cpu, ram,
                 ram_available, ram_cached, ram_total,
                 disk_in, disk_out):
        self.name = name
        self.cpu = cpu
        self.ram = ram
        self.ram_available = ram_available
        self.ram_cached = ram_cached
        self.ram_total = ram_total
        self.disk_in = disk_in
        self.disk_out = disk_out


class ServerService:
    @staticmethod
    def getServerInfo():
        # CPU usage
        cpu = round(psutil.cpu_percent() / psutil.cpu_count(), 3)

        # RAM usage
        total, available, percent, used, free, active, inactive,            \
            buff, cache, shared = psutil.virtual_memory()
        ram = round(percent, 3)
        ram_available = bytesToMegabytes(available)
        ram_cached = bytesToMegabytes(cache)
        ram_total = bytesToMegabytes(total)

        # IO usage
        read_count, write_count, read_bytes, write_bytes,                   \
            read_time, write_time, read_merged_count,                       \
            write_merged_count, busy_time 		                            \
            = psutil.disk_io_counters()
        disk_in = bytesToMegabytes(read_bytes)
        disk_out = bytesToMegabytes(write_bytes)

        hostname = socket.gethostname()
        return sSample(hostname, cpu, ram, ram_available,
                       ram_cached, ram_total, disk_in, disk_out)


class sSampleRepository:
    def __init__(self, db):
        self.db = db

    def add(self, ssample):
        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO sSAMPLE(NAME, CPU, RAM, "
                           "RAM_AVAILABLE, RAM_CACHED, RAM_TOTAL, "
                           "DISK_IN, DISK_OUT) VALUES"
                           "(%s, %s, %s, %s, %s, %s, %s, %s)",
                           (ssample.name, ssample.cpu, ssample.ram,
                            ssample.ram_available,
                            ssample.ram_cached, ssample.ram_total,
                            ssample.disk_in, ssample.disk_out))
            self.db.commit()
            cursor.close()
        except Exception as e:
            print("sSampleRepository: add()")
            print(e)

    def getMinAndMaxDiskInLaterThan(self, server_name, timestamp):
        min_disk_in = None
        max_disk_in = None
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT MIN(DISK_IN), MAX(DISK_IN) "
                           "FROM sSAMPLE WHERE NAME = %s "
                           "AND TIMESTAMP > %s",
                           (server_name, timestamp))
            for row in cursor:
                min_disk_in, max_disk_in = row
        except Exception as e:
            print("sSampleRepository: getMinAndMaxDiskInLaterThan()")
            print(e)
        cursor.close()
        return min_disk_in, max_disk_in

    def getRamCachedWithDiskInGequal(self, server_name, disk_in):
        cursor = self.db.cursor()
        ram_cached = None
        try:
            cursor.execute("SELECT RAM_CACHED FROM sSAMPLE "
                           "WHERE NAME = %s AND DISK_IN >= %s",
                           (server_name, disk_in))
            for row in cursor:
                ram_cached = row[0]
        except Exception as e:
            print("sSampleRepository: getRamCachedWithDiskInGreaterThan()")
            print(e)
        cursor.close()
        return ram_cached

    def getLatestServerCPUAndTime(self, server_name):
        cursor = self.db.cursor()
        cpu, timestamp = None, None
        try:
            cursor.execute("SELECT CPU, TIMESTAMP FROM sSAMPLE "
                           "WHERE NAME = %s "
                           "ORDER BY TIMESTAMP DESC",
                           (server_name, ))
            for row in cursor:
                cpu, timestamp = row
                break
        except Exception as e:
            print("sSampleRepository: getLatestServerCPUAndTime()")
            print(e)
        return float(cpu), timestamp

    def getServerTotalRam(self, server_name):
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT RAM_TOTAL FROM sSAMPLE "
                           "WHERE NAME = %s", (server_name, ))
            for row in cursor:
                return row[0]
        except Exception as e:
            print("sSampleRepository: getServerTotalRam()")
            print(e)
        return None


##############################
#      Control Prediction    #
##############################
class Prediction:
    def __init__(self, user, stat):
        self.uid = user.uid
        self.username = user.name
        self.last_used_server = user.last_used_server
        self.last_login = stat.run_time
        self.avg_cpu = stat.avg_cpu
        self.max_cpu = stat.max_cpu
        self.avg_ram = stat.avg_ram
        self.max_ram = stat.max_ram


class PredictionRepository:
    def __init__(self, db):
        self.db = db

    def exist(self, uid):
        user_exist = 0
        cursor = self.db.cursor()
        cursor.execute("SELECT UID FROM PREDICTION WHERE "
                       "UID = %s", (uid, ))
        for row in cursor:
            user_exist = row[0]
        cursor.close()
        return user_exist != 0

    def add(self, pred):
        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO PREDICTION "
                           "(UID, USER_NAME, LAST_USED_SERVER, "
                           "LAST_LOGIN, AVG_CPU, MAX_CPU, "
                           "AVG_RAM, MAX_RAM) "
                           "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                           (pred.uid, pred.username, pred.last_used_server,
                            pred.last_login, pred.avg_cpu, pred.max_cpu,
                            pred.avg_ram, pred.max_ram))
            self.db.commit()
            cursor.close()
        except Exception as e:
            print("PredictionRepository: add()")
            print(e)

    def get(self, uid):
        cursor = self.db.cursor()
        username = None
        last_used_server = None
        last_login = None
        avg_cpu = None
        max_cpu = None
        avg_ram = None
        max_ram = None
        try:
            cursor.execute("SELECT USER_NAME, LAST_USED_SERVER, "
                           "LAST_LOGIN, AVG_CPU, MAX_CPU, "
                           "AVG_RAM, MAX_RAM FROM PREDICTION "
                           "WHERE UID = %s", (uid, ))
            for row in cursor:
                username, last_used_server, last_login,       \
                    avg_cpu, max_cpu, avg_ram, max_ram = row
        except Exception as e:
            print("PredictionRepository: get()")
            print(e)
        if username is None:
            uid = None

        user = User(uid, username, last_used_server)
        stat = jSampleStatistic(avg_cpu, max_cpu,
                                avg_ram, max_ram, last_login)
        return Prediction(user, stat)

    def update(self, pred):
        cursor = self.db.cursor()
        try:
            cursor.execute("UPDATE PREDICTION SET "
                           "LAST_USED_SERVER = %s, LAST_LOGIN = %s, "
                           "AVG_CPU = %s, MAX_CPU = %s, "
                           "AVG_RAM = %s, MAX_RAM = %s "
                           "WHERE UID = %s",
                           (pred.last_used_server, pred.last_login,
                            pred.avg_cpu, pred.max_cpu,
                            pred.avg_ram, pred.max_ram, pred.uid))
            cursor.close()
            self.db.commit()
        except Exception as e:
            print("PredictionRepository: update()")
            print(e)

    def getSumAvgCPUFromServerLaterThan(self, server_name, timestamp):
        cursor = self.db.cursor()
        try:
            avgs_cpu = []
            cursor.execute("SELECT AVG_CPU FROM PREDICTION "
                           "WHERE LAST_USED_SERVER = %s "
                           "AND LAST_LOGIN > %s",
                           (server_name, timestamp))
            for row in cursor:
                avgs_cpu.append(row[0])
        except Exception as e:
            print("PredictionRepository: getListAvgCPUFromServerLaterThan()")
            print(e)
        return float(sum(avgs_cpu))
