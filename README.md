# workstation-local-admin-auditor

Audit local administrator accounts on workstations: the input CSV lists workstation, user, admin (yes/no) and last_login_days — SHARED ADMIN when the same admin user holds local admin rights on 3 or more workstations (a stolen password spreads far), STALE ADMIN when an admin has not logged in for over 90 days, ADMIN for an active local admin, NOT ADMIN for a standard user — SHARED ADMIN first, then STALE ADMIN, then ADMIN, then NOT ADMIN. Rows with a missing column or a non-numeric last_login_days are reported as skipped, not silently dropped.

Sample input is included (sample.csv with seven accounts, one invalid row).

## How to run

```sh
python3 main.py sample.csv
```

## Example output

```
WS-01 admin: SHARED ADMIN - local admin on 3 workstation(s)
WS-02 admin: SHARED ADMIN - local admin on 3 workstation(s)
WS-03 admin: SHARED ADMIN - local admin on 3 workstation(s)
WS-04 oldadmin: STALE ADMIN - no login for 120 day(s)
WS-01 ayesha: NOT ADMIN - standard user
WS-02 bilal: NOT ADMIN - standard user
3 shared admin(s), 1 stale admin(s), 0 active admin(s), 2 standard user(s) out of 6 account(s).
Skipped 1 invalid row(s).
```

Standard library only. Run the tests with `python3 -m unittest discover`.
