from utils import *
import socket
import MySQLdb


db = MySQLdb.connect(host="localhost", user="lb",
                     passwd="lb", db="MONITOR")
hostname = socket.gethostname()


s = ServerService.getServerInfo()
ssample_repo = sSampleRepository(db)
server_repo = ServerRepository(db)

print(s.name, s.cpu, s.ram, s.ram_available, s.ram_cached,
      s.disk_in, s.disk_out)
print(server_repo.getAll())
