"""Synthetic CLI fixtures. No real provider calls, auth reads, or spending."""
import importlib.util
import json
import os
from pathlib import Path
import stat
import signal
import subprocess
import time
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("terminal_review", ROOT / "scripts/terminal_review.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def review(snapshot="snapshot"):
    return dict(snapshot_id=snapshot, findings=[], coverage="full", inspected=["inline packet"],
                checked=["requirements"], open_question="None")


@unittest.skipUnless(os.name == "posix", "Process-group tests need POSIX")
class TerminalReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        r.STOP.clear()
        self.addCleanup(r.STOP.clear)

    def executable(self, body):
        path = self.root / "fake-cli"
        path.write_text("#!" + sys.executable + "\nimport sys\n"
                        "if '--version' in sys.argv:\n    print('2.1.292'); raise SystemExit(0)\n"
                        "if sys.argv[-2:] == ['features', 'list']:\n    print(" +
                        repr("\n".join(f + " stable false" for f in r.CODEX_FEATURES)) + "); raise SystemExit(0)\n" + body)
        path.chmod(stat.S_IRWXU)
        return str(path)

    def test_environment_retains_auth_locations_without_api_or_parent_overrides(self):
        env = r.child_environment({"HOME": "/test", "PATH": "/bin", "CODEX_HOME": "/codex",
                                   "CLAUDE_CONFIG_DIR": "/claude", "ANTHROPIC_API_KEY": "secret",
                                   "OPENAI_API_KEY": "secret", "CODEX_API_KEY": "secret",
                                   "CLAUDE_CODE_USE_BEDROCK": "1", "ANTHROPIC_BASE_URL": "api",
                                   "CLAUDE_CODE_OAUTH_TOKEN": "secret", "CLAUDECODE": "parent"})
        self.assertEqual(env, {"HOME": "/test", "PATH": "/bin", "CODEX_HOME": "/codex", "CLAUDE_CONFIG_DIR": "/claude"})

    def test_probe_requires_subscription_and_does_not_echo_account_or_key(self):
        payload = {"loggedIn": True, "authMethod": "api_key", "apiProvider": "firstParty", "email": "private@test"}
        executable = self.executable("print(" + repr(json.dumps(payload)) + ")")
        with patch.object(r.shutil, "which", return_value=executable):
            outcome = r.probe("claude", r.child_environment(), self.root)
        self.assertFalse(outcome["ready"])
        self.assertEqual(outcome["reason"], "subscription_login_required")
        self.assertNotIn("private@test", json.dumps(outcome))
        self.assertNotIn("api_key", json.dumps(outcome))

    def test_claude_subscription_probe_and_codex_api_key_probe(self):
        executable = self.executable('print(\'{"loggedIn":true,"authMethod":"claude.ai","apiProvider":"firstParty"}\')')
        with patch.object(r.shutil, "which", return_value=executable):
            self.assertTrue(r.probe("claude", r.child_environment(), self.root)["ready"])
        executable = self.executable('print("Logged in using an API key: synthetic")')
        with patch.object(r.shutil, "which", return_value=executable):
            self.assertFalse(r.probe("codex", r.child_environment(), self.root)["ready"])

    def test_missing_cli_does_not_launch_anything(self):
        with patch.object(r.shutil, "which", return_value=None), patch.object(r, "execute") as execute:
            self.assertEqual(r.probe("codex", {}, self.root)["reason"], "missing_cli")
            execute.assert_not_called()

    def test_quota_flag_on_zero_exit_is_a_failed_review(self):
        stdout = json.dumps({"type": "result", "subtype": "success", "is_error": True,
                             "result": "You've hit your monthly spend limit"})
        with self.assertRaisesRegex(RuntimeError, "provider_limit"):
            r.parse_result("claude", {"stdout": stdout}, self.root, "snapshot")

    def test_claude_object_and_array_outputs_validate_without_guessing_model(self):
        wrapper = dict(type="result", subtype="success", is_error=False, result=json.dumps(review()))
        for value in [wrapper, [dict(type="system", subtype="init"), wrapper]]:
            got, models = r.parse_result("claude", {"stdout": json.dumps(value)}, self.root, "snapshot")
            self.assertEqual(got, review())
            self.assertEqual(models, [])

    def test_denied_tool_attempt_is_not_accepted_as_packet_only_review(self):
        wrapper = dict(type="result", subtype="success", is_error=False, result=json.dumps(review()),
                       permission_denials=[{"tool_name": "Bash"}])
        with self.assertRaises(ValueError):
            r.parse_result("claude", {"stdout": json.dumps(wrapper)}, self.root, "snapshot")

    def test_wrong_snapshot_empty_inspection_and_malformed_finding_fail(self):
        for value in [review("other"), dict(review(), inspected=[]), dict(review(), findings=[{}])]:
            with self.assertRaises(ValueError):
                r.validate_review(value, "snapshot")

    def test_codex_tool_execution_and_failure_events_are_rejected(self):
        (self.root / "review.json").write_text(json.dumps(review()))
        for event in [dict(type="item.completed", item={"type": "command_execution"}), dict(type="turn.failed")]:
            with self.assertRaises(ValueError):
                r.parse_result("codex", {"stdout": json.dumps(event)}, self.root, "snapshot")

    def test_completed_codex_result_requires_final_json(self):
        with self.assertRaises(FileNotFoundError):
            r.parse_result("codex", {"stdout": '{"type":"turn.completed"}'}, self.root, "snapshot")
        (self.root / "review.json").write_text(json.dumps(review()))
        got, models = r.parse_result("codex", {"stdout": '{"type":"turn.completed"}'}, self.root, "snapshot")
        self.assertEqual(got, review())
        self.assertEqual(models, [])

    def test_disabled_code_mode_startup_notice_is_not_a_failed_turn(self):
        notice = {"type": "item.completed", "item": {"type": "error", "message":
                  "Code Mode is unavailable because code-mode host is disabled. Code mode will fail closed."}}
        (self.root / "review.json").write_text(json.dumps(review()))
        events = [notice, {"type": "turn.started"}, {"type": "turn.completed"}]
        got, _ = r.parse_result("codex", {"stdout": "\n".join(map(json.dumps, events))}, self.root, "snapshot")
        self.assertEqual(got, review())
        events = [{"type": "turn.started"}, notice]
        with self.assertRaises(ValueError):
            r.parse_result("codex", {"stdout": "\n".join(map(json.dumps, events))}, self.root, "snapshot")

    def test_deadline_terminates_a_real_process(self):
        executable = self.executable("import time\ntime.sleep(30)")
        outcome = r.execute([executable], self.root / "call", r.child_environment(), 0.15)
        self.assertEqual(outcome["status"], "timed_out")
        self.assertTrue(outcome["cleanup_confirmed"])
        self.assertIsNotNone(outcome["returncode"])
        self.assertLess(outcome["duration_seconds"], 5)

    def test_children_are_stopped_when_the_cli_leader_exits(self):
        marker = self.root / "orphan-kept-running"
        executable = self.executable("import os,signal,time\nfrom pathlib import Path\n"
            "if os.fork() == 0:\n    signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "    time.sleep(1.5)\n    Path(" + repr(str(marker)) + ").touch()\n    os._exit(0)\n"
            "os._exit(0)\n")
        outcome = r.execute([executable], self.root / "call", r.child_environment(), 5)
        time.sleep(1.6)
        self.assertFalse(marker.exists())
        self.assertIn(outcome["status"], ["finished", "cleanup_unconfirmed"])

    def test_cancel_event_terminates_a_real_process(self):
        executable = self.executable("import time\ntime.sleep(30)")
        r.STOP.set()
        outcome = r.execute([executable], self.root / "call", r.child_environment(), 30)
        self.assertEqual(outcome["status"], "cancelled")
        self.assertTrue(outcome["cleanup_confirmed"])

    def test_output_limit_is_checked_even_when_cli_exits_quickly(self):
        executable = self.executable('print("x" * 1000)')
        with patch.object(r, "MAX_OUTPUT_BYTES", 50):
            outcome = r.execute([executable], self.root / "call", r.child_environment(), 5)
        self.assertEqual(outcome["status"], "output_limit")
        self.assertLessEqual(len(outcome["stdout"]), 50)

    def test_codex_final_json_without_completed_turn_is_not_success(self):
        (self.root / "review.json").write_text(json.dumps(review()))
        with self.assertRaises(ValueError):
            r.parse_result("codex", {"stdout": '{"type":"turn.started"}'}, self.root, "snapshot")

    def test_work_is_stdin_data_and_artifacts_are_private(self):
        marker = self.root / "must-not-exist"
        payload = '$(touch "' + str(marker) + '")'
        executable = self.executable("import sys\nprint(sys.stdin.read())")
        result = r.execute([executable], self.root / "call", r.child_environment(), 5, payload)
        self.assertIn(payload, result["stdout"])
        self.assertFalse(marker.exists())
        for p in (self.root / "call").iterdir():
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.root / "call").stat().st_mode & 0o777, 0o700)

    def test_unavailable_seat_never_dispatches(self):
        with patch.object(r, "execute") as execute:
            result = r.run_seat(1, r.parse_seat("claude"), {"ready": False, "reason": "missing_cli"},
                                {}, "snapshot", "security", self.root, {}, 5)
            self.assertEqual(result["status"], "unavailable")
            self.assertEqual(json.loads((self.root / "seat-1/result.json").read_text()), result)
            execute.assert_not_called()

    def test_packet_is_complete_hashed_and_not_truncated(self):
        path = self.root / "packet.json"
        packet = dict(goal="review", decisions=[], author_models=["unknown"], work="full target")
        path.write_text(json.dumps(packet))
        got, first = r.load_packet(path)
        self.assertEqual(got, packet)
        packet["work"] += " changed"
        path.write_text(json.dumps(packet))
        self.assertNotEqual(first, r.load_packet(path)[1])
        packet["work"] = "x" * r.MAX_PACKET_CHARS
        path.write_text(json.dumps(packet))
        with self.assertRaises(ValueError):
            r.load_packet(path)

    def test_model_cannot_be_a_cli_flag_and_rebuttal_keeps_snapshot(self):
        with self.assertRaises(ValueError):
            r.parse_seat("claude:--dangerously-skip-permissions")
        prompt = r.reviewer_prompt(dict(goal="goal", decisions=[], author_models=["unknown"], work="target"),
                                   "snapshot", "correctness", "prior finding")
        self.assertIn('"snapshot_id": "snapshot"', prompt)
        self.assertIn("<untrusted_rebuttal_context>\nprior finding", prompt)

    def test_old_cli_is_blocked_before_authentication_or_inference(self):
        executable = self.root / "old-cli"
        marker = self.root / "must-not-dispatch"
        executable.write_text("#!" + sys.executable + "\nimport sys\nfrom pathlib import Path\n"
                              "if sys.argv[1:] == ['--version']:\n    print('codex-cli 0.159.0')\n"
                              "else:\n    Path(" + repr(str(marker)) + ").touch()\n")
        executable.chmod(0o700)
        outcome = r.probe("codex", r.child_environment(), self.root, str(executable))
        self.assertEqual(outcome["reason"], "unsupported_cli")
        self.assertEqual(outcome["version"], "0.159.0")
        self.assertFalse(marker.exists())

    def test_cli_with_ignored_safety_feature_is_blocked_before_inference(self):
        executable = self.root / "incompatible-cli"
        marker = self.root / "must-not-dispatch"
        executable.write_text("#!" + sys.executable + "\nimport sys\nfrom pathlib import Path\n"
            "if sys.argv[1:] == ['--version']:\n    print('codex-cli 0.160.1')\n"
            "elif sys.argv[-2:] == ['features','list']:\n    print('shell_tool stable true')\n"
            "else:\n    Path(" + repr(str(marker)) + ").touch()\n")
        executable.chmod(0o700)
        outcome = r.probe("codex", r.child_environment(), self.root, str(executable))
        self.assertEqual(outcome["reason"], "unsupported_cli_controls")
        self.assertFalse(marker.exists())

    def test_large_raw_packet_and_final_file_are_bounded(self):
        path = self.root / "large.json"
        path.write_text(" " * 100)
        with patch.object(r, "MAX_INPUT_BYTES", 50), self.assertRaises(ValueError):
            r.load_packet(path)
        (self.root / "review.json").write_text(json.dumps(review()))
        with patch.object(r, "MAX_OUTPUT_BYTES", 50), self.assertRaises(ValueError):
            r.parse_result("codex", {"stdout": '{"type":"turn.completed"}'}, self.root, "snapshot")

    def test_cli_file_output_is_part_of_output_budget(self):
        destination = self.root / "large-output.json"
        executable = self.executable("from pathlib import Path\nPath(" + repr(str(destination)) + ").write_text('x'*1000)")
        with patch.object(r, "MAX_OUTPUT_BYTES", 50):
            outcome = r.execute([executable], self.root / "call", r.child_environment(), 5,
                                output_paths=(destination,))
        self.assertEqual(outcome["status"], "output_limit")
        self.assertTrue(outcome["cleanup_confirmed"])

    def test_bom_and_plain_json_fence_preserve_review_and_reject_noise(self):
        for text in ["\ufeff" + json.dumps(review()), "```\n" + json.dumps(review()) + "\n```"]:
            self.assertEqual(r.decode_json(text), review())
        with self.assertRaises(ValueError):
            r.decode_json("log noise\n" + json.dumps(review()))
        with self.assertRaises(ValueError):
            r.parse_result("claude", {"stdout": '[null]'}, self.root, "snapshot")

    def fake_subscription_cli(self, provider, delay=0):
        executable = self.root / (provider + " cli with spaces")
        auth = "Logged in using ChatGPT" if provider == "codex" else json.dumps(
            dict(loggedIn=True, authMethod="claude.ai", apiProvider="firstParty"))
        version = "codex-cli 0.160.1" if provider == "codex" else "2.1.292 (Claude Code)"
        body = ("import sys,json,re,time\nfrom pathlib import Path\n"
                "if sys.argv[1:] == ['--version']:\n    print(" + repr(version) + "); raise SystemExit(0)\n"
                "if sys.argv[-2:] == ['features','list']:\n    print(" + repr("\n".join(f + " stable false" for f in r.CODEX_FEATURES)) + "); raise SystemExit(0)\n"
                "if sys.argv[1:] in [['login','status'], ['auth','status']]:\n    print(" + repr(auth) + "); raise SystemExit(0)\n"
                "text=sys.stdin.read()\ntime.sleep(" + repr(delay) + ")\n"
                "snapshot=re.search(r'\"snapshot_id\": \"([^\"]+)\"', text).group(1)\n"
                "value=" + repr(review()) + "\nvalue['snapshot_id']=snapshot\n")
        if provider == "codex":
            body += ("Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text(json.dumps(value))\n"
                     "print(json.dumps({'type':'turn.started'}))\nprint(json.dumps({'type':'turn.completed'}))\n")
        else:
            body += "print(json.dumps(dict(type='result', subtype='success', is_error=False, result=json.dumps(value))))\n"
        executable.write_text("#!" + sys.executable + "\n" + body)
        executable.chmod(0o700)
        return executable

    def panel_command(self, delay=0):
        packet = self.root / "packet.json"
        packet.write_text(json.dumps(dict(goal="review", decisions=[], author_models=["unknown"], work="complete target")))
        return [sys.executable, "-I", str(ROOT / "scripts/terminal_review.py"), "run", "--packet", str(packet),
                "--reviewer", "codex", "--reviewer", "claude",
                "--codex-bin", str(self.fake_subscription_cli("codex", delay)),
                "--claude-bin", str(self.fake_subscription_cli("claude", delay)), "--timeout-seconds", "30"]

    def test_full_panel_works_with_explicit_paths_and_private_durable_manifest(self):
        completed = subprocess.run(self.panel_command(), env=dict(os.environ, PATH="/missing", TMPDIR=str(self.root)),
                                   capture_output=True, text=True, timeout=20)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        started = json.loads(completed.stderr.splitlines()[0])
        manifest = json.loads(completed.stdout)
        self.assertEqual(started["artifacts"], manifest["artifacts"])
        self.assertEqual(manifest["status"], "completed")
        self.assertEqual([v["status"] for v in manifest["results"]], ["completed", "completed"])
        root = Path(manifest["artifacts"])
        self.assertEqual(json.loads((root / "manifest.json").read_text()), manifest)
        self.assertEqual((root / "manifest.json").stat().st_mode & 0o777, 0o600)
        for seat in manifest["results"]:
            self.assertTrue(seat["cleanup_confirmed"])
            self.assertEqual(seat["review"]["snapshot_id"], manifest["snapshot_id"])

    def test_missing_seat_produces_incomplete_manifest_without_losing_completed_seat(self):
        command = self.panel_command()
        command[command.index('--claude-bin') + 1] = str(self.root / 'missing-cli')
        completed = subprocess.run(command, env=dict(os.environ, TMPDIR=str(self.root)),
                                   capture_output=True, text=True, timeout=20)
        self.assertEqual(completed.returncode, 1)
        manifest = json.loads(completed.stdout)
        self.assertEqual(manifest["status"], "incomplete")
        self.assertEqual([v["status"] for v in manifest["results"]], ["completed", "unavailable"])
        self.assertEqual(manifest["results"][1]["reason"], "missing_cli")
        root = Path(manifest["artifacts"])
        self.assertEqual(json.loads((root / 'seat-2/result.json').read_text()), manifest["results"][1])

    def test_sigterm_cancels_full_panel_and_preserves_each_seat_outcome(self):
        process = subprocess.Popen(self.panel_command(delay=30), env=dict(os.environ, TMPDIR=str(self.root)),
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        started = json.loads(process.stderr.readline())
        root = Path(started["artifacts"])
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if all((root / ('seat-' + str(i)) / 'session/stdin.txt').exists() for i in [1, 2]):
                break
            time.sleep(0.05)
        else:
            self.fail("Panel did not start both seats")
        process.send_signal(signal.SIGTERM)
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 1, stderr)
        manifest = json.loads(stdout)
        self.assertEqual(manifest["status"], "cancelled")
        self.assertEqual(len(manifest["results"]), 2)
        self.assertTrue(all(v["status"] == "cancelled" and v["cleanup_confirmed"] for v in manifest["results"]))
        self.assertEqual(json.loads((root / 'manifest.json').read_text()), manifest)


if __name__ == "__main__":
    unittest.main()
