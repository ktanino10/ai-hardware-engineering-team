"""Explicit external SYNTHETIC fixtures for the CLI/tests, never target inputs.

This module is deliberately separate from sequencer.py. Receiver rows below
are supplied hypothetical histories, NOT observations produced by executing
commands. A real adapter/proof producer does not exist in this scope.
"""
from dataclasses import replace
from .sequencer import (
    base, Sequencer, Denied, Receiving, ReceiveAssumption,
    LOW, HIGH, Z, UNKNOWN, SYNTHETIC, adverse_order,
)


# Independent fixture table: source CLR/CLK/OE, driver CLR/CLK,
# FF receiving CLR/CLK, FF Q. UNKNOWN never means LOW.
RECEIVE_ROWS = {
    "DISABLE": (UNKNOWN, UNKNOWN, LOW, Z, Z, UNKNOWN, UNKNOWN, UNKNOWN),
    "PARK_CLEAR": (LOW, UNKNOWN, LOW, Z, Z, UNKNOWN, UNKNOWN, UNKNOWN),
    "PARK_CLOCK": (LOW, LOW, LOW, Z, Z, UNKNOWN, UNKNOWN, UNKNOWN),
    "ENABLE_LOW": (LOW, LOW, HIGH, LOW, LOW, LOW, LOW, LOW),
    "ACTIVE_CLEAR": (LOW, LOW, HIGH, LOW, LOW, LOW, LOW, LOW),
    "NORMALIZE_CLOCK": (LOW, LOW, HIGH, LOW, LOW, LOW, LOW, LOW),
    "REJOIN_CLOCK_LOW": (LOW, LOW, HIGH, LOW, LOW, LOW, LOW, LOW),
    "RELEASE_CLEAR": (HIGH, LOW, HIGH, HIGH, LOW, HIGH, LOW, LOW),
    "FRESH_CLOCK_HIGH": (HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH),
    "PULSE_CLOCK_LOW": (HIGH, LOW, HIGH, HIGH, LOW, HIGH, LOW, HIGH),
}
QUALIFIED = frozenset({
    "C_power_qualified", "local_power_qualified", "return_load_qualified",
    "D_PRE_qualified_HIGH", "receiver_edges_qualified",
    "complete_ordered_history_no_unobserved_edges",
    "other_axes_preserve_qualified_states",
    "source_LOW_before_OE_return", "active_clear_qualified",
    "clean_clear_release_with_clock_LOW", "recovery_setup_hold_qualified",
    "fresh_single_pulse_qualified", "pulse_completed_qualified",
})
MAPPING = (("X", "resource-X"), ("Y", "resource-Y"), ("Z", "resource-Z"))
CUTS = frozenset("L:" + p[0] for p in base.ENDPOINTS)


def machine():
    """Same existing endpoint contract; NOT another electrical graph campaign."""
    topology = base.Topology(
        "SYNTHETIC:external-complete-inventory",
        tuple(base.Route(p[0], d, frozenset({"L:" + p[0]}))
              for p in base.ENDPOINTS for d in ("H_TO_L", "L_TO_H")),
        inventory_complete_assumption=True,
    )
    owner = base.Ownership(
        1, frozenset({"scheduler", "manual"}),
        tuple(base.ActorClaim(a, "excluded", "SYNTHETIC:external-exclusion")
              for a in sorted(base.ACTORS)),
    )
    fixture = base.Fixture(
        "SYNTHETIC:qualified-normal-components", base.ASSUMPTIONS,
        "SYNTHETIC:unquantified-envelope", "SYNTHETIC:unquantified-limits")
    return base.Model(topology, MAPPING, owner, "epoch:initial", fixture,
                      base.SyntheticJournal("SYNTHETIC:external-continuity"))


def external_service_proof(m, identity):
    """External oracle explicitly asserts ALL service checks for this context.

    Context reading alone is not qualification. This helper is fixture input,
    not a producer inferred from output completion or ACK. Valid only at the
    unchanged logical step; the number is not a chosen physical delay.
    """
    return base.ServiceProof(
        "SYNTHETIC:service:" + identity, m.epoch, "epoch:" + identity,
        base.REVISION, m.topology.identity, m.mapping, m.owner.generation,
        m.fixture.label, m.fixture.envelope, m.fixture.limits,
        base.SERVICE_CHECKS, CUTS, m.request, m.event_outcome, m.now, m.now,
        recovery=m.recovery_context())


def external_receive(command):
    return ReceiveAssumption(command, SYNTHETIC,
                             Receiving(*RECEIVE_ROWS[command.stage]), QUALIFIED)


def run_sequence(s):
    while s.phase in ("HOLD", "REJOIN"):
        command = s.issue()
        s.ack("COMMAND_ACCEPTED_ONLY")
        s.receive(external_receive(command))


def hold(s, mode="initialize"):
    s.begin_hold(mode)
    run_sequence(s)


def rejoin(s, identity):
    proof = external_service_proof(s.model, identity)
    s.begin_rejoin(proof)
    run_sequence(s)
    s.commit_rejoin(proof)
    return proof


def boot():
    s = Sequencer(machine())
    hold(s)
    rejoin(s, "boot")
    return s


def useful(s, identity):
    # Actual calls to the REUSED model, not a fabricated "success" log.
    s.require_service()
    m = s.model
    m.submit(identity, dict(m.mapping)["X"])
    m.start_transaction(identity)
    m.finish_transaction(identity, "DONE")
    m.dispose_transaction(identity, "ACCOUNTED_NO_REPLAY")


def pending_event(s, issuer="scheduler"):
    m = s.model
    q = m.make_request("event:new", issuer, "RESET")
    m.capture(q)
    m.freeze()
    m.quiesce(base.EngineReport(
        q, m.owner.generation, q.resources, m.freeze_generation,
        m.accounting_generation, "SYNTHETIC:ENGINE_OBSERVATION", True, True))
    hold(s, "withdraw")
    return q


def finish_event(s):
    m = s.model
    m.supply_evidence(base.Evidence(
        m.request, "SYNTHETIC:DESIGN_PROOF", m.fixture.label,
        m.fixture.envelope, m.fixture.limits, CUTS, base.EVIDENCE_CHECKS,
        m.now, m.now, None, True))
    token = m.authorize()
    m.start(token)
    m.finish_event("COMPLETE")
    # The old model advanced generations during the event. Reconfirm active
    # clear with new receiving assumptions; never reuse old held-state tickets.
    hold(s, "recover")


def pack(s, name, outcome, **extra):
    return {
        "scenario": name, "outcome": outcome,
        "assumptions": "EXPLICIT_SYNTHETIC_EXTERNAL_ORACLES_ONLY",
        "logical_indexes_are_not_elapsed_time": True,
        "output_trace": s.trace, "existing_model_trace": s.model.trace,
        "final": s.snapshot(), **extra,
    }


def normal():
    s = boot()
    useful(s, "useful-before-event")
    pending_event(s)
    finish_event(s)
    rejoin(s, "fresh-after-event")
    useful(s, "useful-after-event")
    assert s.snapshot()["synthetic_sequenced_service"]
    return pack(s, "normal", "USEFUL_SYNTHETIC_SERVICE_NOT_PHYSICAL_PERMISSION")


def held_request():
    s = boot()
    m = s.model
    m.contact(True)  # level retained at startup, no release/new qualified edge
    q = m.make_request("stale-strobe", "manual", "RESET")
    try:
        m.capture(q)
    except Denied as error:
        assert str(error) == "HELD_OR_UNQUALIFIED_CONTACT"
        return pack(s, "held-request", "EXPECTED_REFUSAL", denial=str(error),
                    note="TREQ OE-return edge is not translated into CLK")
    raise AssertionError("held request unexpectedly accepted")


def unknown(kind):
    s = Sequencer(machine())
    s.begin_hold()
    command = s.issue()
    assumption = external_receive(command)
    if kind in ("C", "local"):
        missing = "C_power_qualified" if kind == "C" else "local_power_qualified"
        assumption = replace(assumption, qualified=assumption.qualified - {missing})
    elif kind == "output":
        assumption = replace(assumption, receiving=Receiving())
    elif kind == "ACK":
        s.ack()
        try:
            s.issue()
        except Denied as error:
            return pack(s, "unknown-ACK", "EXPECTED_REFUSAL", denial=str(error))
        raise AssertionError("ACK advanced receive fence")
    else:
        raise ValueError(kind)
    try:
        s.receive(assumption)
    except Denied as error:
        assert not s.model.bus_grant
        return pack(s, "unknown-" + kind, "EXPECTED_REFUSAL", denial=str(error))
    raise AssertionError("unknown assumption accepted")


def cancel_or_loss(kind):
    s = boot()
    pending_event(s)
    finish_event(s)
    p = external_service_proof(s.model, "before-loss")
    s.begin_rejoin(p)
    # Meaningful point: first axis CLR released; pulse has not been emitted.
    for _ in range(2):
        s.receive(external_receive(s.issue()))
    queued = s.issue()  # HIGH command may already have an irreversible effect!
    if kind == "cancel":
        s.model.cancel()
    else:
        s.model.lose("EXTERNAL_RECEIVING_EVIDENCE_LOST")
    denials = []
    for attempt in (lambda: s.receive(external_receive(queued)),
                    lambda: s.commit_rejoin(p), lambda: s.model.prepare_rearm(p)):
        try:
            attempt()
        except Denied as error:
            denials.append(str(error))
        else:
            raise AssertionError("stale authorization revived")
    interrupted = s.snapshot()
    # Genuinely fresh recovery after requalified active hold. Not always OFF.
    hold(s, "recover")
    rejoin(s, "new-after-" + kind)
    useful(s, "useful-after-" + kind)
    return pack(s, kind, "REFUSED_STALE_THEN_FRESH_SYNTHETIC_SERVICE",
                denials=denials, interrupted=interrupted)


def bad_order():
    traces = [adverse_order("clear_first"), adverse_order("clock_first"),
              adverse_order("clear_first", qualified=False)]
    assert [t["ff_q_symbolic"] for t in traces] == [HIGH, LOW, UNKNOWN]
    return {
        "scenario": "bad-order", "outcome": "RETAINED_EXECUTABLE_COUNTEREXAMPLE",
        "traces": traces, "actual_operation_permission": False,
        "note": "Unsequenced stale HIGH can set symbolic Q without fresh intent; "
                "ordered commands with UNKNOWN propagation cannot exclude it.",
    }


def stale_high_return():
    s = Sequencer(machine())
    s.begin_hold()
    for _ in range(3):
        s.receive(external_receive(s.issue()))
    command = s.issue()  # OE HIGH after both LOW commands and assumed LOWs
    # The oracle now reports a contrary history (e.g. unqualified propagation,
    # power/retained output). Earlier assumptions do not guarantee continuation.
    contrary = replace(external_receive(command),
                       receiving=Receiving(HIGH, HIGH, HIGH, HIGH, HIGH,
                                           HIGH, HIGH, HIGH))
    s.ack("OE_ENABLE_ACK")
    try:
        s.receive(contrary)
    except Denied as error:
        return pack(s, "stale-high-return", "EXPECTED_REFUSAL_NOT_CONTAINMENT",
                    denial=str(error), adverse=adverse_order("clear_first"),
                    note="Contrary received HIGH invalidates the hypothetical "
                         "normal assumptions. LOW commands/ACK cannot override it.")
    raise AssertionError("stale HIGH accepted as initialized LOW")


SCENARIOS = {
    "normal": normal, "held-request": held_request,
    "stale-high-return": stale_high_return,
    "cancel": lambda: cancel_or_loss("cancel"),
    "evidence-loss": lambda: cancel_or_loss("evidence-loss"),
    "unknown-C": lambda: unknown("C"),
    "unknown-local": lambda: unknown("local"),
    "unknown-output": lambda: unknown("output"),
    "unknown-ACK": lambda: unknown("ACK"),
    "bad-order": bad_order,
}
