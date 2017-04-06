from utils import *
import time
import MySQLdb


def changeAlgorithm(new_avg, prev_avg, difference):
    return new_avg


def predictUserLoad(user, jsample_repo, pred_repo):
    # Current system statistic
    stat = jsample_repo.statistic(user.uid)
    user_exist = pred_repo.exist(user.uid)
    if not user_exist:
        pred_repo.add(Prediction(user, stat))
    else:
        # As previous system statistic
        pred = pred_repo.get(user.uid)

        # We want to adjust the value of average CPU for the user
        # in the prediction table by using an algorithm that can
        # adjust the value based on the difference
        difference = stat.avg_cpu - pred.avg_cpu
        new_avg_cpu = changeAlgorithm(stat.avg_cpu, pred.avg_cpu,
                                      difference)

        # Similiar with RAM
        difference = stat.avg_ram - pred.avg_ram
        new_avg_ram = changeAlgorithm(stat.avg_ram, pred.avg_ram,
                                      difference)

        # We check if the user have heavier CPU jobs
        # running in the system
        if stat.max_cpu > pred.max_cpu:
            new_max_cpu = stat.max_cpu
        else:
            new_max_cpu = pred.max_cpu

        # Check if the user have heavier RAM jobs
        # running in the system
        if stat.max_ram > pred.max_ram:
            new_max_ram = stat.max_ram
        else:
            new_max_ram = pred.max_ram

        # Update the prediction table with the
        # new calculated data
        pred.last_used_server = user.last_used_server
        pred.last_login = stat.run_time
        pred.avg_cpu = new_avg_cpu
        pred.max_cpu = new_max_cpu
        pred.avg_ram = new_avg_ram
        pred.max_ram = new_max_ram

        # Clean up the user monitor table
        jsample_repo.deleteUidsEarlierThan(user.uid, stat.run_time)


if __name__ == '__main__':
    # Connect to database
    try:
        db = MySQLdb.connect(host="localhost", user="lb",
                             passwd="lb", db="MONITOR")
    except Exception as e:
        print("Khong the ket noi DB")
        print(e)

    user_repo = UserRepository(db)
    jsample_repo = jSampleRepository(db)
    pred_repo = PredictionRepository(db)

    while (True):
        users = user_repo.getAll()

        for user in users:
            predictUserLoad(user, jsample_repo, pred_repo)

        time.sleep(10)
