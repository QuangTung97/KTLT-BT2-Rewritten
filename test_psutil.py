import unittest
import psutil
import datetime


def BytesToMB(bytes):
    return bytes / 1024 / 1024


# Black box testing
class TestPsutil(unittest.TestCase):
    def test_cpu_count(self):
        assert(psutil.cpu_count() == 4)

    def test_cpu_percent(self):
        percent = psutil.cpu_percent()
        assert(percent >= 0 and percent <= 400)

    def test_virtual_memory(self):
        total, available, percent, used, free, active, inactive,            \
            buff, cache, shared = psutil.virtual_memory()

        assert(percent >= 0 and percent <= 100)
        available = BytesToMB(available)
        cache = BytesToMB(cache)
        assert(cache >= 100 and cache < 2048)
        assert(available >= 128)
        assert(available <= 4096)

    def test_disk_io_counters(self):
        read_count, write_count, read_bytes, write_bytes,                   \
            read_time, write_time, read_merged_count,                       \
            write_merged_count, busy_time 		                            \
            = psutil.disk_io_counters()
        disk_in = BytesToMB(read_bytes)
        disk_out = BytesToMB(write_bytes)
        assert(disk_in < 10 * 1024)
        assert(disk_in > 128)
        assert(disk_out < 10 * 1024)
        assert(disk_out > 128)

    def test_process_iter_and_uids(self):
        count = 0
        for proc in psutil.process_iter():
            count += 1
            real, effective, saved = proc.uids()
            assert(real >= 0 and real <= 0xffff)
            assert(effective >= 0 and effective <= 0xffff)
            assert(saved >= 0 and saved <= 0xffff)
        assert(count > 0)

    def test_psutil_process_functions(self):
        for proc in psutil.process_iter():
            real, effective, saved = proc.uids()
            if real < 1000:
                continue
            assert(proc.pid <= 0xffff)
            assert(proc.ppid() >= 0 and proc.ppid() <= 0xffff)
            assert(isinstance(proc.name(), str))
            assert(isinstance(proc.username(), str))
            timestamp = datetime.datetime                   \
                .fromtimestamp(proc.create_time())          \
                .strftime("%Y-%m-%d %H:%M:%S")
            assert(isinstance(timestamp, str))
            assert(isinstance(proc.cmdline(), list))

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

            assert(rss <= 1024)
            assert(vms <= 1024)
            assert(cpu >= 0 and cpu <= 100)
            assert(ram >= 0 and ram <= 100)
            assert(rIO < 1024)
            assert(wIO < 1024)
            break


if __name__ == '__main__':
    unittest.main()
