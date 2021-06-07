"""Main module."""

import enum
import functools
import inspect
from abc import abstractmethod
from typing import Dict


class Visitor():
    
    VISITABLE_TYPES: Dict[str, dict] = {
        'prefix': {},
        'infix': {},
        'suffix': {} 
    }

    @classmethod
    def decorator(cls, mode):

        def actual_decorator(method):
            
            if not mode in cls.VISITABLE_TYPES:
                raise ValueError(f"Visit mode {mode} does not exist. Only 'prefix', 'infix' or 'suffix' are available")
            arg_spec = inspect.getfullargspec(method)
            if len(arg_spec.args) < 2:
                raise ValueError(f"{mode} visitmethod {method} of class {cls} does not provide a node argument to visit")
            visitable_argname = arg_spec.args[1]
            if visitable_argname not in arg_spec.annotations:
                raise ValueError(f"Argument {visitable_argname} is not type annotated for {mode} visitmethod {method} of class {cls}")
            type_annotation = arg_spec.annotations[visitable_argname]

            @functools.wraps(method)
            def wrapper(*args, **kwargs):
                definitive_args = args
                if arg_spec.varargs is None:
                    definitive_args = args[:len(arg_spec.args)]
                definitive_kwargs = kwargs
                if arg_spec.varkw is None:
                    definitive_kwargs = {
                        key: kwargs[key] for key in arg_spec.kwonlyargs
                    }
                return method(*definitive_args, **definitive_kwargs)
            
            cls.VISITABLE_TYPES[mode][type_annotation] = wrapper

            return method
        
        return actual_decorator

    @classmethod
    def prefix_decorator(cls):
        return cls.decorator('prefix')
    
    @classmethod
    def infix_decorator(cls):
        return cls.decorator('infix')
    
    @classmethod
    def suffix_decorator(cls):
        return cls.decorator('suffix')
        
    
    def _visit(self, node, mode, *args, **kwargs):
        import pprint
        pprint.pprint(self.VISITABLE_TYPES[mode])
        for visitable_type in self.VISITABLE_TYPES[mode]:
            if isinstance(node, visitable_type):
                method = self.VISITABLE_TYPES[mode][visitable_type]
                return method(
                    self, 
                    node, 
                    *args, 
                    **kwargs
                )
        raise ValueError(f"No suitable {mode} method found for node type {type(node)} in visitor {type(self)}")
    
    def visit_prefix(self, node, *args, **kwargs):
        return self._visit(node, 'prefix', *args, **kwargs)
    
    def visit_infix(self, node, *args, **kwargs):
        return self._visit(node, 'infix', *args, **kwargs)
    
    def visit_suffix(self, node, *args, **kwargs):
        return self._visit(node, 'suffix', *args, **kwargs)


class PrefixVisitor(Visitor):

    VISITABLE_TYPES: Dict[str, dict] = {
        'prefix': {},
        'infix': {},
        'suffix': {} 
    }

    @classmethod
    def decorator(cls):
        return super().decorator('prefix')
    
    def visit_infix(cls, *_, **__):
        pass
    
    def visit_suffix(cls, *_, **__):
        pass


class InfixVisitor(Visitor):

    VISITABLE_TYPES: Dict[str, dict] = {
        'prefix': {},
        'infix': {},
        'suffix': {} 
    }

    @classmethod
    def decorator(cls):
        return super().decorator('infix')
    
    def visit_prefix(self, *_, **__):
        pass
    
    def visit_suffix(self, *_, **__):
        pass


class SuffixVisitor(Visitor):

    VISITABLE_TYPES: Dict[str, dict] = {
        'prefix': {},
        'infix': {},
        'suffix': {} 
    }

    @classmethod
    def decorator(cls):
        return super().decorator('suffix')
    
    def visit_prefix(self, *_, **__):
        pass
    
    def visit_infix(self, *_, **__):
        pass


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
    
    def accept(self, visitor: Visitor, parent_res=None):
        print(visitor)
        print(visitor.visit_prefix)
        print(inspect.getfullargspec(visitor.visit_prefix))
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