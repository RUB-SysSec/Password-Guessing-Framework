# Python Logger wrapper

Simple wrapper for Python logging module. Adds information about location
emitting the debug information (file, line, function) and timestamp.

### Logger mixin

Logger mixin/base class adding verbose logging to subclasses.
Subclasses get debug(), warning() and error() methods which, alongside
the information given, also show location of the message (file, line and
function).

Example mixin usage:

    class MyClass(Logger):
        def my_method(self):
            self.debug('called')

    >>> x = MyClass()
    >>> x.my_method()
    2011-05-15 13:01:45 DEBUG (test.py:7):MyClass.my_method(): called

### logger singleton object

Module also provides a singleton "logger" instance of Logger class, which
can be used when it's not feasible to use the mixin. The logger provides
the same debug(), warning() and error() methods.

Example singleton usage:

    >>> logger.debug('This is a debug message')
    2011-05-15 13:01:45 DEBUG (test.py:12):<module>: This is a debug message

### License

Licensed under MIT license. Forks and pull-requests (and bug reports) are welcome.

### URL
https://github.com/senko/python-logger