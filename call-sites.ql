/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id java/example/empty-block
 */

import java

// from Call c, IfStmt i
// where i.toString().indexOf("if") = -1 and i.toString().indexOf(c.getCallee().getName()) != -1
// select c, "call sites in an if/else"

from Call c, MethodCall m, IfStmt i
where m.getEnclosingStmt() = i and c.getCallee() = m.getMethod()
select c, "call sites in an if/else"