import MySQLdb
import sys
import datetime
from utils import *


# Find the server with the most available CPU
def leastLoadServer(server_repo, ssample_repo, pred_repo):
    servers = server_repo.getAll()
    server_dict = {}
    for server in servers:
        latest_time = 0
        server_cpu, latest_time =                                       \
            ssample_repo.getLatestServerCPUAndTime(server)
        if latest_time == 0:
            continue
        last_hour = latest_time - datetime.timedelta(hours=1)

        sum_avg_cpu =                                                   \
            pred_repo.getSumAvgCPUFromServerLaterThan(
                server, last_hour)
        # Total cpu
        server_dict[server] = server_cpu + sum_avg_cpu

    # Print the server with the lowest load
    print(min(server_dict, key=server_dict.get))


def loadBalance(uid, server_repo, ssample_repo, pred_repo):
    if pred_repo.exist(uid):
        # Prediction Record of UID
        pred = pred_repo.get(uid)
        last_hour = pred.last_login - datetime.timedelta(hours=1)
        min_disk_in, max_disk_in                                        \
            = ssample_repo.getMinAndMaxDiskInLaterThan(
                        pred.last_used_server,
                        last_hour)

        disk_difference = max_disk_in - min_disk_in
        ram_cached = ssample_repo.getRamCachedWithDiskInGequal(
                            pred.last_used_server,
                            max_disk_in)

        # See if cache is still available
        cache_available = cacheAvailable(
                disk_difference, pred.avg_ram, ram_cached)

        # if there is still cache available,
        # we check if the server has enough memory CPU
        # to support the user
        if cache_available:
            server_cpu, latest_time =                                  \
                    ssample_repo.getLatestServerCPUAndTime(
                        pred.last_used_server)

            sum_avg_cpu =                                               \
                pred_repo.getSumAvgCPUFromServerLaterThan(
                    pred.last_used_server,
                    latest_time - datetime.timedelta(hours=1))

            if server_cpu < sum_avg_cpu:
                server_cpu = sum_avg_cpu

            total_cpu = server_cpu + pred.avg_cpu
            if total_cpu < 100:
                print(pred.last_used_server)
            else:
                leastLoadServer(server_repo, ssample_repo, pred_repo)
        else:
            leastLoadServer(server_repo, ssample_repo, pred_repo)
    else:
        leastLoadServer(server_repo, ssample_repo, pred_repo)


def cacheAvailable(disk_diff, user_avg_ram, cache):
    cache_not_replace = cache - disk_diff
    if cache_not_replace > user_avg_ram:
        return True
    else:
        return False


if __name__ == '__main__':
    # connect to database
    try:
        db = MySQLdb.connect(host="localhost", user="lb",
                             passwd="lb", db="MONITOR")
    except Exception as e:
        print("Can't connect to database")

    server_repo = ServerRepository(db)
    pred_repo = PredictionRepository(db)
    ssample_repo = sSampleRepository(db)

    uid = int(sys.argv[1])

    loadBalance(uid, server_repo, ssample_repo, pred_repo)
