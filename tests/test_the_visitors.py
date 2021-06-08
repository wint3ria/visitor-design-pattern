#!/usr/bin/env python

"""Tests for `py6s_rtm_driver` package."""

from visitor_design_pattern import VisitableInterface, visitor, traverse, prefix, infix, suffix

class IgnoredNodeType(VisitableInterface):
    pass

class MyNode(VisitableInterface):

    def __init__(self, name, children=[]):
        self.name = name
        self.children = children
        self.ignored = IgnoredNodeType()

tree = MyNode("A", children=[
    MyNode("B", children=[
        MyNode("C"),
        MyNode("D")
    ]),
    MyNode("E"),
    MyNode("F", children=[
        MyNode("G")
    ]),
    MyNode("H")
])

@visitor()
class PrettyPrinter():

    def __init__(self) -> None:
        self.indent_level = ""

    @prefix()
    def visit_node_prefix(self, node: MyNode):
        if len(node.children):
            print(self.indent_level + "<" + node.name)
        else:
            print(self.indent_level + "<" + node.name, end='')
        self.indent_level += "  "
    
    @infix()
    def visit_node_infix(self, node: MyNode):
        print(",")
    
    @suffix()
    def visit_node_suffix(self, node: MyNode):
        self.indent_level = self.indent_level[2:]
        if len(node.children):
            print("\n" + self.indent_level +  ">", end='')
        else:
            print(">", end='')
    
    @traverse(["prefix", "infix", "suffix"])
    def do_nothing(self, node: IgnoredNodeType):
        pass


@visitor(traversal_mode='prefix')
class PathVisitor():

    def __init__(self) -> None:
        self.path = []
    
    @prefix()
    def visit_node_prefix(self, node: MyNode):
        self.path.append(node.name)
        return self.path

    @traverse(["prefix"])
    def do_nothing(self, node: IgnoredNodeType):
        pass


@visitor()
class IncompleteVisitor():
    pass


def test_prettyprint(capsys):
    pp = PrettyPrinter()
    tree.accept(pp)
    captured = capsys.readouterr()
    assert captured.out == "<A\n  <B\n    <C>,\n    <D>\n  >,\n  <E>,\n  <F\n    <G>\n  >,\n  <H>\n>"

def test_leaf_paths():
    pv = PathVisitor()
    prefix, infix, suffix = tree.accept(pv)
    print(prefix)

def test_incomplete():
    iv = IncompleteVisitor()
    raised = False
    try:
        tree.accept(iv)
    except ValueError:
        raised = True
    if not raised:
        raise RuntimeError("Should raise a value error")

def test_ill_format1():
    raised=False
    try:
        @visitor(traversal_mode='prefix')
        class IllformatedVisitor():
            @prefix()
            def visit_node_prefix(self, node):
                pass
            @traverse(["prefix"])
            def do_nothing(self, node: IgnoredNodeType):
                pass
    except ValueError:
        raised = True
    if not raised:
        raise RuntimeError("Should raise a value error")

def test_ill_format2():
    raised=False
    try:
        @visitor(traversal_mode='prefix')
        class IllformatedVisitor():
            @prefix()
            def visit_node_prefix(self):
                pass
            @traverse(["prefix"])
            def do_nothing(self, node: IgnoredNodeType):
                pass
    except ValueError:
        raised = True
    if not raised:
        raise RuntimeError("Should raise a value error")
