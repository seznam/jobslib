
import functools
import inspect

__all__ = ['option', 'OptionsContainer']


class option(object):

    def __new__(cls, func=None, required=False, attrtype=None):
        if func is not None:
            # Decorated without any arguments: @option
            return cls._create_instance(func, required, attrtype)
        else:
            # Decorated with arguments: @option(required=True, ...)
            def decorator(func):
                return cls._create_instance(func, required, attrtype)
            return decorator

    @classmethod
    def _create_instance(cls, func, required, attrtype):
        inst = object.__new__(cls)
        inst.func = func
        inst.required = required
        inst.attrtype = attrtype
        functools.update_wrapper(inst, func)
        return inst

    @classmethod
    def get_option_names(cls, inst):
        res = []
        for attrname, attrvalue in inspect.getmembers(inst.__class__):
            if isinstance(attrvalue, cls):
                res.append(attrname)
        return res

    @classmethod
    def load_all_options(cls, inst):
        for attrname in cls.get_option_names(inst):
            getattr(inst, attrname)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.__qualname__)

    def __get__(self, inst, unused_objtype):
        if inst is None:
            return self
        else:
            if self.func.__name__ not in inst.__dict__:
                try:
                    value = self.func(inst)
                    self._validate(value)
                except Exception as exc:
                    raise ValueError("{}: {}".format(self.__qualname__, exc))
                inst.__dict__[self.__name__] = value
            return inst.__dict__[self.__name__]

    def _validate(self, value):
        if value is None:
            if self.required:
                raise ValueError("Option value is required")
        else:
            if self.attrtype and not isinstance(value, self.attrtype):
                raise ValueError(
                    "{} type is expected".format(self.attrtype.__name__)
                )


class OptionsContainer(object):

    def __init__(self, *args, **kwargs):
        self.initialize(*args, **kwargs)
        option.load_all_options(self)

    def __repr__(self):
        options = (
            (name, getattr(self, name))
            for name in option.get_option_names(self)
        )
        return "<{}: {}>".format(
            self.__class__.__name__,
            ", ".join("{}={!r}".format(k, v) for k, v in options),
        )

    def initialize(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
