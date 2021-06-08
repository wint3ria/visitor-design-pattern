from visitor_design_pattern import VisitableInterface

class MyNode(VisitableInterface):

    """First data node type"""

    def __init__(self, name, children=[]):
        self.name = name
        self.children = children
        self.ignored = AnotherNodeType()

class AnotherNodeType(VisitableInterface):

    """Second data node type"""

    pass

# Instantiate a structure:
root = MyNode("A", children=[
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

from visitor_design_pattern import visitor, prefix, infix, suffix, traverse

@visitor() # Declare the class as visitor
class PrettyPrinter():

    def print(self, *args):
        return print(*args, end="")

    @prefix()
    def visit_node_prefix(self, node: MyNode):
        if len(node.children):
            self.print(f"<{node.name}>")
        else:
            self.print(f"<{node.name}/>")

    @infix()
    def visit_node_infix(self, node: MyNode):
        pass # ignore the infix order

    @suffix()
    def visit_node_suffix(self, node: MyNode):
        if len(node.children):
            self.print(f"</{node.name}>")

    @traverse(["prefix", "infix", "suffix"])
    def do_nothing(self, node: AnotherNodeType):
        pass

pp = PrettyPrinter()
root.accept(pp)