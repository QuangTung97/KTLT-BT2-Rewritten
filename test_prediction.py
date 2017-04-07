from prediction import predictUserLoad
from utils import *
import unittest
from mock import Mock


class TestPredictionMethod(unittest.TestCase):
    def setUp(self):
        # Mock jSampleRepository
        self.jsample_repo = jSampleRepository(None)

        self.stat = jSampleStatistic(
            avg_cpu=10.0, max_cpu=17.2,
            avg_ram=20.0, max_ram=25.4,
            run_time="2017-4-8 11:25:00"
        )
        self.jsample_repo.statistic = Mock(
            return_value=self.stat
        )

        # Mock PredictionRepository
        self.pred_repo = PredictionRepository(None)

        self.user = User(1000, "user1", "server1")

    def test_predictUserLoad_UserExist(self):
        self.pred_repo.exist = Mock(
            return_value=True
        )

        newuser = User(1000, "user1", "server2")

        newstat = jSampleStatistic(
            avg_cpu=15.0, max_cpu=20.3,
            avg_ram=25.333, max_ram=30.1,
            run_time="2017-4-8 10:00:00"
        )
        pred = Prediction(newuser, newstat)

        self.pred_repo.get = Mock(
            return_value=pred
        )
        self.pred_repo.update = Mock()
        self.jsample_repo.deleteUidsEarlierThan = Mock()

        predictUserLoad(self.user, self.jsample_repo,
                        self.pred_repo)

        self.pred_repo.get.assert_called_once_with(1000)

        self.assertEqual(pred.avg_cpu, 12.5)
        self.assertEqual(pred.max_cpu, 20.3)
        self.assertEqual(pred.avg_ram, 22.666)
        self.assertEqual(pred.max_ram, 30.1)
        self.assertEqual(pred.last_used_server, "server1")
        self.assertEqual(pred.last_login, "2017-4-8 11:25:00")

    def test_predictUserLoad_UserNotExist(self):
        self.pred_repo.exist = Mock(
            return_value=False
        )
        self.pred_repo.add = Mock()

        predictUserLoad(self.user, self.jsample_repo,
                        self.pred_repo)

        self.pred_repo.add.assert_called_once()

        # pred_repo.add call with right args
        pred_called = self.pred_repo.add.call_args[0][0]
        pred = Prediction(self.user, self.stat)
        self.assertEqual(pred_called.uid, pred.uid)
        self.assertEqual(pred_called.username, pred.username)
        self.assertEqual(pred_called.last_used_server,
                         pred.last_used_server)
        self.assertEqual(pred_called.last_login, pred.last_login)
        self.assertEqual(pred_called.avg_cpu, pred.avg_cpu)
        self.assertEqual(pred_called.max_cpu, pred.max_cpu)
        self.assertEqual(pred_called.avg_ram, pred.avg_ram)
        self.assertEqual(pred_called.max_ram, pred.max_ram)


if __name__ == '__main__':
    unittest.main()
