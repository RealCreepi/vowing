import vowing
import time

def intensive_operation(n):
    time.sleep(10)

    return n / 25

def while_waiting():
    # do something else
    pass

vow = vowing.Vow(target = intensive_operation, args = (100,))
vow.wait_for_me(while_waiting)

status = vow.get()
result = None
if status.ran:
    result = status.returned

print(result)