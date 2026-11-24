import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unittest
from main import audit

def row(workstation, user, admin, days):
    return {"workstation": workstation, "user": user, "admin": admin,
            "last_login_days": str(days)}

class TestLocalAdminAuditor(unittest.TestCase):
    def test_shared_admin(self):
        rows = [row("WS-01", "admin", "yes", 2), row("WS-02", "admin", "yes", 5),
                row("WS-03", "admin", "yes", 1)]
        r, skipped = audit(rows)
        self.assertEqual(r[0][2], "SHARED ADMIN")
        self.assertIn("3 workstation(s)", r[0][3])
        self.assertEqual(skipped, 0)

    def test_two_workstations_is_not_shared(self):
        rows = [row("WS-01", "admin", "yes", 2), row("WS-02", "admin", "yes", 5)]
        r, _ = audit(rows)
        self.assertEqual(r[0][2], "ADMIN")

    def test_stale_admin(self):
        r, _ = audit([row("WS-01", "oldadmin", "yes", 120)])
        self.assertEqual((r[0][2], r[0][3]), ("STALE ADMIN", "no login for 120 day(s)"))

    def test_exactly_90_days_is_not_stale(self):
        r, _ = audit([row("WS-01", "oldadmin", "yes", 90)])
        self.assertEqual(r[0][2], "ADMIN")

    def test_not_admin(self):
        r, _ = audit([row("WS-01", "ayesha", "no", 1)])
        self.assertEqual((r[0][2], r[0][3]), ("NOT ADMIN", "standard user"))

    def test_shared_beats_stale(self):
        rows = [row("WS-01", "admin", "yes", 200), row("WS-02", "admin", "yes", 200),
                row("WS-03", "admin", "yes", 200)]
        r, _ = audit(rows)
        self.assertEqual(r[0][2], "SHARED ADMIN")

    def test_invalid_row_is_skipped_and_counted(self):
        rows = [row("WS-01", "admin", "yes", "soon"),
                row("WS-02", "ayesha", "no", 1)]
        r, skipped = audit(rows)
        self.assertEqual((len(r), skipped), (1, 1))
        self.assertEqual(r[0][1], "ayesha")

    def test_empty_input(self):
        self.assertEqual(audit([]), ([], 0))
