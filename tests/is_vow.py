import vowing
import time

@vowing.is_vow
def intensive_operation(n):
    time.sleep(10)

    return n / 25

vow = intensive_operation(100)
vow.wait_for_me()
print(vow.get())