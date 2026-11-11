"""Synthetic software tests, not evidence of live router compliance."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("cis_ios", Path(__file__).resolve().parents[1] / "scripts/cis_ios.py")
cis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cis)

GOOD = """hostname R1
ip ssh version 2
no cdp run
service tcp-keepalives-in
service tcp-keepalives-out
line con 0
 exec-timeout 5 0
line aux 0
 no exec
line vty 0 4
 transport input ssh
 exec-timeout 5 0
end
"""
SSH = "SSH Enabled - version 2.0\nAuthentication timeout: 60 secs; Authentication retries: 2"


class FakeConnection:
    def __init__(self, config=GOOD, reject=False):
        self.config, self.reject = config, reject
        self.commands = []
        self.saved = False

    def enable(self):
        pass

    def send_command(self, command):
        self.commands.append(command)
        return {"show version": "Cisco IOS Software, Version 12.4(25d)",
                "show running-config": self.config, "show ip ssh": SSH,
                "show clock": "12:00:00 UTC"}[command]

    def send_config_set(self, commands, **kwargs):
        self.commands.extend(commands)
        if self.reject:
            raise RuntimeError("Rejected")
        self.config = GOOD
        return "OK"

    def check_config_mode(self):
        return False

    def save_config(self):
        self.saved = True
        return "[OK]"

    def disconnect(self):
        pass


class EvaluationTests(unittest.TestCase):
    def test_good(self):
        self.assertEqual(len(cis.evaluate(GOOD, SSH)), 10)
        self.assertTrue(cis.all_pass(cis.evaluate(GOOD, SSH)))

    def test_every_vty_range_checked(self):
        config = GOOD.replace("end", "line vty 5 15\n transport input telnet ssh\n exec-timeout 0 0\nend")
        results = {r["id"]: r for r in cis.evaluate(config, SSH)}
        self.assertEqual(results["1.2.2"]["status"], "FAIL")
        self.assertEqual(results["1.2.9"]["status"], "FAIL")
        self.assertIn("line vty 5 15", results["1.2.2"]["commands"])

    def test_default_and_boundary_timeouts(self):
        for value, expected in [(None, True), ("0 0", False), ("0 30", True),
                                ("10 0", True), ("10 1", False), ("1 60", False)]:
            lines = [] if value is None else [f"exec-timeout {value}"]
            self.assertEqual(cis.timeout_ok({"lines": lines}), expected)

    def test_unknown_ssh_and_missing_aux(self):
        results = {r["id"]: r for r in cis.evaluate(GOOD.replace("line aux 0\n no exec\n", ""), "% Invalid input")}
        self.assertEqual(results["1.2.3"]["status"], "UNKNOWN")
        self.assertEqual(results["2.1.1.1.4"]["status"], "UNKNOWN")

    def test_runtime_ssh_must_match(self):
        result = {r["id"]: r for r in cis.evaluate(GOOD, SSH.replace("2.0", "1.99"))}
        self.assertEqual(result["2.1.1.2"]["status"], "FAIL")

    def test_truncated_config_rejected(self):
        with self.assertRaises(ValueError):
            cis.evaluate(GOOD.replace("end", ""), SSH)

    def test_redaction(self):
        config = GOOD + "username axel secret 5 SECRET\nsnmp-server community PUBLIC RO\ncrypto pki certificate chain TP\n certificate ca 01\n  ABC123\n quit\n!\ninterface Fa0/0\n"
        output = cis.sanitize(config)
        for secret in ("SECRET", "PUBLIC", "ABC123"):
            self.assertNotIn(secret, output)
        self.assertIn("interface Fa0/0", output)

    def run_device(self, connection, mode, connector=None):
        with tempfile.TemporaryDirectory() as directory:
            return cis.process_device({"name": "R1", "host": "10.24.23.1"}, {}, mode, "test",
                                      connector or (lambda **kwargs: connection), Path(directory))

    def test_audit_never_configures_or_saves(self):
        conn = FakeConnection(GOOD.replace("transport input ssh", "transport input telnet ssh"))
        report = self.run_device(conn, "audit")
        self.assertTrue(all(c.startswith("show ") for c in conn.commands))
        self.assertFalse(conn.saved)
        self.assertFalse(report["errors"])

    def test_apply_rechecks_and_saves(self):
        conn = FakeConnection(GOOD.replace("transport input ssh", "transport input telnet ssh"))
        report = self.run_device(conn, "apply")
        self.assertTrue(cis.all_pass(report["after"]))
        self.assertTrue(report["saved"])
        self.assertEqual(conn.commands.count("show running-config"), 2)

    def test_partial_failure_has_post_report_without_save(self):
        conn = FakeConnection(GOOD.replace("no cdp run", "cdp run"), reject=True)
        report = self.run_device(conn, "apply")
        self.assertTrue(report["after"])
        self.assertTrue(report["errors"])
        self.assertFalse(conn.saved)

    def test_failed_reconnect_prevents_save(self):
        conn = FakeConnection()
        calls = []

        def connect(**kwargs):
            calls.append(True)
            if len(calls) > 1:
                raise ConnectionError("Unavailable")
            return conn

        report = self.run_device(conn, "apply", connect)
        self.assertTrue(report["errors"])
        self.assertFalse(conn.saved)

    def test_connection_failure_reported(self):
        def connect(**kwargs):
            raise ConnectionError("Secret must not leak")

        report = self.run_device(None, "audit", connect)
        self.assertTrue(report["errors"])
        self.assertNotIn("Secret must not leak", str(report))


if __name__ == "__main__":
    unittest.main()
