"""
Visitor Design Pattern main module

This module defines the main component exposed by the visitor-design-pattern package:
 - visitor class decorator
 - traverse method decorator
 - prefix method decorator
 - infix method decorator
 - suffix method decorator
 - Visitable interface
"""

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
    raise ValueError(
        f"No suitable {mode} method found for node type"
        f" {type(node)} in visitor {type(self)}"
    )


def _visit_prefix(self, node, *args, **kwargs):
    return self._visit(node, 'prefix', *args, **kwargs)


def _visit_infix(self, node, *args, **kwargs):
    return self._visit(node, 'infix', *args, **kwargs)


def _visit_suffix(self, node, *args, **kwargs):
    return self._visit(node, 'suffix', *args, **kwargs)


def _do_nothing(self, *_, **__):
    pass


class _Wrapper():

    def __init__(self, method) -> None:
        self.method = method
        self.arg_spec = inspect.getfullargspec(method)

    def __call__(self, *args, **kwargs):
        definitive_args = args
        if self.arg_spec.varargs is None:
            definitive_args = args[:len(self.arg_spec.args)]
        definitive_kwargs = {}
        if not self.arg_spec.defaults is None:
            definitive_kwargs = {
                key: kwargs[key] for key in self.arg_spec.args[-len(self.arg_spec.defaults):]
            }
        return self.method(*definitive_args, **definitive_kwargs)


def visitor(traversal_mode=None):

    """
    visitor class decorator

    Mark a class cls as visitor. This initializes the supported
    VISITABLE_TYPES dict in cls, and gather the different visit method
    marked with the `traverse`, `prefix`, `infix` or `suffix` decorators

    Usage:

    .. code:: python

        @visitor()
        def MyVisitor():
            ...
    
    Parameters:
     - traversal_mode: None, "prefix", "infix" or "suffix"
        Specifying a non None traversal_mode prevents other modes to be used in the decorated visitor
    """

    def actual_class_wrapper(cls):

        cls.VISITABLE_TYPES = {
            'prefix': {},
            'infix': {},
            'suffix': {}
        }

        for name, method in cls.__dict__.items():
            modes = getattr(method, "__traversal_mode", None)
            if modes is None:
                continue
            arg_spec = inspect.getfullargspec(method)
            if len(arg_spec.args) < 2:
                raise ValueError(
                    f"visitmethod {name} of class {cls}"
                    " does not provide a node argument to visit"
                )
            visitable_argname = arg_spec.args[1]
            if visitable_argname not in arg_spec.annotations:
                raise ValueError(
                    f"Argument {visitable_argname} is not type"
                    f" annotated for visitmethod {name} of class {cls}"
                )
            type_annotation = arg_spec.annotations[visitable_argname]

            for mode in modes:
                cls.VISITABLE_TYPES[mode][type_annotation] = _Wrapper(method)

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

    """
    visit method decorator

    Mark a method as visit method

    Usage:

    .. code:: python

        @visitor()
        def MyVisitor():

            @traverse("prefix")
            def my_visit_method(self, node: Type):
                ...
            
            ...
    
    Parameters:
     - traversal_mode: "prefix", "infix" or "suffix" or list
        The specified mode defines when the visit method should be called
        when traversing the structure.
        
        A list of multiple modes can be specified.
    """

    if isinstance(traversal_mode, str):
        traversal_mode = [traversal_mode]

    for m in traversal_mode:
        if m not in ALLOWED_VISIT_MODES:
            raise ValueError(
                f"Visit mode {m} does not exist. "
                "Only 'prefix', 'infix' or 'suffix' are available"
            )

    def actual_decorator(method):
        if hasattr(method, '__traversal_mode'):
            method.__traversal_mode += traversal_mode
        else:
            method.__traversal_mode = traversal_mode
        return method

    return actual_decorator


def prefix():
    
    """
    prefix visit method decorator

    Equivalent to traverse('prefix')
    """
    
    return traverse('prefix')


def infix():

    """
    infix visit method decorator

    Equivalent to traverse('infix')
    """

    return traverse("infix")


def suffix():

    """
    suffix visit method decorator

    Equivalent to traverse('suffix')
    """

    return traverse("suffix")


class VisitableInterface():

    """
    Base class for visited nodes of the data structure
    """

    def accept(self, visitor, parent_res=None):

        """
        Default accept method

        This method implement the base logic of the traversal.

        A complex data structure may need a custom implementation.
        In that case users may subclass the VisitableInterface and
        implement their own traversal logic.

        Parameters:
         - visitor: class decorated by the visitor class decorator
         - parent_res: return value of the prefix call of visitor on the current node's parent
        """

        prefix_res = visitor.visit_prefix(self, parent_res=parent_res)
        visited_attrs = {}
        for i, (key, value) in enumerate(self.__dict__.items()):
            if isinstance(value, list):
                visited = []
                for j, x in enumerate(value):
                    if not isinstance(x, VisitableInterface):
                        continue
                    res = x.accept(visitor, parent_res=prefix_res)
                    if res is not None:
                        visited.append(res)
                    if j < len(value) - 1:
                        visitor.visit_infix(self, parent_res=parent_res)
                if len(visited) != 0:
                    visited_attrs[key] = visited
            elif isinstance(value, VisitableInterface):
                visited = value.accept(visitor, parent_res=prefix_res)
                if i < len(self.__dict__.keys()) - 1:
                    visitor.visit_infix(self, parent_res=parent_res)
                if visited is not None:
                    visited_attrs[key] = visited
        postfix_res = visitor.visit_suffix(
            self,
            parent_res=parent_res,
            prefix_res=prefix_res,
            visited_attrs=visited_attrs
        )
        return prefix_res, visited_attrs, postfix_res
