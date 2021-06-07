"""Main module."""

import enum
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
    def visitmethod(cls, method, mode='prefix'):
        if not mode in cls.VISITABLE_TYPES:
            raise ValueError(f"Visit mode {mode} does not exist. Only 'prefix', 'infix' or 'suffix' are available")
        arg_spec = inspect.getfullargspec(method)
        if len(arg_spec.args) < 2:
            raise ValueError(f"{mode} visitmethod {method} of class {cls} does not provide a node argument to visit")
        visitable_argname = arg_spec.args[1]
        if visitable_argname not in arg_spec.annotations:
            raise ValueError(f"Argument {visitable_argname} is not type annotated for {mode} visitmethod {method} of class {cls}")
        type_annotation = arg_spec.annotations[visitable_argname]
        if not hasattr(type_annotation, "accept"):
            raise ValueError(f"Visited type {type_annotation} by {mode} visitmethod {method} of class {cls} does not implement an 'accept' method")
        
        cls.VISITABLE_TYPES[mode][type_annotation] = method
        
        return method
    
    def visit(self, node, mode, *args, **kwargs):
        method = self.VISITABLE_TYPES[mode][type(node)]
        return method(self, node, *args, **kwargs)
    
    def visit_prefix(self, node, *args, **kwargs):
        return self.visit(node, 'prefix', *args, **kwargs)
    
    def visit_infix(self, node, *args, **kwargs):
        return self.visit(node, 'infix', *args, **kwargs)
    
    def visit_suffix(self, node, *args, **kwargs):
        return self.visit(node, 'suffix', *args, **kwargs)



class PostfixVisitor(Visitor):

    @Visitor.visitmethod
    def visit_prefix_any(self, _: object):
        pass
    
    @Visitor.visitmethod
    def visit_infix_any(self, _: object):
        pass


class PrefixVisitor(Visitor):

    @Visitor.visitmethod
    def visit_infix_any(self, _: object):
        pass

    @Visitor.visitmethod
    def visit_postfix_any(self, _: object):
        pass


class InfixVisitor(Visitor):
    
    @Visitor.visitmethod
    def visit_prefix_any(self, _: object):
        pass

    @Visitor.visitmethod
    def visit_postfix_any(self, _: object):
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