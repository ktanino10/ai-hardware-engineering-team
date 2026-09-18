"""HOST-ONLY command ordering, not GPIO firmware or a physical safety barrier.

Driver binding: original proposal/schematic + EFFECTIVE capacitance correction.
DS-IFACE-002/040/075: A1 -> /CLR, A2 -> CLK, active-HIGH OE; own-rail D/PRE.
DS-IFACE-039/055: receiver qualification required; high-Z is not LOW.
DS-IFACE-017 corrected view: no capacitance MAX / RC / arrival bound inferred.

Every receiving state below is an explicit external SYNTHETIC assumption.
No command, ACK, logical index or FF symbol generates physical proof. The
existing model exclusively owns request/epoch/proof/invalidation/recovery.
"""
from dataclasses import dataclass, asdict
import hashlib
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parent
BINDINGS = {
    "model.py":
        "ce496b2806b21966d68cec789ae85ec5dbdd4cf1eb7762a8d0b29fac172af447",
    "source-context/acceptance-spec.json":
        "07a73624d64cca3463930a878faaefce41eab16f0a1a77d9f6b8de1c1bd1e290",
    "source-context/firmware-authority-map.json":
        "0da8afe95c78da49c547859b3777e3a1ec41805323e8877294a95393d71936d3",
    "source-context/driver-proposal.json":
        "4c26e4bdb00335bae9b1a63366d66f680b41c3fb2ed3ee26067e09bb31e8e582",
    "source-context/driver-schematic.md":
        "bb828875aac86ff62469419b7d981275fb3cdcbffb0171d07a3777db60c05fb2",
    "source-context/source-proposals.json":
        "49d613967bb59c8a9f17e76b666549c65eb92ede5cb626bea81c963255c14c85",
    "source-context/capacitance-correction.json":
        "45440084ce0a51fe4cbe12ef45a65ab000564eb21dddb7ea897e7052d0900d71",
}


def _read_public(path):
    current = ROOT
    for part in Path(path).parts:
        current = current / part
        if current.is_symlink():
            raise RuntimeError("PUBLIC_SOURCE_SYMLINK:" + path)
    try:
        return current.read_bytes()
    except OSError:
        raise RuntimeError("PUBLIC_SOURCE_UNREADABLE:" + path) from None


def check_bindings():
    """Check this derivative's seven explicit bindings, not original seals."""
    for path, expected in BINDINGS.items():
        if hashlib.sha256(_read_public(path)).hexdigest() != expected:
            raise RuntimeError("PUBLIC_SOURCE_MISMATCH:" + path)
    return dict(BINDINGS)


def _load_existing_model():
    check_bindings()
    data = _read_public("model.py")
    if hashlib.sha256(data).hexdigest() != BINDINGS["model.py"]:
        raise RuntimeError("PUBLIC_SOURCE_MISMATCH:model.py")
    name = __name__.rsplit(".", 1)[0] + ".model"
    if name in sys.modules:
        raise RuntimeError("PUBLIC_MODEL_MODULE_COLLISION")
    module = ModuleType(name)
    module.__file__ = str(ROOT / "model.py")
    sys.modules[name] = module  # dataclasses requires registration
    try:
        exec(compile(data, "model.py", "exec"), module.__dict__)
    except BaseException:
        del sys.modules[name]
        raise
    return module


base = _load_existing_model()
Denied = base.Denied
AXES = ("X", "Y", "Z")
UNKNOWN = "UNKNOWN"
LOW, HIGH, Z = "LOW", "HIGH", "HIGH_Z"
SYNTHETIC = "SYNTHETIC:EXTERNAL_RECEIVING_ORACLE"
# Qualitative obligations, deliberately no selected time / voltage / load.
COMMON = frozenset({
    "C_power_qualified", "local_power_qualified", "return_load_qualified",
    "D_PRE_qualified_HIGH", "receiver_edges_qualified",
    "complete_ordered_history_no_unobserved_edges",
    "other_axes_preserve_qualified_states",
})
RELEASE = frozenset({"clean_clear_release_with_clock_LOW"})
PULSE = frozenset({"recovery_setup_hold_qualified", "fresh_single_pulse_qualified"})
FINISH = frozenset({"pulse_completed_qualified"})
ENABLE = frozenset({"source_LOW_before_OE_return", "active_clear_qualified"})


@dataclass(frozen=True)
class Receiving:
    """Separate source pin, driver-drive and FF-receiver assumptions."""
    source_clr: str = UNKNOWN
    source_clk: str = UNKNOWN
    source_oe: str = UNKNOWN
    driver_clr: str = UNKNOWN
    driver_clk: str = UNKNOWN
    ff_clr: str = UNKNOWN
    ff_clk: str = UNKNOWN
    ff_q: str = UNKNOWN


@dataclass(frozen=True)
class Step:
    axis: str
    label: str
    signal: str
    level: str
    expected: Receiving
    required: frozenset[str]


@dataclass(frozen=True)
class Command:
    sequence: int
    ordinal: int
    axis: str
    stage: str
    signal: str
    level: str
    source_port: str
    driver_pin: str
    driver_output_pin: str
    receiver_pin: str


@dataclass(frozen=True)
class ReceiveAssumption:
    """External fixture input, NOT a software ACK or measured hardware record.

    Object ticket identity and old recovery snapshot restrict this serialized
    model's API. Python attribute access is not security or authentication.
    """
    command: Command
    origin: str
    receiving: Receiving
    qualified: frozenset[str]


def _step(axis, label, signal, level, states, required=()):
    return Step(axis, label, signal, level, Receiving(*states),
                COMMON | frozenset(required))


def hold_steps(mode):
    """Source schematic sections 5/6. All XYZ only in this first cut."""
    result = []
    for axis in AXES:
        if mode == "initialize":
            # Explicitly UNKNOWN receiver voltage after high-Z; no POR/RC model.
            result += [
                _step(axis, "DISABLE", "OE", LOW,
                      (UNKNOWN, UNKNOWN, LOW, Z, Z, UNKNOWN, UNKNOWN, UNKNOWN)),
                _step(axis, "PARK_CLEAR", "CLR", LOW,
                      (LOW, UNKNOWN, LOW, Z, Z, UNKNOWN, UNKNOWN, UNKNOWN)),
                _step(axis, "PARK_CLOCK", "CLK", LOW,
                      (LOW, LOW, LOW, Z, Z, UNKNOWN, UNKNOWN, UNKNOWN)),
                _step(axis, "ENABLE_LOW", "OE", HIGH,
                      (LOW, LOW, HIGH, LOW, LOW, LOW, LOW, LOW), ENABLE),
            ]
        else:
            # Never routinely disable an existing active-clear path on withdraw.
            result += [
                _step(axis, "ACTIVE_CLEAR", "CLR", LOW,
                      (LOW, LOW, HIGH, LOW, LOW, LOW, LOW, LOW),
                      {"active_clear_qualified"}),
                _step(axis, "NORMALIZE_CLOCK", "CLK", LOW,
                      (LOW, LOW, HIGH, LOW, LOW, LOW, LOW, LOW),
                      {"active_clear_qualified"}),
            ]
    return tuple(result)


def rejoin_steps():
    return tuple(step for axis in AXES for step in (
        _step(axis, "REJOIN_CLOCK_LOW", "CLK", LOW,
              (LOW, LOW, HIGH, LOW, LOW, LOW, LOW, LOW),
              {"active_clear_qualified"}),
        _step(axis, "RELEASE_CLEAR", "CLR", HIGH,
              (HIGH, LOW, HIGH, HIGH, LOW, HIGH, LOW, LOW), RELEASE),
        _step(axis, "FRESH_CLOCK_HIGH", "CLK", HIGH,
              (HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH), PULSE),
        _step(axis, "PULSE_CLOCK_LOW", "CLK", LOW,
              (HIGH, LOW, HIGH, HIGH, LOW, HIGH, LOW, HIGH), FINISH),
    ))


class Sequencer:
    """Adds only command tickets, receive fences and a rejoin completion fence.

    Model is caller-owned. Direct use of it is NOT an alternate sequencer API:
    the wrapper checks context on every in-flight transition, and service epoch
    at use. It cannot police arbitrary Python writes or real external actors.
    """
    def __init__(self, model):
        self.model = model
        self.sequence = 0
        self.phase = "IDLE"
        self.plan = ()
        self.index = 0
        self.pending = None
        self.context = None
        self.proof = None
        self.service_epoch = None
        self.receiving = {a: Receiving() for a in AXES}
        self.trace = []

    def _log(self, action, **detail):
        self.trace.append({
            "index_not_time": len(self.trace), "action": action,
            "phase": self.phase, "detail": detail,
            "actual_operation_permission": False,
            "physical_conductance": UNKNOWN,
        })

    def interrupt(self, reason):
        """Revoke via existing generation logic. Issued effects are NOT undone."""
        self.model.lose("OUTPUT_SEQUENCE:" + reason)
        self.phase = "INTERRUPTED"
        self.plan = ()
        self.pending = self.context = self.proof = None
        self.service_epoch = None
        self.receiving = {a: Receiving() for a in AXES}
        # These are only new LOW demands; do not claim they arrive, cancel an
        # already issued HIGH, beat an in-flight edge, or re-establish isolation.
        self._log("INTERRUPT_NO_ROLLBACK", reason=reason,
                  best_effort_demands=[
                      {"axis": a, "signal": s, "level": LOW}
                      for a in AXES for s in ("CLR", "CLK")],
                  OE="NO_NEW_ENABLE_OR_DISABLE_COMMAND",
                  in_flight_physical_effects=UNKNOWN)

    def _need(self, condition, reason):
        if not condition:
            self.interrupt(reason)
            raise Denied(reason)

    def _current(self):
        self._need(self.context is not None
                   and self.context == self.model.recovery_context(),
                   "STALE_SEQUENCE_RECOVERY_CONTEXT")
        if self.phase == "REJOIN":
            # FR-SEQ-01: journal consumption need not change recovery_context.
            # issue/receive must reuse the FULL non-consuming base validator,
            # not a shadow epoch-set check. Final rejoin still validates/consumes.
            self._need(self.model.state == base.State.REARM
                       and self.proof is self.model.service_proof,
                       "NO_FRESH_REJOIN_AUTHORIZATION")
            try:
                self.model._service_valid(self.proof)
            except Denied:
                # A HIGH already issued before this fence is not recalled.
                self.interrupt("EXISTING_FORWARD_REJOIN_VALIDATION_REFUSED")
                raise

    def _begin(self, kind, plan):
        self.sequence += 1
        self.phase, self.plan, self.index = kind, plan, 0
        self.pending = None
        self.context = self.model.recovery_context()
        self._log("BEGIN", sequence=self.sequence, stages=len(plan))

    def begin_hold(self, mode="initialize"):
        self._need(mode in ("initialize", "withdraw", "recover"), "UNKNOWN_HOLD_MODE")
        self._need(self.phase not in ("HOLD", "REJOIN", "READY_TO_COMMIT"),
                   "SEQUENCE_ALREADY_ACTIVE")
        if mode == "withdraw":
            self._need(self.service_epoch == self.model.epoch
                       and self.model.state == base.State.EVIDENCE
                       and self.model.request is not None
                       and self.model.request.axes == base.AXES,
                       "WITHDRAW_NEEDS_EXISTING_FULL_SCOPE_FREEZE_AND_QUIESCENCE")
        else:
            self._need(self.model.state in (base.State.RECOVERY, base.State.LOST),
                       "INITIALIZATION_NEEDS_WITHDRAWN_SERVICE")
            # Restarting output qualification can disturb earlier held-state
            # premises. Use the EXISTING invalidator; no second epoch machine.
            self.model.lose("OUTPUT_HOLD_REQUALIFICATION")
        self.service_epoch = None
        self.proof = None
        self._begin("HOLD", hold_steps(mode))

    def begin_rejoin(self, proof):
        self._need(self.phase == "HELD", "ACTIVE_HOLD_NOT_QUALIFIED")
        self._current()
        self._need(isinstance(proof, base.ServiceProof), "MALFORMED_SERVICE_PROOF")
        self._need(all(r.ff_q == LOW and r.ff_clr == LOW
                       and r.ff_clk == LOW and r.source_oe == HIGH
                       for r in self.receiving.values()), "HOLD_STATE_UNKNOWN")
        # NOT a locally manufactured proof. The caller supplies qualification;
        # the existing validator checks the cause/generation at preparation.
        try:
            self.model.prepare_rearm(proof)
        except Denied:
            self.interrupt("EXISTING_PREPARE_REFUSED")
            raise
        except (TypeError, AttributeError) as error:
            self.interrupt("MALFORMED_SERVICE_PROOF")
            raise Denied("MALFORMED_SERVICE_PROOF") from error
        self.proof = proof
        self._begin("REJOIN", rejoin_steps())

    def issue(self):
        self._need(self.phase in ("HOLD", "REJOIN"), "NO_ISSUABLE_SEQUENCE")
        self._current()
        self._need(self.pending is None, "AWAITING_EXTERNAL_RECEIVING_ASSUMPTION")
        step = self.plan[self.index]
        port, dp, rp = {
            "CLR": ("C_CLR_RELEASE_", ".2", ".6"),
            "CLK": ("C_FRESH_CLK_", ".3", ".1"),
            "OE": ("C_DRV_ENABLE_", ".8", ".8"),
        }[step.signal]
        command = Command(self.sequence, self.index, step.axis, step.label,
                          step.signal, step.level, port + step.axis,
                          "TDRV_" + step.axis + dp,
                          ("TDRV_" + step.axis + {"CLR": ".13", "CLK": ".12",
                                                 "OE": ".8"}[step.signal]),
                          ("TDRV_" if step.signal == "OE" else "FF_")
                          + step.axis + rp)
        self.pending = command
        self._log("COMMAND_INTENT_ONLY", command=asdict(command),
                  physical_pin_state=UNKNOWN, arrival_order=UNKNOWN)
        return command

    def ack(self, label="SOFTWARE_ACK"):
        self.model.observation(label)
        self._log("ACK_NOT_RECEIVING_EVIDENCE", label=label)

    def receive(self, assumption):
        self._need(self.phase in ("HOLD", "REJOIN"), "NO_RECEIVING_SEQUENCE")
        self._current()
        self._need(isinstance(assumption, ReceiveAssumption)
                   and assumption.command is self.pending
                   and self.pending is not None, "STALE_OR_FOREIGN_COMMAND_TICKET")
        step = self.plan[self.index]
        self._need(assumption.origin == SYNTHETIC, "RECEIVE_ORACLE_UNKNOWN")
        self._need(isinstance(assumption.qualified, frozenset),
                   "MALFORMED_RECEIVE_QUALIFICATION")
        self._need(step.required <= assumption.qualified,
                   "POWER_ORDER_OR_RECEIVER_QUALIFICATION_UNKNOWN")
        self._need(assumption.receiving == step.expected,
                   "RECEIVING_STATE_NOT_EXPECTED")
        self.receiving[step.axis] = assumption.receiving
        self._log("EXTERNAL_SYNTHETIC_RECEIVING_ASSUMPTION",
                  command=asdict(assumption.command),
                  receiving=asdict(assumption.receiving),
                  qualified=sorted(assumption.qualified),
                  still_not_physical_evidence=True)
        self.index += 1
        self.pending = None
        if self.index == len(self.plan):
            self.phase = "HELD" if self.phase == "HOLD" else "READY_TO_COMMIT"
            self._log("SEQUENCE_RECEIVING_FENCES_COMPLETE")

    def commit_rejoin(self, proof):
        self._need(self.phase == "READY_TO_COMMIT", "OUTPUT_SEQUENCE_INCOMPLETE")
        self._current()
        self._need(proof is self.proof, "FOREIGN_SERVICE_PROOF")
        try:
            # Existing _service_valid runs AGAIN here. Never assign bus_grant.
            self.model.rejoin(proof)
        except Denied:
            self.interrupt("EXISTING_REJOIN_REFUSED")
            raise
        self.service_epoch = self.model.epoch
        self.phase = "SERVICE"
        self.context = self.proof = None
        self._log("EXISTING_MODEL_REJOIN_COMMITTED",
                  service_epoch=self.service_epoch, synthetic_only=True)

    def require_service(self):
        self._need(self.phase == "SERVICE"
                   and self.model.state == base.State.SERVICE
                   and self.model.bus_grant
                   and self.model.epoch == self.service_epoch,
                   "NO_SEQUENCED_SERVICE")

    def snapshot(self):
        service = (self.phase == "SERVICE"
                   and self.model.state == base.State.SERVICE
                   and self.model.bus_grant
                   and self.model.epoch == self.service_epoch)
        return {
            "phase": self.phase, "sequence": self.sequence,
            "synthetic_sequenced_service": service,
            "receiving_assumptions": {a: asdict(r) for a, r in self.receiving.items()},
            "actual_operation_permission": False, "actual_bus_permission": False,
            "actual_pin_states": UNKNOWN, "actual_arrival_order": UNKNOWN,
            "physical_disconnection_established": False,
            "physical_conductance": UNKNOWN, "motor_inhibit": UNKNOWN,
            "model": self.model.snapshot(),
        }


def symbolic_ff(q, clr, previous_clk, clk, *, qualified):
    """Bounded adverse-witness primitive, NOT part of permission generation.

    DS-IFACE-075 functional cases under externally qualified D/PRE HIGH.
    qualified also assumes receiver recovery/setup/hold/pulse conditions; no
    time unit or propagation calculation is supplied. Otherwise UNKNOWN.
    """
    if qualified is not True or any(x not in (LOW, HIGH)
                                   for x in (clr, previous_clk, clk)):
        return UNKNOWN
    if clr == LOW:
        return LOW
    if previous_clk == LOW and clk == HIGH:
        return HIGH
    return q


def adverse_order(order="clear_first", qualified=True):
    """Executable counterexample to treating an OE return as fresh intent."""
    if order not in ("clear_first", "clock_first"):
        raise ValueError("unknown receive order")
    # External INITIAL LOW receiver bias and normal power are explicit,
    # not inferred from an OE=LOW command or from pull-down positions.
    clr, clk, q = LOW, LOW, LOW
    events = []
    for signal in (("CLR", "CLK") if order == "clear_first" else ("CLK", "CLR")):
        old_clk = clk
        if signal == "CLR":
            clr = HIGH
        else:
            clk = HIGH
        q = symbolic_ff(q, clr, old_clk, clk, qualified=qualified)
        events.append({"received": signal + "_STALE_HIGH", "ff_clr": clr,
                       "ff_clk": clk, "ff_q_symbolic": q})
    return {
        "case": "OE_RETURN_STALE_HIGH", "fresh_request": False,
        "command_intent": {"CLR": HIGH, "CLK": HIGH, "OE": "LOW_THEN_HIGH"},
        "bad_command_order": [
            {"signal": "OE", "level": LOW},
            {"signal": "CLR", "level": HIGH, "meaning": "retained, not fresh"},
            {"signal": "CLK", "level": HIGH, "meaning": "retained, not fresh"},
            {"signal": "OE", "level": HIGH, "meaning": "BAD: no LOW parking"},
        ],
        "external_initial_condition": "SYNTHETIC:qualified_receiver_LOWs",
        "external_receive_order": "SYNTHETIC:" + order,
        "external_receiver_conditions_qualified": qualified,
        "events": events, "ff_q_symbolic": q,
        "actual_operation_permission": False, "actual_bus_permission": False,
        "physical_conductance": UNKNOWN, "actual_arrival_order": UNKNOWN,
        "conclusion": "Counterexample, not a supported rejoin API or real waveform",
    }
