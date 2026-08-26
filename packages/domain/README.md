# Domain policy

`@everything-agentic/domain` owns the enterprise workflow state machine and
fail-closed authorization rules. It has no framework, database, network, or UI
dependency. Production adapters call this policy rather than reimplementing
transitions at the edge. Included fixtures are synthetic and local-only.
