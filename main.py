"""Audit local administrator accounts on workstations.

Usage: python3 main.py admins.csv
CSV columns: workstation,user,admin,last_login_days.
admin is yes or no; last_login_days is how many days ago the
account last logged in. Verdicts:
- SHARED ADMIN: the same admin user holds local admin rights
  on 3 or more workstations (a stolen password spreads far).
- STALE ADMIN: an admin who has not logged in for over 90 days.
- ADMIN: an active local admin.
- NOT ADMIN: a standard user.
SHARED ADMIN first, then STALE ADMIN, then ADMIN, then
NOT ADMIN; within a verdict by workstation, then user.
Rows with a missing column or a non-numeric last_login_days
are reported as skipped, not silently dropped.
"""
import argparse, csv, sys

VERDICT_ORDER = {"SHARED ADMIN": 0, "STALE ADMIN": 1, "ADMIN": 2, "NOT ADMIN": 3}
SHARED_THRESHOLD = 3
STALE_DAYS = 90

def audit(rows):
    admin_counts = {}
    parsed = []
    skipped = 0
    for row in rows:
        try:
            workstation = row["workstation"].strip()
            user = row["user"].strip()
            admin = row["admin"].strip().lower()
            days = int(row["last_login_days"])
            if admin not in ("yes", "no") or not workstation or not user:
                raise ValueError("bad value")
        except (KeyError, AttributeError, ValueError, TypeError):
            skipped += 1
            continue
        parsed.append((workstation, user, admin == "yes", days))
        if admin == "yes":
            admin_counts[user] = admin_counts.get(user, 0) + 1
    out = []
    for workstation, user, is_admin, days in parsed:
        if not is_admin:
            verdict, detail = "NOT ADMIN", "standard user"
        elif admin_counts[user] >= SHARED_THRESHOLD:
            verdict = "SHARED ADMIN"
            detail = (f"local admin on {admin_counts[user]} workstation(s)")
        elif days > STALE_DAYS:
            verdict = "STALE ADMIN"
            detail = f"no login for {days} day(s)"
        else:
            verdict, detail = "ADMIN", f"last login {days} day(s) ago"
        out.append((workstation, user, verdict, detail))
    out.sort(key=lambda r: (VERDICT_ORDER[r[2]], r[0], r[1]))
    return out, skipped

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args = parser.parse_args(argv)
    with open(args.path, newline="", encoding="utf-8") as f:
        results, skipped = audit(list(csv.DictReader(f)))
    for workstation, user, verdict, detail in results:
        print(f"{workstation} {user}: {verdict} - {detail}")
    counts = {v: sum(1 for *_, verdict, _ in results if verdict == v)
              for v in VERDICT_ORDER}
    print(f"{counts['SHARED ADMIN']} shared admin(s), "
          f"{counts['STALE ADMIN']} stale admin(s), "
          f"{counts['ADMIN']} active admin(s), "
          f"{counts['NOT ADMIN']} standard user(s) out of "
          f"{len(results)} account(s).")
    if skipped:
        print(f"Skipped {skipped} invalid row(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
