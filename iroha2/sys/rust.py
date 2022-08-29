# Export
from typing import NamedTuple
import enum
import collections
import dataclasses
from importlib import import_module
from ..iroha2 import Dict, List

ClassPath = str


def query(*path):

    class IntoInner:

        @staticmethod
        def parse_output(out):
            for p in path:
                out = out[p]
            return out

    return IntoInner


def to_rust(obj):
    if isinstance(obj, list):
        return [to_rust(i) for i in obj]
    if isinstance(obj, tuple):
        if len(obj) == 0:
            return None
        else:
            return tuple(to_rust(i) for i in obj)
    if isinstance(obj, dict):
        return {k: to_rust(v) for k, v in obj.items()}

    return obj.to_rust() if hasattr(obj, 'to_rust') else obj


def get_class(path) -> type:
    if isinstance(path, type):
        return path
    path = path.split('.')
    name = path[-1]
    import_path = '.' + '.'.join(path[:-1])
    mod = import_module(import_path, package='iroha2.sys')
    return getattr(mod, name)


# TODO: bring in line with other factories
class _Enum(type):

    @staticmethod
    def _make_class(variants):

        class RustEnum:
            __variants = None
            Type = enum.Enum('Type', [k for k, v in variants])

            def __str__(self):
                return f"{self.variant.name}"

            @classmethod
            def _variants(cls):
                if not cls.__variants:
                    cls.__variants = {k: get_class(v) for k, v in variants}
                return cls.__variants

            @classmethod
            def from_rust(cls, value):
                # TODO: Dict should inherit from Mapping
                if isinstance(value, collections.Mapping)\
                   or isinstance(value, Dict):
                    if len(list(value.keys())) > 1:
                        raise ValueError

                    variant = list(value.keys())[0]
                    variant_class = cls._variants()[variant]
                    variant_value = value[variant]
                    if hasattr(variant_class, 'from_rust'):
                        variant_value = variant_class.from_rust(variant_value)
                    if hasattr(variant_class, '_into_wrapped'):
                        variant_value = variant_class._into_wrapped(
                            variant_value)
                    return cls(variant_value, variant)
                elif type(value) is str:
                    if value in cls._variants().keys():
                        return cls(None, value)
                    else:
                        raise ValueError
                else:
                    raise ValueError

            def _from_value(self, value):
                for variant, ty in self._variants().items():
                    if isinstance(value, ty):
                        self.variant = self.Type[variant]
                        self.value = value
                        return

                raise TypeError(f"Unknown type for enum: {value}")

            def __init__(self, value, variant=None):
                if variant is None:
                    self._from_value(value)
                else:
                    self.variant = self.Type[variant]
                    self.value = value

            def to_rust(self) -> dict:
                return {self.variant.name: to_rust(self.value)}

        for var, ty in variants:

            def constructor_meta(value, var, ty):
                if isinstance(ty, str):
                    ty = get_class(ty)

                if not isinstance(value, ty):
                    value = ty(value)
                return RustEnum(value, variant=var)

            # Type here might be a string also
            if ty == type(None):
                # https://stackoverflow.com/questions/2295290/what-do-lambda-function-closures-capture
                constructor = (
                    lambda var: lambda: RustEnum(None, variant=var))(var)
            else:

                constructor = (
                    lambda var, ty: lambda v: constructor_meta(v, var, ty))(
                        var, ty)

            setattr(RustEnum, var, staticmethod(constructor))

        return RustEnum

    def __getitem__(
        cls,
        variants,
    ) -> type:
        if isinstance(variants, tuple) and isinstance(variants[0], str):
            variants = [variants]

        return cls.__class__._make_class(variants)


class Enum(metaclass=_Enum):
    pass


def make_tuple(name, fields=None):
    if fields is None:
        fields = []
    cls = NamedTuple(name, [(f"f{i}", typ) for i, typ in enumerate(fields)])
    cls.to_rust = lambda tup: tuple(to_rust(i) for i in tup)
    return cls


def make_struct(structname, fields):

    def struct_to_rust(s):
        return {field: to_rust(getattr(s, field)) for (field, _) in fields}

    def struct_from_rust(cls, obj):
        args = []
        for (argname, argtype) in fields:
            argtype = get_class(argtype)
            try:
                # Special case, since those are flattened
                # TODO: handle it better
                if structname == "EvaluatesTo" or structname == "Metadata":
                    arg = obj
                else:
                    arg = obj[argname]
            except KeyError:
                raise KeyError(
                    f"Error deserializing {structname}: "
                    f"no key for field {argname}"
                )
            if hasattr(argtype, "from_rust"):
                args.append(argtype.from_rust(arg))
            else:
                args.append(arg)
        return cls(*args)

    return dataclasses.make_dataclass(structname,
                                      fields,
                                      namespace={
                                          "to_rust": struct_to_rust,
                                          "from_rust": classmethod(struct_from_rust),
                                      })


def wrapper(base):

    def decorate(subclass):

        def into_wrapped(self):
            return subclass._from_inner(self)

        base._into_wrapped = into_wrapped

        def from_inner(inner):
            inner.__class__ = subclass
            return inner

        subclass._from_inner = from_inner

        return subclass
    return decorate
