"""Main module."""

import enum
import inspect


ALLOWED_VISIT_MODES = [
    'prefix',
    'infix',
    'suffix',
]


def _visit(self, node, mode, *args, **kwargs):
    for visitable_type in self.VISITABLE_TYPES[mode]:
        if isinstance(node, visitable_type):
            method = type(self).VISITABLE_TYPES[mode][visitable_type]
            return method(
                self, 
                node, 
                *args, 
                **kwargs
            )
    raise ValueError(f"No suitable {mode} method found for node type {type(node)} in visitor {type(self)}")

def _visit_prefix(self, node, *args, **kwargs):
    return self._visit(node, 'prefix', *args, **kwargs)

def _visit_infix(self, node, *args, **kwargs):
    return self._visit(node, 'infix', *args, **kwargs)
    
def _visit_suffix(self, node, *args, **kwargs):
    return self._visit(node, 'suffix', *args, **kwargs)

def _do_nothing(self, *_, **__):
    pass


class Wrapper():
                
    def __init__(self, method) -> None:
        self.method = method
        self.arg_spec = inspect.getfullargspec(method)
    
    def __call__(self, *args, **kwargs):
        definitive_args = args
        if self.arg_spec.varargs is None:
            definitive_args = args[:len(self.arg_spec.args)]
        definitive_kwargs = kwargs
        if self.arg_spec.varkw is None:
            definitive_kwargs = {
                key: kwargs[key] for key in self.arg_spec.kwonlyargs
            }
        return self.method(*definitive_args, **definitive_kwargs)


def visitor(traversal_mode=None):

    if not traversal_mode in ALLOWED_VISIT_MODES:
        raise ValueError(f"Visit mode {traversal_mode} does not exist. Only 'prefix', 'infix' or 'suffix' are available")

    def actual_class_wrapper(cls):

        cls.VISITABLE_TYPES = {
            'prefix': {},
            'infix': {},
            'suffix': {} 
        }

        for name, method in cls.__dict__.items():
            mode = getattr(method, "__traversal_mode", None)
            if mode is None:
                continue
            arg_spec = inspect.getfullargspec(method)
            if len(arg_spec.args) < 2:
                raise ValueError(f"{mode} visitmethod {name} of class {cls} does not provide a node argument to visit")
            visitable_argname = arg_spec.args[1]
            if visitable_argname not in arg_spec.annotations:
                raise ValueError(f"Argument {visitable_argname} is not type annotated for {mode} visitmethod {name} of class {cls}")
            type_annotation = arg_spec.annotations[visitable_argname]
            
            cls.VISITABLE_TYPES[mode][type_annotation] = Wrapper(method)
        
        setattr(cls, '_visit', _visit)
        setattr(cls, 'visit_prefix', _visit_prefix)
        setattr(cls, 'visit_infix', _visit_infix)
        setattr(cls, 'visit_suffix', _visit_suffix)

        if traversal_mode == 'prefix':
            setattr(cls, 'visit_infix', _do_nothing)
            setattr(cls, 'visit_suffix', _do_nothing)

        if traversal_mode == 'infix':
            setattr(cls, 'visit_prefix', _do_nothing)
            setattr(cls, 'visit_suffix', _do_nothing)

        if traversal_mode == 'suffix':
            setattr(cls, 'visit_infix', _do_nothing)
            setattr(cls, 'visit_prefix', _do_nothing)

        return cls
    
    return actual_class_wrapper


def traverse(traversal_mode):

    if not traversal_mode in ALLOWED_VISIT_MODES:
        raise ValueError(f"Visit mode {traversal_mode} does not exist. Only 'prefix', 'infix' or 'suffix' are available")

    def actual_decorator(method):
        method.__traversal_mode = traversal_mode
        return method
    
    return actual_decorator


def prefix():
    return traverse('prefix')

def infix():
    return traverse("infix")

def suffix():
    return traverse("suffix")


class VisitableInterface():

    DATA_TYPES = [
        str, 
        float, 
        int,
        complex,
        tuple,
        range,
        set,
        frozenset,
        bool,
        bytes,
        bytearray,
        memoryview,
        type(None), 
        dict,
        enum.EnumMeta,
    ]
    
    def accept(self, visitor, parent_res=None):
        prefix_res = visitor.visit_prefix(self, parent_res=parent_res)
        visited_attrs = {}
        for i, (key, value) in enumerate(self.__dict__.items()):
            if type(value) not in self.DATA_TYPES:
                visited = None
                if isinstance(value, list):
                    visited = []
                    for j, x in enumerate(value):
                        visited.append(x.accept(visitor, parent_res=prefix_res))
                        if j < len(value) - 1:
                            visitor.visit_infix(self, parent_res=parent_res)
                else:
                    visited = value.accept(visitor, parent_res=prefix_res)
                    if i < len(self.__dict__.keys()) - 1:
                        visitor.visit_infix(self, parent_res=parent_res)
                visited_attrs[key] = visited
        postfix_res = visitor.visit_suffix(self, parent_res=parent_res, prefix_res=prefix_res, visited_attrs=visited_attrs)
        return prefix_res, visited_attrs, postfix_res