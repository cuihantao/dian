import sympy


def non_commutative_sympify(expr_string):
    parsed_expr = sympy.parsing.sympy_parser.parse_expr(
        expr_string,
        evaluate=False
    )

    new_locals = {sym.name: sympy.Symbol(sym.name, commutative=False)
                  for sym in parsed_expr.atoms(sympy.Symbol)}

    return sympy.sympify(expr_string, locals=new_locals)
