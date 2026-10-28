"""Read-only Python AST triage. Never imports or executes the target."""
import argparse
import ast
from common import emit, read_text, run


def inspect(source, filename="<input>"):
    tree = ast.parse(source, filename=filename)
    findings = []

    def flag(code, node, message, certainty="structural"):
        findings.append({"code": code, "line": node.lineno, "column": node.col_offset + 1,
                         "message": message, "certainty": certainty})

    # Only directly terminal statements: no speculative whole-program flow claims.
    for parent in ast.walk(tree):
        for _, value in ast.iter_fields(parent):
            if isinstance(value, list) and value and all(isinstance(x, ast.stmt) for x in value):
                terminal = False
                for stmt in value:
                    if terminal:
                        flag("PY_UNREACHABLE", stmt, "Statement follows a direct return/raise/break/continue in the same block")
                    terminal = terminal or isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue))
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and isinstance(node.right, ast.Constant) and type(node.right.value) in (int, float, complex) and node.right.value == 0:
            flag("PY_ZERO_DIVISION", node, "Literal zero divisor; confirm this is not an intentional exception test")
        if isinstance(node, ast.Subscript):
            index = node.slice
            number = index.value if isinstance(index, ast.Constant) and type(index.value) is int else None
            if isinstance(index, ast.UnaryOp) and isinstance(index.op, ast.USub) and isinstance(index.operand, ast.Constant) and type(index.operand.value) is int:
                number = -index.operand.value
            if number is not None and isinstance(node.value, (ast.List, ast.Tuple)) and not any(isinstance(x, ast.Starred) for x in node.value.elts):
                size = len(node.value.elts)
                if not -size <= number < size:
                    flag("PY_LITERAL_INDEX", node, "Literal list/tuple index is out of bounds")
            elif number in (0, -1) and isinstance(node.value, ast.Name):
                flag("PY_BOUNDARY_REVIEW", node, "Verify empty-input behavior or a documented nonempty contract for indexing", "review_candidate")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_nodes = [child for statement in node.body for child in ast.walk(statement)]
            excluded = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda, ast.ListComp,
                        ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.Global, ast.Nonlocal)
            if any(isinstance(x, excluded) for x in body_nodes):
                continue
            if any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id in {"locals", "vars", "eval", "exec"} for x in body_nodes):
                continue
            reads = {x.id for x in body_nodes if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load)}
            reads.update(x.target.id for x in body_nodes if isinstance(x, ast.AugAssign) and isinstance(x.target, ast.Name))
            writes = {}
            for child in body_nodes:
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                    writes.setdefault(child.id, child)
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    for alias in child.names:
                        name = alias.asname or (alias.name.split(".")[0] if isinstance(child, ast.Import) else alias.name)
                        if name != "*":
                            writes.setdefault(name, child)
            for name, location in writes.items():
                if name not in reads and not name.startswith("_"):
                    flag("PY_UNUSED_LOCAL", location, "Local binding is never read in this simple function: " + name, "review_candidate")
    return sorted(findings, key=lambda f: (f["line"], f["column"], f["code"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file")
    args = parser.parse_args()
    if not args.file.lower().endswith(".py"):
        raise ValueError("Only .py source is supported; use the language's own tools for other files")
    return emit("check_python", inspect(read_text(args.file), args.file),
                "Partial Python AST triage; no type, security, concurrency or whole-program proof. Columns are UTF-8 byte offsets (1-based).", file=args.file)


if __name__ == "__main__":
    run(main)
