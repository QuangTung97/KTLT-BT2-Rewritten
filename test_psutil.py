import unittest
import psutil
import datetime


def BytesToMB(bytes):
    return bytes / 1024 / 1024


# Black box testing
class TestPsutil(unittest.TestCase):
    def test_cpu_count(self):
        self.assertEqual(psutil.cpu_count(), 4)

    def test_cpu_percent(self):
        percent = psutil.cpu_percent()
        self.assertTrue(percent >= 0 and percent <= 400)

    def test_virtual_memory(self):
        total, available, percent, used, free, active, inactive,            \
            buff, cache, shared = psutil.virtual_memory()

        self.assertTrue(percent >= 0 and percent <= 100)
        available = BytesToMB(available)
        cache = BytesToMB(cache)
        self.assertTrue(cache >= 100 and cache < 2048)
        self.assertTrue(available >= 128)
        self.assertTrue(available <= 4096)

    def test_disk_io_counters(self):
        read_count, write_count, read_bytes, write_bytes,                   \
            read_time, write_time, read_merged_count,                       \
            write_merged_count, busy_time 		                            \
            = psutil.disk_io_counters()
        disk_in = BytesToMB(read_bytes)
        disk_out = BytesToMB(write_bytes)
        self.assertTrue(disk_in < 10 * 1024)
        self.assertTrue(disk_in >= 16)
        self.assertTrue(disk_out < 10 * 1024)
        self.assertTrue(disk_out >= 16)

    def test_process_iter_and_uids(self):
        count = 0
        for proc in psutil.process_iter():
            count += 1
            real, effective, saved = proc.uids()
            self.assertTrue(real >= 0 and real <= 0xffff)
            self.assertTrue(effective >= 0 and effective <= 0xffff)
            self.assertTrue(saved >= 0 and saved <= 0xffff)
        self.assertTrue(count > 0)

    def test_psutil_process_functions(self):
        for proc in psutil.process_iter():
            real, effective, saved = proc.uids()
            if real < 1000:
                continue
            self.assertTrue(proc.pid <= 0xffff)
            self.assertTrue(proc.ppid() >= 0 and proc.ppid() <= 0xffff)
            self.assertIsInstance(proc.name(), str)
            self.assertIsInstance(proc.username(), str)
            timestamp = datetime.datetime                   \
                .fromtimestamp(proc.create_time())          \
                .strftime("%Y-%m-%d %H:%M:%S")
            self.assertIsInstance(timestamp, str)
            self.assertIsInstance(proc.cmdline(), list)

            rIO, wIO, rB, wB, read_chars, write_chars       \
                = proc.io_counters()
            rss, vms, shared, text, lib, data, dirty        \
                = proc.memory_info()
            cpu = proc.cpu_percent()
            ram = proc.memory_percent()

            rss = BytesToMB(rss)
            vms = BytesToMB(vms)
            rIO = BytesToMB(rIO)
            wIO = BytesToMB(wIO)

            self.assertTrue(rss <= 1024)
            self.assertTrue(vms <= 1024)
            self.assertTrue(cpu >= 0 and cpu <= 100)
            self.assertTrue(ram >= 0 and ram <= 100)
            self.assertTrue(rIO < 1024)
            self.assertTrue(wIO < 1024)
            break


if __name__ == '__main__':
    unittest.main()
