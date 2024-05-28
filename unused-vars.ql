/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id java/example/empty-block
 */

import java

from Variable v
where v.getNumberOfLinesOfCode() <= 1
select v, "This is an unused variable"
