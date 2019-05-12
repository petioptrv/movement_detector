from threading import Thread, get_ident
from multiprocessing import Process
from multiprocessing import Lock
import time


class ThreadingTest:
    def __init__(self):
        self.test_var = 0
        self.var_lock = Lock()

    def heavy_op(self):
        def inner_op(self):
            for i in range(1000):
                with self.var_lock:
                    print('heavy_op start, var is', self.test_var)
                    self.test_var += 1
        thread = Thread(target=inner_op, args=(self,))
        thread.start()

    def another_op(self):
        for i in range(10):
            with self.var_lock:
                print('another_op start, var is', self.test_var)
                self.test_var += 1


def main():
    thread_obj = ThreadingTest()
    # thread_obj.heavy_op()
    thread = Process(target=thread_obj.another_op)
    print(thread.is_alive())
    print(thread.ident)
    thread.start()
    print(thread.is_alive())
    print(thread.ident)
    thread.join()
    print(thread.is_alive())
    print(thread.ident)


if __name__ == '__main__':
    main()
