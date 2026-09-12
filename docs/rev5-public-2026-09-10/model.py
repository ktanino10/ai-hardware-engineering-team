"""Deterministic HOST-ONLY ordering model. NEVER an actual operation permit.

A1 spec.json: acceptance C1..C5, evidence_obligations, event_protocol.
B authority-map.json: later_host_only_interface_conditions and B-* routes.
No SDK import, device access, clock, file I/O, motor/control or electrical math.
All positive evidence is explicitly SYNTHETIC. Python object/attribute access
is not a privilege boundary; the journal is an assumed external model oracle.
"""
from dataclasses import dataclass
from enum import Enum


# Current correction's frozen INPUT revision, not a self-hash or review verdict.
SOURCE = "afd531ad4b3dfb9611cba0d78b2dfdba64e42605"
CONFIG = "0d524373af5f0a87e792d8a46a55caa4041987f2"
A1_SHA = "50a7d689125a0355076af1f62ce64ff69baab8bf23851629d9f7f961647881c9"
B_SHA = "213d166f0f3872f2afd44fbc8ba2943d0494fda1f7b4707baa58d95c9361fa52"
REVISION = (SOURCE, CONFIG, A1_SHA, B_SHA)
AXES = frozenset(("X", "Y", "Z"))
# A1 endpoint_binding.lines / B hardware_endpoint_boundary. NOT new pin choices.
ENDPOINTS = (
    ("X-SCL", "U201.12", 8, "DRV_X_SCL", "U301.10", "DRV_X_SCL_D"),
    ("X-SDA", "U201.17", 9, "DRV_X_SDA", "U301.11", "DRV_X_SDA_D"),
    ("Y-SCL", "U201.31", 38, "DRV_Y_SCL", "U302.10", "DRV_Y_SCL_D"),
    ("Y-SDA", "U201.32", 39, "DRV_Y_SDA", "U302.11", "DRV_Y_SDA_D"),
    ("Z-SCL", "U201.33", 40, "DRV_Z_SCL", "U303.10", "DRV_Z_SCL_D"),
    ("Z-SDA", "U201.34", 41, "DRV_Z_SDA", "U303.11", "DRV_Z_SDA_D"),
)
ACTORS = frozenset((
    "privileged", "other_core", "ISR_callback", "DMA", "ROM_boot",
    "debug_probe", "manual_EN", "power_access", "direct_noos",
))
ASSUMPTIONS = frozenset((
    "normal_components", "specified_power_return_load_envelope",
    "hypothetical_limits_not_actual_thresholds", "complete_route_inventory",
    "precompletion_transition_qualified", "independent_gate_and_hold",
))
EVIDENCE_CHECKS = frozenset((
    "E_TOPOLOGY", "E_CONTINUOUS", "E_TRANSIENT", "E_COMPLETION_TIME",
    "E_VALIDITY", "C4_MAINTAINED", "PRECOMPLETION_TRANSITION",
))
SERVICE_CHECKS = EVIDENCE_CHECKS | frozenset((
    "cause_disposed", "pin_rail_hold_state", "transaction_disposition",
    "fresh_service_qualified", "sequential_rejoin_qualified",
    "post_event_mapping_confirmed",
))
Mapping = tuple[tuple[str, str], ...]


class State(str, Enum):
    RECOVERY = "RECOVERY_ISOLATED"
    SERVICE = "SERVICE_CONDITIONAL"
    CAPTURED = "REQUEST_CAPTURE"
    WITHDRAW = "WITHDRAW"
    EVIDENCE = "EVIDENCE_PENDING"
    PERMITTED = "EVENT_PERMITTED"
    ACTIVE = "EVENT_ACTIVE"
    REARM = "REARM_READY"
    LOST = "REJECTED_OR_PROOF_LOST"


class Denied(ValueError):
    """A refused model transition, not proof that hardware was stopped."""


@dataclass(frozen=True)
class Route:
    line: str
    direction: str
    # Alternative serial blockers on THIS route; each route needs one witness.
    blockers: frozenset[str]


@dataclass(frozen=True)
class Topology:
    identity: str
    routes: tuple[Route, ...]
    resource_axes: tuple[tuple[str, frozenset[str]], ...] = ()
    endpoints: tuple = ENDPOINTS
    inventory_complete_assumption: bool = False


@dataclass(frozen=True)
class ActorClaim:
    actor: str
    disposition: str  # cooperative or excluded, only under a synthetic fixture
    basis: str


@dataclass(frozen=True)
class Ownership:
    generation: int
    issuers: frozenset[str]
    claims: tuple[ActorClaim, ...] = ()


@dataclass(frozen=True)
class Fixture:
    label: str = "UNKNOWN"
    assumptions: frozenset[str] = frozenset()
    envelope: str = "UNKNOWN"
    limits: str = "UNKNOWN"


class SyntheticJournal:
    """Explicit external continuity assumption, not persistent storage/security.

    Reuse this same object across modeled restarts. Losing/forking/replacing it
    cannot be detected against reality by this model; no real replay guarantee.
    """

    def __init__(self, continuity_basis: str = "UNKNOWN"):
        self.continuity_basis = continuity_basis
        self.epochs: set[str] = set()
        self.events: set[tuple[str, str]] = set()
        self.service_ids: set[str] = set()

    def reserve_epoch(self, epoch: str) -> bool:
        if not self.continuity_basis.startswith("SYNTHETIC:") or not epoch:
            return False
        if epoch in self.epochs:
            return False
        self.epochs.add(epoch)
        return True


@dataclass(frozen=True)
class Request:
    event_id: str
    issuer: str
    epoch: str
    kind: str
    revision: tuple
    topology: str
    owner_generation: int
    old_mapping: Mapping
    new_mapping: Mapping
    axes: frozenset[str]
    resources: frozenset[str]
    endpoints: tuple
    # Upper bound through recovery AND rejoin, in synthetic steps; None asks
    # for indefinite maintained evidence, not an unknown duration treated zero.
    hold_until: int | None
    contact_edge: int | None = None


@dataclass(frozen=True)
class EngineReport:
    request: Request
    owner_generation: int
    resources: frozenset[str]
    freeze_generation: int
    accounting_generation: int
    origin: str = "UNKNOWN"
    engines_idle: bool = False
    callbacks_fenced: bool = False


@dataclass(frozen=True)
class Evidence:
    request: Request
    origin: str
    fixture: str
    envelope: str
    limits: str
    cut_set: frozenset[str]
    checks: frozenset[str]
    available_at: int
    completion_latest: int
    valid_until: int | None
    indefinite_hold: bool = False


@dataclass(frozen=True)
class Permit:
    """Only a one-use synthetic transition capability. No physical permission."""

    request: Request
    evidence: Evidence
    serial: int
    actual_operation_permission: bool = False


@dataclass
class Transaction:
    resource: str
    phase: str = "QUEUED"
    timed_out: bool = False
    effect: bool = False
    disposition: str | None = None


@dataclass(frozen=True)
class RecoveryContext:
    """Model-owned freshness binding for an explicitly synthetic qualification.

    Generation is local ordering, independent of logical time/caller generations.
    The opaque instance scope prevents cross-model reuse, NOT real authentication
    or persistent storage. Cause disposition must qualify this whole snapshot.
    """

    instance_scope: object
    generation: int
    cause: str
    losses: tuple[str, ...]
    accounting_generation: int
    transactions: tuple
    ownership: Ownership
    topology: Topology
    fixture: Fixture
    mapping: Mapping
    mapping_known: bool
    freeze_generation: int
    epoch: str
    continuity_assumed: bool
    journal_scope: SyntheticJournal | None
    journal_continuity: str | None
    request: Request | None
    event_outcome: str
    event_running: bool
    effects: tuple[str, ...]
    contact_state: tuple


@dataclass(frozen=True)
class ServiceProof:
    request_id: str
    old_epoch: str
    new_epoch: str
    revision: tuple
    topology: str
    mapping: Mapping
    owner_generation: int
    fixture: str
    envelope: str
    limits: str
    checks: frozenset[str]
    cut_set: frozenset[str]
    event_binding: Request | None
    event_outcome: str
    available_at: int
    valid_until: int
    # Covers present held isolation to rejoin; does not erase an earlier gap.
    # None keeps old constructor calls representable, but NEVER authorizable.
    recovery: RecoveryContext | None = None


class Model:
    """Cooperating finite-context machine; every actual acceptance stays false."""

    actual_operation_permission = False
    actual_bus_permission = False
    physical_disconnection_established = False
    normal_board_conformance = "UNKNOWN"
    actual_electrical_limits = "UNKNOWN"
    motor_inhibit = "UNKNOWN"
    command_permission = False

    def __init__(self, topology: Topology, mapping: Mapping, owner: Ownership,
                 epoch: str, fixture: Fixture = Fixture(),
                 journal: SyntheticJournal | None = None):
        self._mapping_dict(mapping)
        self.topology, self.mapping, self.owner = topology, mapping, owner
        self.mapping_known = True  # source of this initial state is a fixture
        self.fixture, self.journal, self.epoch = fixture, journal, epoch
        self.fresh = journal is not None and journal.reserve_epoch(epoch)
        self.state, self.now = State.RECOVERY, 0
        self.bus_grant = False  # synthetic service only
        self.off_demand = True  # demand != achieved blocking
        self.request: Request | None = None
        self.evidence: Evidence | None = None
        self.permit: Permit | None = None
        self.service_proof: ServiceProof | None = None
        self.transactions: dict[str, Transaction] = {}
        self.event_running = False
        self.event_outcome = "BOOT_UNKNOWN"
        self.effects: list[str] = []
        self.losses: list[str] = []
        self.trace: list[dict] = []
        self._serial = 0
        self.freeze_generation = 0
        self.accounting_generation = 0
        self._contact_level: bool | None = None
        self._contact_released = False
        self._edge = 0
        self._used_edge = 0
        self._recovery_scope = object()
        self._recovery_generation = 0
        self._recovery_cause = "BOOT_UNQUALIFIED"

    def recovery_context(self) -> RecoveryContext:
        """Read-only snapshot; obtaining it does NOT dispose a cause or qualify
        service. A new SYNTHETIC ServiceProof must assert all existing checks for
        this context. No real proof-producer authenticity is implemented.
        """
        return RecoveryContext(
            instance_scope=self._recovery_scope,
            generation=self._recovery_generation,
            cause=self._recovery_cause,
            losses=tuple(self.losses),
            accounting_generation=self.accounting_generation,
            transactions=tuple(
                (key, t.resource, t.phase, t.timed_out, t.effect, t.disposition)
                for key, t in sorted(self.transactions.items())),
            ownership=self.owner, topology=self.topology, fixture=self.fixture,
            mapping=self.mapping, mapping_known=self.mapping_known,
            freeze_generation=self.freeze_generation, epoch=self.epoch,
            continuity_assumed=self.fresh, journal_scope=self.journal,
            journal_continuity=self.journal.continuity_basis if self.journal else None,
            request=self.request,
            event_outcome=self.event_outcome, event_running=self.event_running,
            effects=tuple(self.effects),
            contact_state=(self._contact_level, self._contact_released,
                           self._edge, self._used_edge),
        )

    def _invalidate_recovery(self, cause: str) -> None:
        """Advance on every accepted invalidating transition, even same-step,
        same-value or ABA changes. Never reset this counter on rejoin/restart.
        """
        self._recovery_generation += 1
        self._recovery_cause = cause
        self.service_proof = None
        if self.state == State.REARM:
            self.state = State.RECOVERY
            self.bus_grant, self.off_demand = False, True
        self._log("RECOVERY_CONTEXT_INVALIDATED", cause)

    def _log(self, action: str, detail: str = "") -> None:
        self.trace.append({"step": self.now, "state": self.state.value,
                           "action": action, "detail": detail,
                           "synthetic_only": True})

    def _need(self, condition: bool, code: str) -> None:
        if not condition:
            self._log("DENY", code)
            raise Denied(code)

    @staticmethod
    def _mapping_dict(mapping: Mapping) -> dict[str, str]:
        if (len(mapping) != 3 or {a for a, _ in mapping} != AXES
                or any(not isinstance(r, str) or not r for _, r in mapping)):
            raise Denied("INVALID_MAPPING")
        return dict(mapping)

    def _environment(self) -> None:
        self._need(self.fixture.label.startswith("SYNTHETIC:")
                   and ASSUMPTIONS <= self.fixture.assumptions
                   and self.fixture.envelope.startswith("SYNTHETIC:")
                   and self.fixture.limits.startswith("SYNTHETIC:"),
                   "ACTUAL_PREMISES_UNKNOWN")
        self._need(bool(self.fresh and self.journal
                        and self.journal.continuity_basis.startswith("SYNTHETIC:")),
                   "FRESHNESS_CONTINUITY_UNKNOWN")
        self._need(self.topology.inventory_complete_assumption
                   and self.topology.identity.startswith("SYNTHETIC:")
                   and self.topology.endpoints == ENDPOINTS, "TOPOLOGY_UNKNOWN")
        claims = self.owner.claims
        self._need(len(claims) == len(ACTORS)
                   and {c.actor for c in claims} == ACTORS
                   and all(c.disposition in ("cooperative", "excluded")
                           and c.basis.startswith("SYNTHETIC:") for c in claims),
                   "UNEXCLUDED_ACTOR")

    def closure(self, kind: str, old: Mapping, new: Mapping):
        """Old/new controller sharing plus explicit resource effects, fixed point.

        Resource names are abstract scheduling/ownership groups, not hardware
        instance allocations, electrical bridges or a third I2C controller.
        """
        old_d, new_d = self._mapping_dict(old), self._mapping_dict(new)
        self._need(kind in ("RESET", "DEBUG", "REMAP"), "UNKNOWN_EVENT_KIND")
        if kind != "REMAP":
            self._need(old == new, "NON_REMAP_MAPPING_CHANGE")
            axes = set(AXES)
        else:
            axes = {a for a in AXES if old_d[a] != new_d[a]}
            self._need(bool(axes), "EMPTY_REMAP")
        groups: dict[str, set[str]] = {}
        for a, resource in old + new:
            groups.setdefault(resource, set()).add(a)
        for resource, members in self.topology.resource_axes:
            self._need(bool(resource) and bool(members) and members <= AXES,
                       "UNKNOWN_RESOURCE_CLOSURE")
            groups.setdefault(resource, set()).update(members)
        changed = True
        while changed:
            size = len(axes)
            for members in groups.values():
                if members & axes:
                    axes.update(members)
            changed = len(axes) != size
        resources = frozenset(r for r, members in groups.items() if members & axes)
        endpoints = tuple(p for p in ENDPOINTS if p[0][0] in axes)
        return frozenset(axes), resources, endpoints

    def make_request(self, event_id: str, issuer: str, kind: str,
                     new_mapping: Mapping | None = None,
                     hold_until: int | None = None) -> Request:
        """Construction convenience only, NOT capture or permission."""
        new = self.mapping if new_mapping is None else new_mapping
        axes, resources, endpoints = self.closure(kind, self.mapping, new)
        return Request(event_id, issuer, self.epoch, kind, REVISION,
                       self.topology.identity, self.owner.generation,
                       self.mapping, new, axes, resources, endpoints, hold_until,
                       self._edge if issuer == "manual" else None)

    def contact(self, pressed: bool) -> None:
        if not pressed:
            self._contact_released = True
        elif self._contact_level is False and self._contact_released:
            self._edge += 1
            self._contact_released = False
        self._contact_level = pressed
        self._invalidate_recovery("CONTACT_REQUALIFICATION")
        self._log("CONTACT", str(pressed))
        if (not pressed and self.request and self.request.issuer == "manual"
                and self.state in (State.CAPTURED, State.WITHDRAW, State.EVIDENCE,
                                   State.PERMITTED, State.ACTIVE)):
            self.cancel()

    def capture(self, q: Request) -> None:
        self._need(self.state == State.SERVICE, "NO_SERVICE_FOR_REQUEST")
        self._environment()
        self._need(bool(q.event_id) and q.issuer in self.owner.issuers,
                   "UNKNOWN_ISSUER_OR_EVENT")
        self._need(q.epoch == self.epoch and q.revision == REVISION
                   and q.topology == self.topology.identity
                   and q.owner_generation == self.owner.generation
                   and q.old_mapping == self.mapping, "STALE_REQUEST_BINDING")
        self._need((q.axes, q.resources, q.endpoints) ==
                   self.closure(q.kind, q.old_mapping, q.new_mapping),
                   "INCOMPLETE_TARGET_CLOSURE")
        self._need(q.hold_until is None or q.hold_until >= self.now,
                   "HOLD_HORIZON_PAST")
        assert self.journal is not None  # established by _environment
        self._need((q.issuer, q.event_id) not in self.journal.events,
                   "EVENT_REPLAY")
        if q.issuer == "manual":
            self._need(self._contact_level is True and
                       q.contact_edge == self._edge > self._used_edge,
                       "HELD_OR_UNQUALIFIED_CONTACT")
            self._used_edge = self._edge
        self.journal.events.add((q.issuer, q.event_id))
        self.request, self.evidence, self.permit = q, None, None
        self.event_outcome = "NOT_STARTED"
        self.state = State.CAPTURED
        self._invalidate_recovery("REQUEST_CAPTURED")
        self._log("REQUEST_CAPTURED", q.event_id)

    def submit(self, identity: str, resource: str) -> None:
        self._need(self.bus_grant and self.state in (State.SERVICE, State.CAPTURED),
                   "ADMISSION_FROZEN")
        self._need(bool(identity) and identity not in self.transactions,
                   "TRANSACTION_REPLAY")
        self._need(resource in self.closure("RESET", self.mapping, self.mapping)[1],
                   "UNKNOWN_RESOURCE")
        self.transactions[identity] = Transaction(resource)
        self.accounting_generation += 1
        self._invalidate_recovery("TRANSACTION_SUBMITTED")
        self._log("QUEUED", identity)

    def start_transaction(self, identity: str) -> None:
        t = self.transactions[identity]
        self._need(self.state in (State.SERVICE, State.CAPTURED, State.WITHDRAW)
                   and t.phase == "QUEUED", "TRANSACTION_START_DENIED")
        t.phase = "ACTIVE"
        self.accounting_generation += 1
        self._invalidate_recovery("TRANSACTION_STARTED")
        self._log("TRANSACTION_ACTIVE", identity)

    def finish_transaction(self, identity: str, outcome: str) -> None:
        t = self.transactions[identity]
        self._need(t.phase == "ACTIVE" and outcome in ("DONE", "PARTIAL"),
                   "INVALID_TRANSACTION_COMPLETION")
        t.phase, t.effect = outcome, True
        self.accounting_generation += 1
        self.effects.append("transaction:" + identity + ":" + outcome)
        self._invalidate_recovery("TRANSACTION_FINISHED:" + outcome)
        self._log("TRANSACTION_RESULT", identity + ":" + outcome)

    def cancel_queued(self, identity: str) -> None:
        t = self.transactions[identity]
        self._need(t.phase == "QUEUED", "CANNOT_CANCEL_ACTIVE_TRANSACTION")
        t.phase = "CANCELLED_BEFORE_START"
        self.accounting_generation += 1
        self._invalidate_recovery("QUEUED_TRANSACTION_CANCELLED")
        self._log("SYNTHETIC_QUEUE_REMOVAL", identity)

    def timeout(self, identity: str) -> None:
        self.transactions[identity].timed_out = True  # NO cancellation/completion
        self.accounting_generation += 1
        self._invalidate_recovery("TRANSACTION_TIMEOUT_NOT_COMPLETION")
        self._log("TIMEOUT_NOT_CANCELLATION", identity)

    def dispose_transaction(self, identity: str, disposition: str) -> None:
        t = self.transactions[identity]
        self._need(t.phase in ("DONE", "PARTIAL", "CANCELLED_BEFORE_START")
                   and disposition == ("PARTIAL_NO_REPLAY" if t.phase == "PARTIAL"
                                       else "ACCOUNTED_NO_REPLAY"),
                   "TRANSACTION_NOT_DISPOSITIONED")
        t.disposition = disposition
        self.accounting_generation += 1
        self._invalidate_recovery("TRANSACTION_DISPOSITION_CHANGED")
        self._log("TRANSACTION_DISPOSITION", identity + ":" + disposition)

    def freeze(self) -> None:
        self._need(self.state == State.CAPTURED, "FREEZE_ORDER")
        self._environment()
        self.bus_grant, self.off_demand = False, True
        self.freeze_generation += 1
        self.state = State.WITHDRAW
        self._invalidate_recovery("ADMISSION_WITHDRAWN")
        self._log("FROZEN_BEFORE_ACCOUNTING")

    def _transactions_resolved(self, resources: frozenset[str]) -> bool:
        return all(t.disposition is not None for t in self.transactions.values()
                   if t.resource in resources)

    def quiesce(self, report: EngineReport) -> None:
        self._need(self.state == State.WITHDRAW, "FREEZE_REQUIRED")
        self._environment()
        self._need(report.request == self.request
                   and report.owner_generation == self.owner.generation
                   and report.resources == self.request.resources
                   and report.freeze_generation == self.freeze_generation
                   and report.accounting_generation == self.accounting_generation,
                   "STALE_ENGINE_REPORT")
        self._need(self._transactions_resolved(report.resources),
                   "LIVE_OR_UNDISPOSITIONED_TRANSACTION")
        self._need(report.origin == "SYNTHETIC:ENGINE_OBSERVATION"
                   and report.engines_idle and report.callbacks_fenced,
                   "ENGINE_QUIESCENCE_UNKNOWN")
        self.state = State.EVIDENCE
        self._invalidate_recovery("ENGINE_REPORT_ACCEPTED")
        self._log("QUIESCENCE_ASSUMED_NOT_DISCONNECTION")

    def observation(self, label: str) -> None:
        """ESP_OK, GPIO, SEL, idle, UART ACK, noos callback and timeout are data."""
        self._log("UNQUALIFIED_OBSERVATION", label)

    def _coverage(self, endpoints: tuple, cut_set: frozenset[str]) -> bool:
        if not cut_set:
            return False
        for endpoint in endpoints:
            for direction in ("H_TO_L", "L_TO_H"):
                paths = [r for r in self.topology.routes
                         if r.line == endpoint[0] and r.direction == direction]
                if not paths or any(not r.blockers & cut_set for r in paths):
                    return False
        return True

    def _evidence_valid(self, e: Evidence, check_horizon: bool = True) -> None:
        self._environment()
        self._need(e.request == self.request and e.request.epoch == self.epoch
                   and e.request.revision == REVISION
                   and e.request.topology == self.topology.identity
                   and e.request.owner_generation == self.owner.generation,
                   "STALE_EVIDENCE_BINDING")
        self._need(e.origin == "SYNTHETIC:DESIGN_PROOF"
                   and e.fixture == self.fixture.label
                   and e.envelope == self.fixture.envelope
                   and e.limits == self.fixture.limits
                   and EVIDENCE_CHECKS <= e.checks, "PROOF_PREMISES_UNKNOWN")
        self._need(0 <= e.available_at <= self.now
                   and 0 <= e.completion_latest <= self.now, "PROOF_NOT_YET_COMPLETE")
        self._need(self._coverage(e.request.endpoints, e.cut_set),
                   "UNCOVERED_DIRECTED_PATH")
        self._need((e.valid_until is None and e.indefinite_hold)
                   or (e.valid_until is not None
                       and e.valid_until >= self.now >= e.available_at),
                   "PROOF_EXPIRED_OR_UNBOUNDED_UNKNOWN")
        horizon = e.request.hold_until
        self._need(horizon is None or self.now <= horizon, "EVENT_HORIZON_EXCEEDED")
        if check_horizon:
            self._need((horizon is None and e.indefinite_hold and e.valid_until is None)
                       or (horizon is not None and
                           (e.valid_until is None or e.valid_until >= horizon)),
                       "HOLD_DOES_NOT_COVER_RECOVERY_REJOIN")

    def supply_evidence(self, evidence: Evidence) -> None:
        self._need(self.state == State.EVIDENCE, "EVIDENCE_ORDER")
        self._evidence_valid(evidence)
        self.evidence = evidence
        self._invalidate_recovery("EVENT_EVIDENCE_CHANGED")
        self._log("SYNTHETIC_C1_C4_PREMISES", ",".join(sorted(evidence.cut_set)))

    def authorize(self) -> Permit:
        self._need(self.state == State.EVIDENCE and self.evidence is not None,
                   "NO_COMPLETION_EVIDENCE")
        self._evidence_valid(self.evidence)
        self._serial += 1
        self.permit = Permit(self.request, self.evidence, self._serial)
        self.state = State.PERMITTED
        self._invalidate_recovery("EVENT_AUTHORIZATION_ISSUED")
        self._log("SYNTHETIC_ONE_USE_GRANT")
        return self.permit

    def start(self, permit: Permit) -> None:
        self._need(self.state == State.PERMITTED and permit is self.permit,
                   "PERMIT_REPLAY_OR_FOREIGN")
        self._evidence_valid(permit.evidence)
        self._need(self.mapping == permit.request.old_mapping, "MAPPING_CHANGED")
        # One modeled atomic step. NOT a hardware atomicity/latency guarantee.
        self.permit = None
        self.event_running = True
        self.state = State.ACTIVE
        self.event_outcome = "BEGUN_IRREVERSIBLE"
        self.effects.append("event:" + permit.request.event_id + ":FIRST_ACTION")
        self._invalidate_recovery("EVENT_FIRST_ACTION")
        self._log("CONSUMED_THEN_FIRST_IRREVERSIBLE_ACTION")

    def cancel(self) -> None:
        self._need(self.state in (State.CAPTURED, State.WITHDRAW, State.EVIDENCE,
                                 State.PERMITTED, State.ACTIVE, State.REARM), "CANCEL_ORDER")
        before_withdraw = self.state == State.CAPTURED
        cancelling_rearm = self.state == State.REARM
        self._invalidate_recovery("CANCEL:" + self.state.value)
        self.permit = None
        self.evidence = None
        if cancelling_rearm:
            # Cancel only the prepared service authorization, not the historical
            # event outcome. Reuse of the revoked proof must still be denied.
            self._log("CANCEL_REARM_NO_AUTOMATIC_REJOIN")
        elif self.event_running:
            self.event_outcome = "CANCEL_REQUESTED_CANNOT_UNDO"
            self.state = State.LOST
            self._log("CANCEL_FUTURE_ACTIONS_ONLY")
        elif before_withdraw:
            self.state = State.SERVICE  # existing service never withdrawn
            self.request = None
            self._log("CANCEL_BEFORE_WITHDRAW_SERVICE_UNCHANGED")
        else:
            self.state = State.RECOVERY
            self.event_outcome = "CANCELLED_BEFORE_EVENT"
            self._log("CANCEL_NO_AUTOMATIC_REJOIN")

    def finish_event(self, outcome: str) -> None:
        self._need(self.event_running and self.state in (State.ACTIVE, State.LOST)
                   and outcome in ("COMPLETE", "PARTIAL_NOT_ROLLED_BACK"),
                   "EVENT_COMPLETION_UNKNOWN")
        # After loss/cancel, caller cannot convert a partial/unknown event to a
        # clean COMPLETE merely by emitting a success label.
        self._need(self.state != State.LOST or outcome == "PARTIAL_NOT_ROLLED_BACK",
                   "LOSS_CANNOT_BECOME_CLEAN_SUCCESS")
        self.event_running = False
        self.event_outcome = outcome
        if outcome == "COMPLETE":
            self.mapping = self.request.new_mapping
        else:
            self.mapping_known = False  # retained old tuple is NOT a rollback
        self.state = State.RECOVERY
        self._invalidate_recovery("EVENT_TERMINATED:" + outcome)
        self._log("EVENT_TERMINATION", outcome)

    def lose(self, reason: str) -> None:
        self.losses.append(reason)
        self._invalidate_recovery("LOSS:" + reason)
        self.permit = self.evidence = self.service_proof = None
        self.bus_grant, self.off_demand = False, True
        self.state = State.LOST
        self._log("PROOF_OR_OWNERSHIP_LOST_NOT_PHYSICAL_CONTAINMENT", reason)

    def advance(self, step: int) -> None:
        self._need(type(step) is int and step >= self.now, "NON_MONOTONIC_MODEL_TIME")
        self.now = step
        if self.evidence is not None:
            try:
                self._evidence_valid(self.evidence)
            except Denied as error:
                self.lose(str(error))
        if self.service_proof and step > self.service_proof.valid_until:
            self.lose("SERVICE_PROOF_EXPIRED")

    def replace_owner(self, owner: Ownership) -> None:
        self.owner = owner
        self.lose("OWNER_GENERATION_OR_ACTOR_SET_CHANGED")

    def replace_topology(self, topology: Topology) -> None:
        self.topology = topology
        self.lose("TOPOLOGY_OR_CUT_GRAPH_CHANGED")

    def bypass(self, actor: str) -> None:
        """A counterexample input, EVEN if fixture formerly assumed exclusion."""
        self._need(actor in ACTORS, "UNKNOWN_ACTOR")
        self.effects.append("BYPASS:" + actor + ":UNCONTROLLED_EFFECT")
        self.mapping_known = False
        self.event_outcome = "UNCONTROLLED_EFFECT"
        self.lose("BYPASS_ASSUMPTION_VIOLATED:" + actor)

    def restart(self, new_epoch: str, continuity_retained: bool = False) -> None:
        """Unexpected/model restart: no automatic grant, drain or termination."""
        self.lose("RESTART_INVALIDATES_OLD_AUTHORITY")
        self.epoch = new_epoch
        self.mapping_known = False
        self.fresh = bool(continuity_retained and self.journal
                          and self.journal.reserve_epoch(new_epoch))
        self._contact_level, self._contact_released = None, False
        self._used_edge = self._edge  # held levels cannot create a new request
        # Active transactions/event remain potentially live; do not reset counts.

    def _service_valid(self, p: ServiceProof) -> None:
        self._environment()
        self._mapping_dict(p.mapping)
        self._need(p.revision == REVISION and p.topology == self.topology.identity
                   and (not self.mapping_known or p.mapping == self.mapping)
                   and p.old_epoch == self.epoch
                   and p.owner_generation == self.owner.generation,
                   "STALE_SERVICE_BINDING")
        self._need(p.fixture == self.fixture.label and p.envelope == self.fixture.envelope
                   and p.limits == self.fixture.limits and SERVICE_CHECKS <= p.checks,
                   "SERVICE_PREMISES_UNKNOWN")
        self._need(not self.event_running
                   and self._transactions_resolved(frozenset(t.resource
                                                            for t in self.transactions.values())),
                   "RECOVERY_HAS_LIVE_WORK")
        self._need(p.event_outcome == self.event_outcome
                   and p.event_binding == self.request, "OUTCOME_NOT_ACCOUNTED")
        self._need(0 <= p.available_at <= self.now <= p.valid_until,
                   "SERVICE_PROOF_NOT_CURRENT")
        self._need(self._coverage(ENDPOINTS, p.cut_set), "REJOIN_HOLD_UNPROVEN")
        self._need(bool(p.request_id) and bool(p.new_epoch)
                   and p.new_epoch != self.epoch, "REARM_NEEDS_FRESH_EPOCH")
        self._need(self.journal is not None and p.request_id not in self.journal.service_ids
                   and p.new_epoch not in self.journal.epochs, "SERVICE_REPLAY")
        if self.request and self.request.issuer == "manual":
            self._need(self._contact_level is False, "MANUAL_RELEASE_REQUIRED")
        # Used by BOTH prepare_rearm and actual rejoin. Timestamps, unused epoch
        # names and caller-supplied owner generations cannot refresh this binding.
        self._need(p.recovery == self.recovery_context(), "STALE_RECOVERY_CONTEXT")

    def prepare_rearm(self, proof: ServiceProof) -> None:
        self._need(self.state in (State.RECOVERY, State.LOST), "REARM_ORDER")
        self._service_valid(proof)
        self.service_proof = proof
        self.state = State.REARM
        self._log("FRESH_SERVICE_QUALIFIED_STILL_ISOLATION_DEMAND")

    def rejoin(self, proof: ServiceProof) -> None:
        self._need(self.state == State.REARM and proof is self.service_proof,
                   "NO_FRESH_REJOIN_AUTHORIZATION")
        self._service_valid(proof)
        assert self.journal is not None
        self._need(self.journal.reserve_epoch(proof.new_epoch), "SERVICE_EPOCH_REPLAY")
        self.journal.service_ids.add(proof.request_id)
        self.epoch = proof.new_epoch
        self.mapping, self.mapping_known = proof.mapping, True
        self.request = self.evidence = self.permit = self.service_proof = None
        self.bus_grant, self.off_demand = True, False
        self.state = State.SERVICE
        self._invalidate_recovery("SERVICE_REJOINED")
        self._log("SYNTHETIC_SEQUENTIAL_REJOIN")

    def snapshot(self) -> dict:
        return {
            "state": self.state.value, "step": self.now, "epoch": self.epoch,
            "recovery_generation": self._recovery_generation,
            "recovery_cause": self._recovery_cause,
            "mapping_known_in_fixture": self.mapping_known,
            "synthetic_bus_grant": self.bus_grant,
            "synthetic_event_permit": self.permit is not None,
            "off_demand_not_achievement": self.off_demand,
            "actual_operation_permission": False, "actual_bus_permission": False,
            "physical_disconnection_established": False,
            "normal_board_conformance": "UNKNOWN", "actual_electrical_limits": "UNKNOWN",
            "motor_inhibit": "UNKNOWN", "command_permission": False,
            "event_running": self.event_running, "event_outcome": self.event_outcome,
            "effects_not_rolled_back": list(self.effects),
            "historical_losses_not_repaired": list(self.losses),
        }
