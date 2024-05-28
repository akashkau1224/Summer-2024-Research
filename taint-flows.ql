/**
 * @name Empty block
 * @kind problem
 * @problem.severity warning
 * @id java/example/empty-block
 */

import java
import semmle.code.java.dataflow.DataFlow
import semmle.code.java.dataflow.FlowSources

module MyFlowConfiguration implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    source.asExpr() instanceof MethodCall and
    exists(MethodCall ma |
      ma = source.asExpr() and
      (
        ma.getMethod().hasName("getParameter") and
        ma.getMethod()
            .getDeclaringType()
            .hasQualifiedName("javax.servlet.http", "HttpServletRequest")
      )
    )
  }

  predicate isSink(DataFlow::Node sink) {
    sink.asExpr() instanceof MethodCall and
    exists(MethodCall mi |
      mi = sink.asExpr() and
      mi.getMethod().hasName("exec") and
      mi.getMethod().getDeclaringType().hasQualifiedName("java.lang", "Runtime")
    )
  }
}

module MyTaintFlow = TaintTracking::Global<MyFlowConfiguration>;

from DataFlow::Node src, DataFlow::Node sink
where MyTaintFlow::flow(src, sink)
select src, "The HTTP Serverlet Request", sink, "The commandline execution"
