"""Targeted stdlib author tests. Not an independent or physical verdict."""
from dataclasses import replace
from pathlib import Path
import runpy
import unittest

_modules = runpy.run_path(str(Path(__file__).with_name("cli.py")))["_load_public"]()
for _name in (
    "base", "Sequencer", "Denied", "Receiving", "LOW", "HIGH", "UNKNOWN", "Z",
    "check_bindings", "symbolic_ff", "adverse_order",
):
    globals()[_name] = getattr(_modules["sequencer"], _name)
for _name in (
    "machine", "external_receive", "external_service_proof", "run_sequence",
    "boot", "hold", "rejoin", "useful", "pending_event", "finish_event", "normal",
    "held_request", "unknown", "cancel_or_loss", "stale_high_return",
):
    globals()[_name] = getattr(_modules["scenarios"], _name)


def staged(kind):
    if kind == "initialize":
        s = Sequencer(machine())
        s.begin_hold()
        return s, None, 12
    if kind == "withdraw":
        s = boot()
        m = s.model
        q = m.make_request("new", "scheduler", "RESET")
        m.capture(q)
        m.freeze()
        m.quiesce(base.EngineReport(
            q, m.owner.generation, q.resources, m.freeze_generation,
            m.accounting_generation, "SYNTHETIC:ENGINE_OBSERVATION", True, True))
        s.begin_hold("withdraw")
        return s, None, 6
    s = Sequencer(machine())
    hold(s)
    p = external_service_proof(s.model, "candidate")
    s.begin_rejoin(p)
    return s, p, 12


class SequencerTests(unittest.TestCase):
    def consumed_proof_boundary(self, boundary, service_id=False):
        """Reconstruct saved FR-SEQ-01; never execute the closed reviewer."""
        s, p, _ = staged("rejoin")
        for _ in range(2):  # X clock LOW, then clear release
            s.receive(external_receive(s.issue()))
        if boundary == "before_receive":
            command = s.issue()
            self.assertEqual(command.stage, "FRESH_CLOCK_HIGH")
        elif boundary == "before_commit":
            run_sequence(s)
        before = s.model.recovery_context()
        if service_id:
            # Synthetic journal contents are mutable model input, not security.
            s.model.journal.service_ids.add(p.request_id)
        else:
            self.assertTrue(s.model.journal.reserve_epoch(p.new_epoch))
        self.assertEqual(before, s.model.recovery_context())
        with self.assertRaisesRegex(Denied, "SERVICE_REPLAY"):
            s.model._service_valid(p)  # diagnostic, no permission consumption
        index = s.index
        command_count = sum(e["action"] == "COMMAND_INTENT_ONLY" for e in s.trace)
        action = (s.issue if boundary == "before_issue" else
                  (lambda: s.receive(external_receive(command)))
                  if boundary == "before_receive" else lambda: s.commit_rejoin(p))
        with self.assertRaisesRegex(Denied, "SERVICE_REPLAY"):
            action()
        self.assertEqual(s.index, index)
        self.assertEqual(sum(e["action"] == "COMMAND_INTENT_ONLY" for e in s.trace),
                         command_count)
        self.assertFalse(s.model.bus_grant)
        self.assertEqual(s.trace[-1]["detail"]["in_flight_physical_effects"], UNKNOWN)
        self.no_actual(s)
        with self.assertRaises(Denied):
            s.issue()
        # Only new cause-bound qualification may recover; not permanent OFF.
        hold(s, "recover")
        rejoin(s, "fresh-" + boundary + ("-service-id" if service_id else "-epoch"))
        useful(s, "useful-after-consumption")
        self.assertTrue(s.snapshot()["synthetic_sequenced_service"])
        self.no_actual(s)

    def test_fr_seq_01_consumed_epoch_before_issue(self):
        self.consumed_proof_boundary("before_issue")

    def test_fr_seq_01_consumed_epoch_before_receive(self):
        self.consumed_proof_boundary("before_receive")

    def test_fr_seq_01_consumed_epoch_before_commit(self):
        self.consumed_proof_boundary("before_commit")

    def test_fr_seq_01_consumed_service_id_at_all_fences(self):
        for boundary in ("before_issue", "before_receive", "before_commit"):
            with self.subTest(boundary=boundary):
                self.consumed_proof_boundary(boundary, service_id=True)

    def test_fr_seq_full_validator_reused_without_early_consumption(self):
        from unittest.mock import patch
        s, p, _ = staged("rejoin")
        with patch.object(s.model, "_service_valid",
                          wraps=s.model._service_valid) as validate:
            for index in range(12):
                s.receive(external_receive(s.issue()))
                self.assertEqual(validate.call_count, 2 * (index + 1))
                self.assertNotIn(p.new_epoch, s.model.journal.epochs)
                self.assertNotIn(p.request_id, s.model.journal.service_ids)
            s.commit_rejoin(p)
            self.assertEqual(validate.call_count, 25)
            self.assertTrue(all(call.args == (p,) for call in validate.call_args_list))
        self.assertIn(p.new_epoch, s.model.journal.epochs)
        self.assertIn(p.request_id, s.model.journal.service_ids)
        useful(s, "useful-after-full-validator")
        self.no_actual(s)

    def no_actual(self, s):
        snap = s.snapshot()
        self.assertIs(snap["actual_operation_permission"], False)
        self.assertIs(snap["actual_bus_permission"], False)
        self.assertIs(snap["physical_disconnection_established"], False)
        self.assertEqual(snap["physical_conductance"], UNKNOWN)
        self.assertEqual(snap["actual_pin_states"], UNKNOWN)
        self.assertEqual(snap["actual_arrival_order"], UNKNOWN)
        self.assertEqual(s.model.now, 0)  # no output ordinal becomes model time

    def test_source_bindings_and_real_model_reuse(self):
        self.assertEqual(len(check_bindings()), 7)
        self.assertEqual(Path(base.__file__), Path(__file__).resolve().with_name("model.py"))
        self.assertIs(type(machine()), base.Model)

    def test_useful_before_and_after_event_not_always_off(self):
        result = normal()
        self.assertTrue(result["final"]["synthetic_sequenced_service"])
        effects = result["final"]["model"]["effects_not_rolled_back"]
        self.assertIn("transaction:useful-before-event:DONE", effects)
        self.assertIn("event:event:new:FIRST_ACTION", effects)
        self.assertIn("transaction:useful-after-event:DONE", effects)
        self.assertFalse(result["final"]["actual_operation_permission"])

    def test_exact_command_order_and_driver_pins(self):
        s = boot()
        commands = [r["detail"]["command"] for r in s.trace
                    if r["action"] == "COMMAND_INTENT_ONLY"]
        for axis in ("X", "Y", "Z"):
            rows = [c for c in commands if c["axis"] == axis]
            self.assertEqual([(c["signal"], c["level"]) for c in rows], [
                ("OE", LOW), ("CLR", LOW), ("CLK", LOW), ("OE", HIGH),
                ("CLK", LOW), ("CLR", HIGH), ("CLK", HIGH), ("CLK", LOW)])
            clr = next(c for c in rows if c["signal"] == "CLR")
            self.assertEqual(clr["driver_pin"], "TDRV_" + axis + ".2")
            self.assertEqual(clr["driver_output_pin"], "TDRV_" + axis + ".13")
            self.assertEqual(clr["receiver_pin"], "FF_" + axis + ".6")
            clk = next(c for c in rows if c["signal"] == "CLK")
            self.assertEqual(clk["driver_output_pin"], "TDRV_" + axis + ".12")
            self.assertEqual(clk["receiver_pin"], "FF_" + axis + ".1")
        self.no_actual(s)

    def test_withdraw_uses_active_clear_not_high_z(self):
        s, _, _ = staged("withdraw")
        start = len(s.trace)
        run_sequence(s)
        commands = [e["detail"]["command"] for e in s.trace[start:]
                    if e["action"] == "COMMAND_INTENT_ONLY"]
        self.assertEqual([(c["signal"], c["level"]) for c in commands],
                         [("CLR", LOW), ("CLK", LOW)] * 3)
        self.assertIsNone(s.model.evidence)
        with self.assertRaises(Denied):
            s.model.authorize()  # FF LOW is not event disconnection proof
        self.no_actual(s)

    def test_commands_and_ack_cannot_advance_receive_fence(self):
        s, _, _ = staged("initialize")
        command = s.issue()
        s.ack()
        self.assertIs(s.pending, command)
        self.assertEqual(s.receiving["X"], Receiving())
        self.assertEqual(s.index, 0)
        with self.assertRaisesRegex(Denied, "AWAITING_EXTERNAL"):
            s.issue()
        self.assertFalse(s.model.bus_grant)
        self.no_actual(s)

    def test_high_z_does_not_become_receiver_low(self):
        s, _, _ = staged("initialize")
        s.receive(external_receive(s.issue()))
        self.assertEqual(s.receiving["X"].driver_clr, Z)
        self.assertEqual(s.receiving["X"].ff_clr, UNKNOWN)
        self.assertEqual(s.receiving["X"].ff_q, UNKNOWN)
        self.no_actual(s)

    def test_power_and_output_unknown_refusals(self):
        for kind in ("C", "local", "output", "ACK"):
            with self.subTest(kind=kind):
                r = unknown(kind)
                self.assertEqual(r["outcome"], "EXPECTED_REFUSAL")
                self.assertFalse(r["final"]["synthetic_sequenced_service"])
                self.assertFalse(r["final"]["model"]["synthetic_bus_grant"])

    def test_missing_qualified_condition_at_every_stage(self):
        for kind in ("initialize", "withdraw", "rejoin"):
            count = 6 if kind == "withdraw" else 12
            for index in range(count):
                s, _, _ = staged(kind)
                for _ in range(index):
                    s.receive(external_receive(s.issue()))
                command = s.issue()
                required = tuple(sorted(s.plan[index].required))
                # Recreate each fixture to avoid testing an already-aborted API.
                for missing in required:
                    with self.subTest(kind=kind, stage=index, missing=missing):
                        t, _, _ = staged(kind)
                        for _ in range(index):
                            t.receive(external_receive(t.issue()))
                        c = t.issue()
                        observation = external_receive(c)
                        with self.assertRaises(Denied):
                            t.receive(replace(observation,
                                              qualified=observation.qualified - {missing}))
                        self.assertFalse(t.model.bus_grant)
                        self.no_actual(t)
                s.interrupt("TEST_END_UNUSED_FIXTURE")

    def test_interrupt_after_every_issued_and_received_stage(self):
        # 30 meaningful stages * 2 boundaries * 3 causes. Issued HIGH is never
        # described as physically recalled, even when its receipt is missing.
        for kind in ("initialize", "withdraw", "rejoin"):
            for index in range(6 if kind == "withdraw" else 12):
                for boundary in ("issued", "received"):
                    for cause in ("cancel", "evidence-loss", "interruption"):
                        with self.subTest(kind=kind, stage=index,
                                          boundary=boundary, cause=cause):
                            s, p, _ = staged(kind)
                            for _ in range(index):
                                s.receive(external_receive(s.issue()))
                            command = s.issue()
                            if boundary == "received":
                                s.receive(external_receive(command))
                            old = s.model.recovery_context()
                            if cause == "cancel" and kind != "initialize":
                                s.model.cancel()
                            elif cause == "evidence-loss":
                                s.model.lose("EXTERNAL_EVIDENCE_LOST")
                            else:
                                s.interrupt(cause)
                            self.assertGreater(s.model.recovery_context().generation,
                                               old.generation)
                            for attempt in (
                                lambda: s.receive(external_receive(command)),
                                s.issue, lambda: s.commit_rejoin(p),
                            ):
                                with self.assertRaises(Denied):
                                    attempt()
                            self.assertFalse(s.model.bus_grant)
                            self.assertFalse(s.snapshot()["synthetic_sequenced_service"])
                            self.no_actual(s)

    def test_preparation_and_actual_rejoin_both_retain_f1_invalidation(self):
        s = Sequencer(machine())
        hold(s)
        old = external_service_proof(s.model, "old")
        s.model.lose("KNOWN_LOSS")
        hold(s, "recover")
        with self.assertRaisesRegex(Denied, "STALE_RECOVERY_CONTEXT"):
            s.begin_rejoin(old)
        self.assertFalse(s.model.bus_grant)
        hold(s, "recover")
        p = external_service_proof(s.model, "fresh")
        s.begin_rejoin(p)
        run_sequence(s)
        s.model.lose("SECOND_SAME_STEP_LOSS")
        with self.assertRaises(Denied):
            s.commit_rejoin(p)
        with self.assertRaises(Denied):
            s.model.prepare_rearm(p)
        hold(s, "recover")
        rejoin(s, "genuinely-new")
        useful(s, "fresh-useful")
        self.assertTrue(s.model.bus_grant)
        self.no_actual(s)

    def test_no_stale_held_snapshot_after_external_loss(self):
        s = Sequencer(machine())
        hold(s)
        s.model.lose("LOSS_AFTER_HOLD")
        fresh = external_service_proof(s.model, "new-proof-but-old-receiving")
        with self.assertRaisesRegex(Denied, "STALE_SEQUENCE"):
            s.begin_rejoin(fresh)
        self.assertFalse(s.model.bus_grant)

    def test_new_hold_cycle_invalidates_old_service_qualification(self):
        s = Sequencer(machine())
        hold(s)
        old = external_service_proof(s.model, "before-repeat-hold")
        hold(s, "recover")
        with self.assertRaisesRegex(Denied, "STALE_RECOVERY_CONTEXT"):
            s.begin_rejoin(old)

    def test_direct_old_model_api_does_not_bypass_new_output_fence(self):
        s, p, _ = staged("rejoin")
        command = s.issue()
        # The base model remains a usable model; it is NOT a security boundary.
        s.model.rejoin(p)
        self.assertTrue(s.model.bus_grant)
        self.assertFalse(s.snapshot()["synthetic_sequenced_service"])
        with self.assertRaisesRegex(Denied, "STALE_SEQUENCE"):
            s.receive(external_receive(command))
        with self.assertRaises(Denied):
            s.require_service()
        self.assertFalse(s.model.bus_grant)
        self.no_actual(s)

    def test_all_actual_rejoin_checks_still_execute(self):
        # No output-complete shortcut: journal changes need not change the base
        # recovery generation, so only the actual existing rejoin validator
        # catches this competing-use case.
        s, p, _ = staged("rejoin")
        run_sequence(s)
        s.model.journal.epochs.add(p.new_epoch)
        with self.assertRaisesRegex(Denied, "SERVICE_REPLAY"):
            s.commit_rejoin(p)
        self.assertFalse(s.model.bus_grant)
        self.no_actual(s)

    def test_public_invalidators_at_each_rejoin_stage(self):
        mutators = {
            "owner_same_generation": lambda m: m.replace_owner(m.owner),
            "topology_same_identity": lambda m: m.replace_topology(m.topology),
            "contact": lambda m: m.contact(False),
            "restart": lambda m: m.restart("restart", continuity_retained=True),
            "bypass": lambda m: m.bypass("debug_probe"),
        }
        for index in range(12):
            for name, mutate in mutators.items():
                with self.subTest(index=index, invalidator=name):
                    s, p, _ = staged("rejoin")
                    for _ in range(index):
                        s.receive(external_receive(s.issue()))
                    c = s.issue()
                    mutate(s.model)
                    with self.assertRaises(Denied):
                        s.receive(external_receive(c))
                    with self.assertRaises(Denied):
                        s.model.prepare_rearm(p)
                    self.assertFalse(s.model.bus_grant)
                    self.no_actual(s)

    def test_expiry_is_logical_only_and_denied(self):
        s, p, _ = staged("rejoin")
        run_sequence(s)
        s.model.advance(1)
        with self.assertRaises(Denied):
            s.commit_rejoin(p)
        self.assertFalse(s.model.bus_grant)
        self.assertFalse(s.snapshot()["actual_operation_permission"])

    def test_held_request_and_fresh_release_protocol_reused(self):
        self.assertEqual(held_request()["denial"], "HELD_OR_UNQUALIFIED_CONTACT")
        s = boot()
        m = s.model
        m.contact(False)
        m.contact(True)
        pending_event(s, "manual")
        finish_event(s)
        with self.assertRaisesRegex(Denied, "MANUAL_RELEASE_REQUIRED"):
            s.begin_rejoin(external_service_proof(m, "still-held"))
        m.contact(False)
        hold(s, "recover")
        rejoin(s, "released-and-qualified")
        useful(s, "manual-fresh-service")
        with self.assertRaises(Denied):
            m.capture(m.make_request("new-id-no-new-press", "manual", "RESET"))
        self.no_actual(s)

    def test_cancel_and_evidence_loss_allow_only_new_qualification(self):
        for kind in ("cancel", "evidence-loss"):
            with self.subTest(kind=kind):
                r = cancel_or_loss(kind)
                self.assertEqual(len(r["denials"]), 3)
                self.assertFalse(r["interrupted"]["synthetic_sequenced_service"])
                self.assertTrue(r["final"]["synthetic_sequenced_service"])
                self.assertFalse(r["final"]["actual_operation_permission"])

    def test_copied_foreign_replayed_and_stale_tickets(self):
        for kind in ("copy", "foreign", "old-cycle", "replay"):
            with self.subTest(kind=kind):
                s, _, _ = staged("initialize")
                c = s.issue()
                if kind == "copy":
                    bad = replace(c)
                elif kind == "foreign":
                    t, _, _ = staged("initialize")
                    bad = t.issue()
                elif kind == "old-cycle":
                    bad = c
                    s.interrupt("CANCEL")
                    s.begin_hold()
                    s.issue()
                else:
                    bad = c
                    s.receive(external_receive(c))
                    s.issue()
                with self.assertRaisesRegex(Denied, "STALE_OR_FOREIGN"):
                    s.receive(external_receive(bad))
                self.assertFalse(s.model.bus_grant)
                self.no_actual(s)

    def test_malformed_public_api_inputs_fail_closed(self):
        for value in (None, {}, "ACK"):
            s, _, _ = staged("initialize")
            s.issue()
            with self.assertRaises(Denied):
                s.receive(value)
            self.assertFalse(s.model.bus_grant)
        s, _, _ = staged("initialize")
        c = s.issue()
        with self.assertRaises(Denied):
            s.receive(replace(external_receive(c), qualified=None))
        for value in (None, "proof"):
            s = Sequencer(machine())
            hold(s)
            with self.assertRaisesRegex(Denied, "MALFORMED_SERVICE_PROOF"):
                s.begin_rejoin(value)
        s = Sequencer(machine())
        hold(s)
        p = replace(external_service_proof(s.model, "malformed"), checks=None)
        with self.assertRaisesRegex(Denied, "MALFORMED_SERVICE_PROOF"):
            s.begin_rejoin(p)
        self.assertFalse(s.model.bus_grant)

    def test_release_or_pulse_state_mismatch_aborts(self):
        for index in (1, 2, 3):
            s, _, _ = staged("rejoin")
            for _ in range(index):
                s.receive(external_receive(s.issue()))
            c = s.issue()
            a = external_receive(c)
            with self.assertRaisesRegex(Denied, "RECEIVING_STATE_NOT_EXPECTED"):
                s.receive(replace(a, receiving=replace(a.receiving, ff_clk=UNKNOWN)))
            self.assertFalse(s.model.bus_grant)
            self.no_actual(s)

    def test_bad_order_executable_not_hidden_or_used_as_success(self):
        a = adverse_order("clear_first")
        b = adverse_order("clock_first")
        c = adverse_order("clear_first", qualified=False)
        self.assertEqual(a["ff_q_symbolic"], HIGH)
        self.assertEqual(b["ff_q_symbolic"], LOW)
        self.assertEqual(c["ff_q_symbolic"], UNKNOWN)
        self.assertFalse(a["fresh_request"])
        self.assertFalse(a["actual_operation_permission"])
        self.assertEqual(a["physical_conductance"], UNKNOWN)
        self.assertEqual(symbolic_ff(LOW, LOW, LOW, HIGH, qualified=True), LOW)
        self.assertEqual(symbolic_ff(LOW, Z, LOW, HIGH, qualified=True), UNKNOWN)
        with self.assertRaises(ValueError):
            adverse_order("guaranteed-by-command-order")

    def test_ordered_commands_cannot_override_stale_high_at_oe_return(self):
        r = stale_high_return()
        self.assertEqual(r["denial"], "RECEIVING_STATE_NOT_EXPECTED")
        self.assertEqual(r["adverse"]["ff_q_symbolic"], HIGH)
        self.assertFalse(r["final"]["synthetic_sequenced_service"])
        self.assertFalse(r["final"]["physical_disconnection_established"])

    def test_early_commit_duplicate_begin_and_wrong_modes_refused(self):
        for count in (0, 1, 2, 3, 11):
            s, p, _ = staged("rejoin")
            for _ in range(count):
                s.receive(external_receive(s.issue()))
            with self.assertRaisesRegex(Denied, "OUTPUT_SEQUENCE_INCOMPLETE"):
                s.commit_rejoin(p)
            self.assertFalse(s.model.bus_grant)
        s, _, _ = staged("initialize")
        with self.assertRaisesRegex(Denied, "SEQUENCE_ALREADY_ACTIVE"):
            s.begin_hold()
        s = Sequencer(machine())
        with self.assertRaisesRegex(Denied, "UNKNOWN_HOLD_MODE"):
            s.begin_hold("assume_safe")
        with self.assertRaises(Denied):
            s.require_service()


if __name__ == "__main__":
    unittest.main(verbosity=2)
