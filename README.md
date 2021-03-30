# Vowing
'Vowing' is an alternative to Python's built in async/await system that has been inspired by Javascript's Promise.

## Documentation
### Vow
```python
Vow(target: Callable, args: Iterable, kwargs: dict, timeout = None)
```
`Vow` is the main class and creates an instance of the vow.\
`.get()` returns `None` or an instance of `VowReturn` depending on if the vow hasn't been fulfilled yet.\
`.wait_for_me(wait_func)` executes `wait_func` repeatedly until the vow has been fulfilled.

### VowReturn
`VowReturn` is an internal class used to store the returned value and status of a vow.\
`.ran` is either `True` or `False` depending on if the vow ran successfully.\
`.exception` is either `None` or an instance of `Exception`.\
`.returned` is the value returned by the vow.

### Decorators
```python
@is_vow()
def function():
    ...
```
`is_vow()` turns a function into a vow. All subsequent calls to that function will return a `Vow` object.\
(Yes, pylint might scream at you.)

### Functions
`wait_for_vows(vows, wait_func)` executes `wait_func` repeatedly until all vows in `vows` have been fulfilled.

## Examples
```python
# Simulate an intensive_operation

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
```

```python
# Turn intensive_operation into a vow
import vowing
import time

@vowing.is_vow
def intensive_operation(n):
    time.sleep(10)

    return n / 25

vow = intensive_operation(100)
vow.wait_for_me()
print(vow.get())
```

## Contributing
Pull requests are always welcome.\
If you have any ideas or issues submit them in the issues tab!