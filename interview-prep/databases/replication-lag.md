# Replication Lag

### 🔴 Q. A user writes data, refreshes, and cannot see it. How can replication cause this?

**Answer.** If writes go to a primary but the refresh reads from an asynchronous replica, that replica may not have replayed the write yet. This violates read-your-writes consistency even though replication is healthy.

Remedies include routing that user's reads to the primary briefly, carrying the write's log position and waiting for a caught-up replica, or using synchronous replication when visibility is worth higher latency and lower availability. A UI can also acknowledge pending processing.

Monitoring only average lag is insufficient: alert on high percentiles and log positions behind. A replica can be seconds behind during a burst and look normal again by the time a coarse dashboard samples it.
