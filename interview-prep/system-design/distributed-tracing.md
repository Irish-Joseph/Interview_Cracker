# Distributed Tracing

### 🟡 Q. Logs already exist. Why add distributed tracing, and what should a trace contain?

**Answer.** Logs describe events inside one component; a distributed trace connects the work caused by one request across services. It shows the critical path, where latency accumulated, and which downstream call failed.

A trace has a shared **trace ID** and a tree of **spans**. Each span records its parent, operation, start and duration, status, and carefully chosen attributes. Propagate context across HTTP, queues, and background jobs or the trace breaks at that boundary.

Trace data is expensive, so sample it. Head sampling decides at request entry and is cheap; tail sampling can retain rare errors or slow traces after seeing the outcome. Never attach secrets or unbounded attributes: they create privacy risk and cardinality explosions.
