import vowing
import time

def intensive_operation(n):
    time.sleep(10)

    return n / 25

vow = vowing.Vow(target = intensive_operation, args = (100,), timeout = 5)
vow.wait_for_me()