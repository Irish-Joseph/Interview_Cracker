# False Sharing

### 🔴 Q. What is false sharing, and why can independent counters slow each other down?

**Answer.** False sharing occurs when threads update different variables that occupy the same CPU cache line. The values are logically independent, but cache coherence moves ownership of the whole line between cores.

The symptom is high coherence traffic and poor scaling without a lock-contention hotspot. Confirm it with profiling or hardware counters. Fixes include per-thread aggregation, padding or aligning hot fields, and layouts that separate frequently written values.

Padding everything wastes cache and may make performance worse. Cache-line size also varies, so isolate only measured hot fields and prefer platform-supported alignment constructs.
