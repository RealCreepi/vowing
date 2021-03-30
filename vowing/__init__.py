"""
MIT License

Copyright (c) 2021 Creepi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import inspect
import queue
import time
import sys
from threading import Thread
from typing import Any, Callable, Iterable, Union


class VowReturn:
    def __init__(self, ran: bool, exception: Exception, returned: Any) -> None:
        self.ran = ran
        self.exception = exception
        self.returned = returned

    def __repr__(self):
        return f"VowReturn(ran = {self.ran}, exception = {self.exception}, returned = {self.returned})"


class VowThread(Thread):
    def __init__(self, target: Callable, args: Iterable) -> None:
        super().__init__(target = target, args = args, daemon = True)
        self.__killed = False
  
    def start(self):
        self.__run_backup = self.run
        self.run = self.__run 
        Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace

        return None
    
    def localtrace(self, frame, event, arg):
        if (self.__killed) and event == 'line':
                raise SystemExit()

        return self.localtrace
    
    def kill(self):
        self.__killed = True


class Vow:
    def __init__(self, target: Callable, args: Iterable = tuple(), kwargs: dict = dict(), timeout = None) -> None:
        self.timeout = timeout

        self.__return_queue = queue.Queue()
        self.__returned = None
        self.__start_time = time.time()
        self.__thread = VowThread(target = self.__returning_thread_wrapper, args = (self.__return_queue, target, args, kwargs))
        self.__thread.start()
    
    def __returning_thread_wrapper(self, sync_queue, target, args, kwargs):
        ran = True
        returned = None
        exception = None

        try:
            returned = target(*args, **kwargs)
        
        except Exception as e:
            ran = False
            exception = e
            returned = None
        
        sync_queue.put({
            "ran": ran,
            "exception": exception,
            "returned": returned
        })

    def get(self, validate: bool = True) -> Union[None, VowReturn]:
        if validate: self.validate()

        if not self.__returned:
            try:
                returned_data = self.__return_queue.get_nowait()
                
                ran = returned_data["ran"]
                exception = returned_data["exception"]
                returned = returned_data["returned"]
                
                self.__returned = VowReturn(ran, exception, returned)
            
            except queue.Empty:
                return None
        
        return self.__returned

    def wait_for_me(self, wait_func: Callable = (lambda: None)) -> None:
        while not self.get():
            wait_func()

    def validate(self) -> None:
        if not self.__returned:
            if self.timeout and (time.time() - self.__start_time) > self.timeout:
                self.__thread.kill()
                raise TimeoutError(f"Vow was broken and timed out after {self.timeout}s.")


def is_vow(func) -> Callable:
    def wrapper(*args, **kwargs) -> Vow:
        if inspect.isclass(func):
            raise TypeError("'is_vow' can't be applied to a class.")

        return Vow(target = func, args = args, kwargs = kwargs)
    
    return wrapper


def wait_for_vows(vows: Iterable[Vow], wait_func: Callable = (lambda: None)) -> None:
    while None in [vow.get() for vow in vows]:
        wait_func()