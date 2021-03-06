from collections import OrderedDict

""" SPI - Simple Pascal Interpreter """

###############################################################################
#                                                                             #
#  LEXER                                                                      #
#                                                                             #
###############################################################################

# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
PROCEDURE, INTEGER, REAL, INTEGER_CONST, REAL_CONST, PLUS, MINUS, MULTIPLY, INTEGER_DIV, FLOAT_DIV, LPAREN, RPAREN, EOF, BEGIN, END, DOT, ASSIGN, SEMI, ID, PROGRAM, VAR, COLON, COMMA = (
    'PROCEDURE',
    'INTEGER',
    'REAL',
    'INTEGER_CONST',
    'REAL_CONST',
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'INTEGER_DIV',
    'FLOAT_DIV',
    'LPAREN',
    'RPAREN',
    'EOF',
    'BEGIN',
    'END',
    'DOT',
    'ASSIGN',
    'SEMI',
    'ID',
    'PROGRAM',
    'VAR',
    'COLON',
    'COMMA'
)

class Token(object):
    def __init__(self, type, value):
        # token type: INTEGER, PLUS, or EOF
        self.type = type
        # token value: 0, 1, 2. 3, 4, 5, 6, 7, 8, 9, '+', or None
        self.value = value

    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS '+')
            Token(MINUS '-')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'DIV': Token('INTEGER_DIV', 'DIV'),
    'END': Token('END', 'END'),
    'PROCEDURE': Token('PROCEDURE', 'PROCEDURE'),
    'PROGRAM': Token('PROGRAM', 'PROGRAM'),
    'INTEGER': Token('INTEGER', 'INTEGER'),
    'REAL': Token('REAL', 'REAL'),
    'VAR': Token('VAR', 'VAR'),
}

class Lexer(object):

    def __init__(self, text):
        # client string input, e.g. "3+5"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos +=1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) -1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char != '}':
            self.advance()
        self.advance()  # the closing curly brace

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            token = Token('REAL_CONST', float(result))
        else:
            token = Token('INTEGER_CONST', int(result))
        return token

    def _id(self):
        """Handle identifiers/variables and reserved keywords"""
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:
            if self.current_char.isalpha():
                return self._id()
            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')
            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')
            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return self.number()
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')
            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')
            if self.current_char == '*':
                self.advance()
                return Token(MULTIPLY, '*')
            if self.current_char == '/':
                self.advance()
                return Token(FLOAT_DIV, '/')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            if self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue
            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')
            if self.current_char == ":":
                self.advance()
                return Token(COLON, ':')
            if self.current_char == '/':
                self.advance()
                return Token(FLOAT_DIV, '/')
            self.error()
        return Token(EOF, None)

###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass

class Program(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block

class ProcedureDeclaration(AST):
    def __init__(self, name, block):
        self.name = name
        self.block = block

class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement

class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Compound(AST):
    """Represents a BEGIN ... END block"""
    def __init__(self):
        self.children = []

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class NoOp(AST):
    pass

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set initial current token to first token in input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def block(self):
        """block : declarations compound_statement"""
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)
        return node

    def declarations(self):
        """
            declarations: VAR (variable_declaration SEMI)+
            | (PROCEDURE ID SEMI BLOCK SEMI)*
            | empty"""
        declarations = []
        if self.current_token.type == VAR:
            self.eat(VAR)
            while self.current_token.type == ID:
                var_decl = self.variable_declaration()
                declarations.extend(var_decl)
                self.eat(SEMI)
        if self.current_token.type == PROCEDURE:
            self.eat(PROCEDURE)
            name = self.current_token.value
            self.eat(ID)
            self.eat(SEMI)
            block_node = self.block()
            procedure_declaration = ProcedureDeclaration(name, block_node)
            declarations.append(procedure_declaration)
            self.eat(SEMI)
        return declarations

    def variable_declaration(self):
        """variable_declaration : ID (COMMA ID)* COLON type_spec"""
        variable_nodes = []
        variable_nodes.append(Var(self.current_token)) # first variable name
        self.eat(ID)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            variable_nodes.append(Var(self.current_token))
            self.eat(ID)
        self.eat(COLON)

        type_node = self.type_spec()
        var_declarations = [
            VarDecl(var_node, type_node) for var_node in variable_nodes
        ]
        return var_declarations

    def type_spec(self):
        """ type_spec : INTEGER | REAL """
        token = self.current_token
        if self.current_token.type == INTEGER:
            self.eat(INTEGER)
            return Type(token)
        elif self.current_token.type == REAL:
            self.eat(REAL)
            return Type(token)
        else:
            self.error()

    def factor(self):
        """factor: PLUS factor
            | MINUS factor
            | INTEGER_CONST
            | REAL_CONST
            | LPAREN expr RPAREN
            | variable
        """
        token = self.current_token
        if token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(token)
        if token.type == REAL_CONST:
            self.eat(REAL_CONST)
            return Num(token)
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        if token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        if token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def term(self):
        """term : factor ((MULTIPLY | INTEGER_DIV | FLOAT_DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MULTIPLY, INTEGER_DIV, FLOAT_DIV):
            token = self.current_token
            if token.type == MULTIPLY:
                self.eat(MULTIPLY)
            elif token.type == INTEGER_DIV:
                self.eat(INTEGER_DIV)
            elif token.type == FLOAT_DIV:
                self.eat(FLOAT_DIV)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def expr(self):
        """
        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MULTIPLY | DIVIDE) factor)*
        factor : (PLUS | MINUS)factor | INTEGER | LPAREN expr RPAREN
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()
        return node

    def program(self):
        """program : PROGRAM variable SEMI block DOT"""
        self.eat(PROGRAM)
        var_node = self.variable()
        program_name = var_node.value
        self.eat(SEMI)
        block_node = self.block()
        self.eat(DOT)
        program_node = Program(program_name, block_node)
        return program_node

    def compound_statement(self):
        """compound_statement : BEGIN statement_list END"""
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self):
        """
        statement_list : statement | statement SEMI statement_list
        """
        node = self.statement()
        results = [node]
        while self.current_token.type == SEMI:
            self.eat(SEMI)
            results.append(self.statement())
        if self.current_token.type == ID:
            self.error()

        return results

    def statement(self):
        """
        statement : compound_statement | assignment_statement | empty
        """
        if self.current_token.type == BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        """
        assignment_statement : variable ASSIGN expr
        """
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def variable(self):
        """
        variable : ID
        """
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        """An empty production"""
        return NoOp()


###############################################################################
#                                                                             #
# AST visitors (walkers)                                                      #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


###############################################################################
#                                                                             #
#  SYMBOLS and SYMBOL TABLE and SYMBOL TABLE BUILDER                                                 #
#                                                                             #
###############################################################################

class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class BuiltInSymbol(Symbol):
    def __init__(self, name):
        super(BuiltInSymbol, self).__init__(name)

    def __str__(self):
        return self.name

    __repr__ = __str__

class VariableSymbol(Symbol):
    def __init__(self, name, type):
        super(VariableSymbol, self).__init__(name, type)

    def __str__(self):
        return '<{name}: {type}>'.format(name=self.name, type=self.type)

    __repr__ = __str__

class SymbolTable():
    def __init__(self):
        self._symbols = OrderedDict()
        self._init_builtins()

    def _init_builtins(self):
        self.define(BuiltInSymbol('REAL'))
        self.define(BuiltInSymbol('INTEGER'))

    def __str__(self):
        symbol_table = 'Symbols: {symbols}'.format(symbols=[
            value for value in self._symbols.values()
        ])
        return symbol_table

    __repr__ = __str__

    def define(self, symbol):
        print 'Define: {symbol}'.format(symbol=symbol)
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        print 'Look up: {}'.format(name)
        return self._symbols.get(name)

class SymbolTableBuilder(NodeVisitor):
    GLOBAL_SCOPE = {}

    def __init__(self):
        self.table = SymbolTable()

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_ProcedureDeclaration(self, node):
        pass

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Num(self, node):
        pass

    def visit_UnaryOp(self, node):
        self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_VarDecl(self, node):
        type_name = node.type_node.value
        type_symbol = self.table.lookup(type_name)
        # import pdb; pdb.set_trace()
        var_name = node.var_node.value
        variable_symbol = VariableSymbol(var_name, type_symbol)
        self.table.define(variable_symbol)

###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class Interpreter(NodeVisitor):

    def __init__(self, tree):
        self.tree = tree
        self.GLOBAL_SCOPE = OrderedDict()

    def visit_UnaryOp(self, node):
        if node.op.type == PLUS:
            return +self.visit(node.expr)
        elif node.op.type == MINUS:
            return -self.visit(node.expr)

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MULTIPLY:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == FLOAT_DIV:
            return self.visit(node.left) / self.visit(node.right)
        elif node.op.type == INTEGER_DIV:
            return self.visit(node.left) // self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_ProcedureDeclaration(self, node):
        pass

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        pass

    def visit_Type(self, node):
        pass

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def interpret(self):
        tree = self.tree
        if tree is None:
            return ''
        return self.visit(tree)







def main():
    while True:
        try:
            text = raw_input('spi> ')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print result


if __name__ == '__main__':
    main()
