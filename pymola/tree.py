#!/usr/bin/env python
"""
Tools for tree walking and visiting etc.
"""

from __future__ import print_function, absolute_import, division, unicode_literals

import numpy as np
import copy
import logging
import copy # TODO
import sys
from collections import OrderedDict
from typing import Union

from . import ast

CLASS_SEPARATOR = '.'

logger = logging.getLogger("pymola")


# TODO Flatten function vs. conversion classes


# noinspection PyPep8Naming
class TreeListener(object):
    """
    Defines interface for tree listeners.
    """

    def __init__(self):
        self.context = {}

    def enterEvery(self, tree: ast.Node) -> None:
        self.context[type(tree).__name__] = tree

    def exitEvery(self, tree: ast.Node):
        self.context[type(tree).__name__] = None

    def enterClass(self, tree: ast.Class) -> None:
        pass

    def exitClass(self, tree: ast.Class) -> None:
        pass

    def enterImportAsClause(self, tree: ast.ImportAsClause) -> None:
        pass

    def exitImportAsClause(self, tree: ast.ImportAsClause) -> None:
        pass

    def enterImportFromClause(self, tree: ast.ImportFromClause) -> None:
        pass

    def exitImportFromClause(self, tree: ast.ImportFromClause) -> None:
        pass

    def enterElementModification(self, tree: ast.ElementModification) -> None:
        pass

    def exitElementModification(self, tree: ast.ElementModification) -> None:
        pass

    def enterClassModification(self, tree: ast.ClassModification) -> None:
        pass

    def exitClassModification(self, tree: ast.ClassModification) -> None:
        pass

    def enterExtendsClause(self, tree: ast.ExtendsClause) -> None:
        pass

    def exitExtendsClause(self, tree: ast.ExtendsClause) -> None:
        pass

    def enterIfExpression(self, tree: ast.IfExpression) -> None:
        pass

    def exitIfExpression(self, tree: ast.IfExpression) -> None:
        pass

    def enterExpression(self, tree: ast.Expression) -> None:
        pass

    def exitExpression(self, tree: ast.Expression) -> None:
        pass

    def enterIfEquation(self, tree: ast.IfEquation) -> None:
        pass

    def exitIfEquation(self, tree: ast.IfEquation) -> None:
        pass

    def enterForIndex(self, tree: ast.ForIndex) -> None:
        pass

    def exitForIndex(self, tree: ast.ForIndex) -> None:
        pass

    def enterForEquation(self, tree: ast.ForEquation) -> None:
        pass

    def exitForEquation(self, tree: ast.ForEquation) -> None:
        pass

    def enterEquation(self, tree: ast.Equation) -> None:
        pass

    def exitEquation(self, tree: ast.Equation) -> None:
        pass

    def enterConnectClause(self, tree: ast.ConnectClause) -> None:
        pass

    def exitConnectClause(self, tree: ast.ConnectClause) -> None:
        pass

    def enterAssignmentStatement(self, tree: ast.AssignmentStatement) -> None:
        pass

    def exitAssignmentStatement(self, tree: ast.AssignmentStatement) -> None:
        pass

    def enterIfStatement(self, tree: ast.IfStatement) -> None:
        pass

    def exitIfStatement(self, tree: ast.IfStatement) -> None:
        pass

    def enterForStatement(self, tree: ast.ForStatement) -> None:
        pass

    def exitForStatement(self, tree: ast.ForStatement) -> None:
        pass

    def enterSymbol(self, tree: ast.Symbol) -> None:
        pass

    def exitSymbol(self, tree: ast.Symbol) -> None:
        pass

    def enterComponentClause(self, tree: ast.ComponentClause) -> None:
        pass

    def exitComponentClause(self, tree: ast.ComponentClause) -> None:
        pass

    def enterArray(self, tree: ast.Array) -> None:
        pass

    def exitArray(self, tree: ast.Array) -> None:
        pass

    def enterSlice(self, tree: ast.Slice) -> None:
        pass

    def exitSlice(self, tree: ast.Slice) -> None:
        pass

    def enterPrimary(self, tree: ast.Primary) -> None:
        pass

    def exitPrimary(self, tree: ast.Primary) -> None:
        pass

    def enterComponentRef(self, tree: ast.ComponentRef) -> None:
        pass

    def exitComponentRef(self, tree: ast.ComponentRef) -> None:
        pass


class TreeWalker(object):
    """
    Defines methods for tree walker. Inherit from this to make your own.
    """

    def walk(self, listener: TreeListener, tree: ast.Node) -> None:
        """
        Walks an AST tree recursively
        :param listener:
        :param tree:
        :return: None
        """
        name = tree.__class__.__name__
        if hasattr(listener, 'enterEvery'):
            getattr(listener, 'enterEvery')(tree)
        if hasattr(listener, 'enter' + name):
            getattr(listener, 'enter' + name)(tree)
        for child_name in tree.__dict__.keys():
            self.handle_walk(listener, tree.__dict__[child_name])
        if hasattr(listener, 'exitEvery'):
            getattr(listener, 'exitEvery')(tree)
        if hasattr(listener, 'exit' + name):
            getattr(listener, 'exit' + name)(tree)

    def handle_walk(self, listener: TreeListener, tree: Union[ast.Node, dict, list]) -> None:
        """
        Handles tree walking, has to account for dictionaries and lists
        :param listener: listener that reacts to walked events
        :param tree: the tree to walk
        :return: None
        """
        if isinstance(tree, ast.Node):
            self.walk(listener, tree)
        elif isinstance(tree, dict):
            for k in tree.keys():
                self.handle_walk(listener, tree[k])
        elif isinstance(tree, list):
            for i in range(len(tree)):
                self.handle_walk(listener, tree[i])
        else:
            pass


def modify_class(root: ast.Tree, class_or_sym: Union[ast.Class, ast.Symbol], modification):
    """
    Apply a modification to a class or symbol.
    :param root: root tree for looking up symbols
    :param class_or_sym: class or symbol to modify
    :param modification: modification to apply
    :return:
    """
    class_or_sym = copy.deepcopy(class_or_sym)
    for class_mod_argument in modification.arguments:
        argument = class_mod_argument.value
        if isinstance(argument, ast.ElementModification):
            if argument.component.name in ast.Symbol.ATTRIBUTES:
                setattr(class_or_sym, argument.component.name, argument.modifications[0])
            else:
                if isinstance(class_or_sym, ast.Class):
                    # First we check the local class definitions
                    s = class_or_sym.classes.get(argument.component.name, None)
                    if s is None:
                        s = root.find_symbol(class_or_sym, argument.component)
                    elif s.type == "__builtin":
                        # We need to do any modifications on the containing symbol
                        s = s.symbols['__value']
                else:
                    s = root.find_symbol(class_or_sym, argument.component)

                for modification in argument.modifications:
                    if isinstance(modification, ast.ClassModification):
                        s.__dict__.update(modify_class(root, s, modification).__dict__)
                    else:
                        s.value = modification
        elif isinstance(argument, ast.ComponentClause):
            for new_sym in argument.symbol_list:
                orig_sym = class_or_sym.symbols[new_sym.name]
                orig_sym.__dict__.update(new_sym.__dict__)
        elif isinstance(argument, ast.ShortClassDefinition):
            class_or_sym.classes[argument.name] = root.find_class(argument.component)
        else:
            raise Exception('Unsupported class modification argument {}'.format(argument))
    return class_or_sym


def flatten_symbol(s: ast.Symbol, instance_prefix: str) -> ast.Symbol:
    """
    Given a symbols and a prefix performs name mangling
    :param s: Symbol
    :param instance_prefix: Prefix for instance
    :return: flattened symbol
    """
    s_copy = copy.deepcopy(s)
    s_copy.name = instance_prefix + s.name
    if len(instance_prefix) > 0:
        # Strip 'input' and 'output' prefixes from nested symbols.
        strip_keywords = ['input', 'output']
        for strip_keyword in strip_keywords:
            try:
                s_copy.prefixes.remove(strip_keyword)
            except ValueError:
                pass
    return s_copy


class ComponentRefFlattener(TreeListener):
    """
    A listener that flattens references to components and performs name mangling,
    it also locates all symbols and determines which are states (
    one of the equations contains a derivative of the symbol)
    """

    def __init__(self, root: ast.Tree, container: ast.Class, instance_prefix: str):
        self.root = root
        self.container = container
        self.instance_prefix = instance_prefix
        self.depth = 0
        self.cutoff_depth = sys.maxsize
        super().__init__()

    def enterComponentRef(self, tree: ast.ComponentRef):
        self.depth += 1
        if self.depth > self.cutoff_depth:
            return

        # Compose flatted name
        new_name = self.instance_prefix + tree.name
        c = tree
        while len(c.child) > 0:
            c = c.child[0]
            new_name += CLASS_SEPARATOR + c.name

        # If the flattened name exists in the container, use it.
        # Otherwise, skip this reference.
        try:
            self.root.find_symbol(self.container, ast.ComponentRef(name=new_name))
        except KeyError:
            # The component was not found in the container.  We leave this
            # reference alone.
            self.cutoff_depth = self.depth
        else:
            tree.name = new_name
            c = tree
            while len(c.child) > 0:
                c = c.child[0]
                if len(c.indices) > 0:
                    tree.indices += c.indices
            tree.child = []

    def exitComponentRef(self, tree: ast.ComponentRef):
        self.depth -= 1
        if self.depth < self.cutoff_depth:
            self.cutoff_depth = sys.maxsize


def flatten_component_refs(
        root: ast.Tree, container: ast.Class,
        expression: ast.Union[ast.ConnectClause, ast.AssignmentStatement, ast.ForStatement, ast.Symbol],
        instance_prefix: str) -> ast.Union[ast.ConnectClause, ast.AssignmentStatement, ast.ForStatement, ast.Symbol]:
    """
    Flattens component refs in a tree
    :param root: root node
    :param container: class
    :param expression: original expression
    :param instance_prefix: prefix for instance
    :return: flattened expression
    """

    expression_copy = copy.deepcopy(expression)

    w = TreeWalker()
    w.walk(ComponentRefFlattener(root, container, instance_prefix), expression_copy)

    return expression_copy


def expand_connectors(root: ast.Tree, node: ast.Node) -> None:
    # keep track of which flow variables have been connected to, and which ones haven't
    disconnected_flow_variables = OrderedDict()
    for sym in node.symbols.values():
        if 'flow' in sym.prefixes:
            disconnected_flow_variables[sym.name] = sym

    # add flow equations
    # for all equations in original class
    flow_connections = OrderedDict()
    orig_equations = node.equations[:]
    node.equations = []
    for equation in orig_equations:
        if isinstance(equation, ast.ConnectClause):
            # expand connector
            sym_left = root.find_symbol(node, equation.left)
            sym_right = root.find_symbol(node, equation.right)

            try:
                class_left = getattr(sym_left, '__connector_type', None)
                if class_left is None:
                    # We may be connecting classes which are not connectors, such as Reals.
                    class_left = root.find_class(sym_left.type)
                # noinspection PyUnusedLocal
                class_right = getattr(sym_right, '__connector_type', None)
                if class_right is None:
                    # We may be connecting classes which are not connectors, such as Reals.
                    class_right = root.find_class(sym_right.type)
            except KeyError:
                primary_types = ['Real']
                # TODO
                if sym_left.type.name not in primary_types or sym_right.type.name not in primary_types:
                    logger.warning("Connector class {} or {} not defined.  "
                                   "Assuming it to be an elementary type.".format(sym_left.type, sym_right.type))
                connect_equation = ast.Equation(left=equation.left, right=equation.right)
                node.equations.append(connect_equation)
            else:
                # TODO: Add check about matching inputs and outputs

                flat_class_left = flatten_class(root, class_left, '')

                for connector_variable in flat_class_left.symbols.values():
                    left_name = equation.left.name + CLASS_SEPARATOR + connector_variable.name
                    right_name = equation.right.name + CLASS_SEPARATOR + connector_variable.name
                    left = ast.ComponentRef(name=left_name, indices=equation.left.indices)
                    right = ast.ComponentRef(name=right_name, indices=equation.right.indices)
                    if len(connector_variable.prefixes) == 0 or connector_variable.prefixes[0] in ['input', 'output']:
                        connect_equation = ast.Equation(left=left, right=right)
                        node.equations.append(connect_equation)
                    elif connector_variable.prefixes == ['flow']:
                        # TODO generic way to get a tuple representation of a component ref, including indices.
                        left_key = (left_name, tuple(i.value for i in left.indices), equation.__left_inner)
                        right_key = (right_name, tuple(i.value for i in right.indices), equation.__right_inner)

                        left_connected_variables = flow_connections.get(left_key, OrderedDict())
                        right_connected_variables = flow_connections.get(right_key, OrderedDict())

                        left_connected_variables.update(right_connected_variables)
                        connected_variables = left_connected_variables
                        connected_variables[left_key] = (left, equation.__left_inner)
                        connected_variables[right_key] = (right, equation.__right_inner)

                        for connected_variable in connected_variables:
                            flow_connections[connected_variable] = connected_variables

                        # TODO When dealing with an array of connectors, we can lose
                        # disconnected flow variables in this way.  We don't initialize
                        # all components of vectors to zero in 'flow_connections' as we
                        # do not always know the length of vectors a priori.
                        disconnected_flow_variables.pop(left_name, None)
                        disconnected_flow_variables.pop(right_name, None)
                    else:
                        raise Exception(
                            "Unsupported connector variable prefixes {}".format(connector_variable.prefixes))
        else:
            node.equations.append(equation)

    processed = []  # OrderedDict is not hashable, so we cannot use sets.
    for connected_variables in flow_connections.values():
        if connected_variables not in processed:
            operand_specs = list(connected_variables.values())
            if np.all([not op_spec[1] for op_spec in operand_specs]):
                # All outer variables. Don't include unnecessary minus expressions.
                operands = [op_spec[0] for op_spec in operand_specs]
            else:
                operands = [op_spec[0] if op_spec[1] else ast.Expression(operator='-', operands=[op_spec[0]]) for op_spec in operand_specs]
            expr = operands[-1]
            for op in reversed(operands[:-1]):
                expr = ast.Expression(operator='+', operands=[op, expr])
            connect_equation = ast.Equation(left=expr, right=ast.Primary(value=0))
            node.equations.append(connect_equation)
            processed.append(connected_variables)

    # disconnected flow variables default to 0
    for sym in disconnected_flow_variables.values():
        connect_equation = ast.Equation(left=sym, right=ast.Primary(value=0))
        node.equations.append(connect_equation)

    # strip connector symbols
    for i, sym in list(node.symbols.items()):
        if hasattr(sym, '__connector_type'):
            del node.symbols[i]


def add_state_value_equations(node: ast.Node) -> None:
    # we do this here, instead of in flatten_class, because symbol values
    # inside flattened classes may be modified later by modify_class().
    non_state_prefixes = set(['constant', 'parameter'])
    for sym in node.symbols.values():
        if not (isinstance(sym.value, ast.Primary) and sym.value.value == None):
            if len(non_state_prefixes & set(sym.prefixes)) == 0:
                node.equations.append(ast.Equation(left=sym, right=sym.value))
                sym.value = ast.Primary(value=None)


def add_variable_value_statements(node: ast.Node) -> None:
    # we do this here, instead of in flatten_class, because symbol values
    # inside flattened classes may be modified later by modify_class().
    for sym in node.symbols.values():
        if not (isinstance(sym.value, ast.Primary) and sym.value.value == None):
            node.statements.append(ast.AssignmentStatement(left=[sym], right=sym.value))
            sym.value = ast.Primary(value=None)


class StateAnnotator(TreeListener):
    """
    This finds all variables that are differentiated and annotates them with the state prefix
    """

    def __init__(self, root: ast.Tree, node: ast.Node):
        self.root = root
        self.node = node
        super().__init__()

    def exitExpression(self, tree: ast.Expression):
        """
        When exiting an expression, check if it is a derivative, if it is
        put state prefix on symbol
        """
        if tree.operator == 'der':
            s = self.root.find_symbol(self.node, tree.operands[0])
            if 'state' not in s.prefixes:
                s.prefixes.append('state')


def annotate_states(root: ast.Tree, node: ast.Node) -> None:
    """
    Finds all derivative expressions and annotates all differentiated
    symbols as states by adding state the prefix list
    :param root: collection for performing symbol lookup etc.
    :param node: node of tree to walk
    :return:
    """
    w = TreeWalker()
    w.walk(StateAnnotator(root, node), node)


class FunctionExpander(TreeListener):
    """
    Listener to extract functions
    """

    def __init__(self, root: ast.Tree, function_set: set):
        self.root = root
        self.function_set = function_set
        super().__init__()

    def exitExpression(self, tree: ast.Expression):
        if isinstance(tree.operator, ast.ComponentRef):
            try:
                function_class = self.root.find_class(tree.operator)

                full_name = str(function_class.full_reference())

                tree.operator = full_name
                self.function_set[full_name] = function_class
            except (KeyError, ast.ClassNotFoundError) as e:
                # Assume built-in function
                pass


# noinspection PyUnusedLocal
def fully_scope_function_calls(root: ast.Tree, expression: ast.Expression, function_set: OrderedDict) -> ast.Expression:
    """
    Turns the function references in this expression into fully scoped
    references (e.g. relative to absolute). The component references of all
    referenced functions are put into the functions set.

    :param root: collection for performing symbol lookup etc.
    :param container: class
    :param expression: original expression
    :param function_set: output of function component references
    :return:
    """
    expression_copy = copy.deepcopy(expression)

    w = TreeWalker()
    w.walk(FunctionExpander(root, function_set), expression_copy)
    return expression_copy


def build_instance_tree(orig_class: ast.Class, modification_environment=None, parent=None) -> ast.InstanceClass:
    extended_orig_class = ast.InstanceClass(
        name=orig_class.name,
        type=orig_class.type,
        parent=parent,
        root=parent.root if parent is not None else None
    )

    for extends in orig_class.extends:
        c = orig_class.find_class(extends.component, check_builtin_classes=True)

        if c.type == "__builtin":
            if len(orig_class.extends) > 1:
                raise Exception("When extending a built-in class (Real, Integer, ...), extending from other as well classes is not allowed.")
            extended_orig_class.type = c.type

        extended_orig_class.classes.update(c.classes)
        extended_orig_class.symbols.update(c.symbols)
        extended_orig_class.equations += c.equations
        extended_orig_class.initial_equations += c.initial_equations
        extended_orig_class.statements += c.statements
        extended_orig_class.initial_statements += c.initial_statements
        extended_orig_class.functions.update(c.functions)

        extended_orig_class.modification_environment.arguments.extend(extends.class_modification.arguments)

        # set visibility
        for sym in extended_orig_class.symbols.values():
            if sym.visibility > extends.visibility:
                sym.visibility = extends.visibility

    extended_orig_class.classes.update(orig_class.classes)
    extended_orig_class.symbols.update(orig_class.symbols)
    extended_orig_class.equations += orig_class.equations
    extended_orig_class.initial_equations += orig_class.initial_equations
    extended_orig_class.statements += orig_class.statements
    extended_orig_class.initial_statements += orig_class.initial_statements
    extended_orig_class.functions.update(orig_class.functions)

    if modification_environment is not None:
        extended_orig_class.modification_environment.arguments.extend(modification_environment.arguments)

    # Redeclarations take effect
    for class_mod_argument in extended_orig_class.modification_environment.arguments:
        if not class_mod_argument.redeclare:
            continue
        argument = class_mod_argument.value
        if isinstance(argument, ast.ShortClassDefinition):
            extended_orig_class.classes[argument.name] = extended_orig_class.find_class(argument.component)
        elif isinstance(argument, ast.ComponentClause):
            # Redeclaration of symbols
            for s in argument.symbol_list:
                extended_orig_class.symbols[s.name].type = s.type
        else:
            raise Exception("Unknown redeclaration type")

    extended_orig_class.modification_environment.arguments = [x for x in extended_orig_class.modification_environment.arguments if not x.redeclare]

    # Assert: Only ast.ElementModification type modifications left in the
    # class's modification environment. No more ComponentClause or
    # ShortClassDefinitions (which are both redeclares). There are still
    # possible redeclares in symbols though.

    # Merge/pass along modifications for classes
    for class_name, c in extended_orig_class.classes.items():
        sub_class_modification = ast.ClassModification()

        sub_class_arguments = [x for x in extended_orig_class.modification_environment.arguments
            if isinstance(x.value, ast.ElementModification) and x.value.component.name == class_name]

        # Remove from current class's modification environment
        extended_orig_class.modification_environment.arguments = [x for x in extended_orig_class.modification_environment.arguments if x not in sub_class_arguments]

        for arg in sub_class_arguments:
            if arg.scope is None:
                arg.scope = extended_orig_class
            sub_class_modification.arguments.append(arg)

        extended_orig_class.classes[class_name] = build_instance_tree(c, sub_class_modification, extended_orig_class)

    for sym_name, sym in extended_orig_class.symbols.items():
        class_name = sym.type

        if isinstance(sym.type, ast.InstanceClass):
            continue

        try:
            c = extended_orig_class.find_class(sym.type)
        except ast.FoundElementaryClassError:
            pass  # Do nothing
        else:
            if sym.class_modification:
                for arg in sym.class_modification.arguments:
                    if arg.scope is None:
                        arg.scope = extended_orig_class

            sym.type = build_instance_tree(c, sym.class_modification, c.parent)
            sym.class_modification = None

    return extended_orig_class


def flatten_instance_tree(class_: ast.InstanceClass, instance_name='', modification=ast.ClassModification()) -> ast.Class:
    # Recursive symbol flattening

    flat_class = ast.Class(
        name=class_.name,
        type=class_.type,
    )

    # append period to non empty instance_name
    if instance_name != '':
        instance_prefix = instance_name + CLASS_SEPARATOR
    else:
        instance_prefix = instance_name

    # for all symbols in the original class
    for sym_name, sym in class_.symbols.items():
        flat_sym = flatten_symbol(sym, instance_prefix)
        try:
            c = class_.find_class(sym.type)

            if c.type == "__builtin":
                flat_class.symbols[flat_sym.name] = flat_sym
                for att in flat_sym.ATTRIBUTES + ["type"]:
                    setattr(flat_class.symbols[flat_sym.name], att, getattr(c.symbols['__value'], att))

                continue

        except ast.FoundElementaryClassError:
            # append original symbol to flat class
            flat_class.symbols[flat_sym.name] = flat_sym
        else:
            # recursively call flatten on the contained class
            flat_sub_class = flatten_instance_tree(c, flat_sym.name, flat_sym.class_modification)

            # carry class dimensions over to symbols
            for flat_class_symbol in flat_sub_class.symbols.values():
                if len(flat_class_symbol.dimensions) == 1 \
                        and isinstance(flat_class_symbol.dimensions[0], ast.Primary) \
                        and flat_class_symbol.dimensions[0].value == 1:
                    flat_class_symbol.dimensions = flat_sym.dimensions
                elif len(flat_sym.dimensions) == 1 and isinstance(flat_sym.dimensions[0], ast.Primary) \
                        and flat_sym.dimensions[0].value == 1:
                    flat_class_symbol.dimensions = flat_class_symbol.dimensions
                else:
                    flat_class_symbol.dimensions = flat_sym.dimensions + flat_class_symbol.dimensions

            # add sub_class members symbols and equations
            flat_class.classes.update(flat_sub_class.classes)
            flat_class.symbols.update(flat_sub_class.symbols)
            flat_class.equations += flat_sub_class.equations
            flat_class.initial_equations += flat_sub_class.initial_equations
            flat_class.statements += flat_sub_class.statements
            flat_class.initial_statements += flat_sub_class.initial_statements
            flat_class.functions.update(flat_sub_class.functions)

            # we keep connectors in the class hierarchy, as we may refer to them further
            # up using connect() clauses
            if c.type == 'connector':
                flat_sym.__connector_type = c
                flat_class.symbols[flat_sym.name] = flat_sym

    return flat_class

def flatten(orig_class: ast.Class) -> ast.Class:
    """
    This function takes a Tree and flattens it so that all subclasses instances
    are replaced by the their equations and symbols with name mangling
    of the instance name passed.
    :param root: The Tree to flatten
    :param class_name: The class that we want to create a flat model for
    :return: flat_class, a Class containing the flattened class
    """

    instance_tree = build_instance_tree(orig_class)


    # Optimization: Merge modifications of elementary types (type =
    # __builtin). This is possible because we know they are the lowest level
    # we go.

    flat_class = flatten_instance_tree(instance_tree)

    return flat_class
