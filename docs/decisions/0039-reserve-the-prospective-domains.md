# ADR 0039: Reserve the prospective domains

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: reserves all forty-nine accepted new digest-domain names in the
  profile core as prospective registrations, reissuing the core schema to
  0.2.0; registers no declaring constant, admits no member, and accepts no
  Gate A row

## Context

The accepted D5 table names roughly fifty digest subjects with no home among
the twenty-one frozen domains. The wave's dictated sequence puts their
registration first, because it edits the profile core and re-freezes its
bytes; every later tranche pins against the result.

Two constraints shaped the design. The core schema pinned the registry at
exactly twenty-one entries, and the profile suite requires the registry to
equal, exactly, the domain constants declared in current schema bytes. Both
are correct disciplines: the registry must never claim a constant that does
not exist. But forty-nine of the accepted subjects have no declaring constant
yet — twenty-three do not even have schemas yet — so putting them in the
registry would have been a lie the suite rightly refuses.

## Decision

A separate `prospective_domain_registry`: forty-nine name reservations, each
carrying its subject class, its intended declaring schema (the current `$id`
where the schema exists, the prospective 0.1.0 identity where the wave will
create it), the acceptance record as its reservation source, and the explicit
status `prospective_name_reserved_no_declaring_constant`. The declared
registry stays at twenty-one, still equal to the constants that exist. The
profile suite now verifies the reservations too: sorted, unique, disjoint from
every declared constant, exact status and source. The eighteen deferred
needs-operator rows — the frontier and commitment families awaiting their one
construction decision — reserve nothing, by design.

The core schema is reissued to 0.2.0 at the same path under the ledger's
precedent, and the succession propagated through every consumer that pinned
the 0.1.0 identity or the core's exact bytes: three suite scripts that
hardcoded the identity, eight candidate and evidence schemas pinning digests
as constants, eight architecture records embedding profile references, the
successor-cohort render digests, the reissue ledger, the module dependency
manifest, and the prerequisite validator. The reconvergence was iterated to a
fixed point — evidence rebinds and schema-constant repoints alternating until
a full pass changed nothing — and the complete validator passes at the end.

## Non-decisions

This decision does not register a declaring constant for any reserved name;
that happens schema by schema in the reissue wave, at which point each
reservation graduates into the declared registry and the suite's equality
check enforces the graduation. It does not decide the frontier or commitment
constructions, does not admit a member, and does not accept Gate A.

## Consequences

Every accepted domain name is now retained, collision-checked, and bound to
the acceptance record. The wave's next tranche — the schema reissues of D2
through D8 — can pin scoped-digest definitions against reserved names instead
of inventing them ad hoc, which is the difference between a registry and a
pile.
