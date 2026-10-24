# Phase 2 Status: Database

**Plan days:** Day 2 and Day 3
**Status:** Done when all tests in section 5 pass
**Next phase:** Phase 3 (Django core and login)

Save this file inside your `docs` folder: `orgtracker/docs/phase_2_status.md`

---

## 1. What we did in this phase

- Made the MySQL database `orgtracker` and the user `orgtracker_user`.
- Made a Python virtual environment inside the `backend` folder.
- Installed Django, Django REST Framework, `mysqlclient`, and `python-dotenv`.
- Started the Django project named `config`.
- Made 8 Django apps.
- Wrote the models for all 38 tables.
- Ran `makemigrations` and `migrate` to make the tables in MySQL.
- Wrote the `seed_roles` script that adds the 23 starting roles and their permissions.
- Saved the work in Git.

---

## 2. Our setup

| Item | Value |
| --- | --- |
| Database | MySQL 8.0.46 (on this computer) |
| Python | 3.14 |
| Django | 5.2 (not the newest) |
| Database name | `orgtracker` |
| Database user | `orgtracker_user` |
| Django project folder | `backend/config` |
| User table | Our own `accounts.User` (set with `AUTH_USER_MODEL`) |

---

## 3. The 8 Django apps and their tables

| App | Tables | Count |
| --- | --- | --- |
| `common` | No tables. It only has the shared base classes. | 0 |
| `accounts` | schools, users, roles, permissions, role_permissions, user_roles, credential_deliveries, approval_requests, audit_logs | 9 |
| `academics` | academic_years, standards, divisions, subjects, school_database_setup | 5 |
| `people` | teachers, parents, students, student_parents, teacher_assignments | 5 |
| `exams` | exam_types, exams, grading_scales, student_marks, student_progress, leaderboard_entries | 6 |
| `operations` | announcements, event_requests, helpdesk_tickets, ticket_comments, meeting_requests | 5 |
| `platform_ops` | revenue_records, system_costs, reports, system_metrics, system_issues, marketing_promotions | 6 |
| `chatbot` | chatbot_conversations, chatbot_messages | 2 |
| **Total** | | **38** |

Django also makes 9 tables of its own, like `django_migrations` and `auth_group`. So MySQL will show about **47 tables** in total.

---

## 4. Important notes

| Item | Note |
| --- | --- |
| `teacher_assignments` | It is in the `people` app, not `academics`. The table is the same. This only avoids a loop between two apps. |
| `AUTH_USER_MODEL` | It must be set in `settings.py` **before** the first `migrate`. If you migrate first, drop the database and start again. |
| Django version | Newest Django needs MySQL 8.4 or later. Our MySQL is 8.0.46, so we use Django 5.2. In the Docker phase we will move to MySQL 8.4. |
| Database password | `.env` and MySQL must have the exact same password. If they differ, you get `Access denied`. |
| Delete | Records are not removed. A delete only sets `deleted_at`. Users, schools, students, teachers, parents, marks, and announcements work this way. |
| IDs | All tables use UUID ids, except the small link tables. |
| `seed_roles` | Safe to run many times. It does not make copies. |
| Roles | 23 in total: 11 platform roles and 12 school/college roles. |
| Secrets | Never paste your `.env` into a chat or a document. If you did, change every password and key in it. |
| Virtual environment | Always turn it on first: `venv\Scripts\activate`. You must see `(venv)` at the start of the line. |

---

## 5. Testing guide

Open the terminal in the `backend` folder. Turn on the virtual environment first. Tick the box when each test passes.

### Test 1: Django check

```powershell
python manage.py check
```

**Pass:** you see `System check identified no issues`.
**Fail:** read the file name and line number in the message. It is usually a typo in a model file.

- [ ] Passed

### Test 2: Django version

```powershell
pip show django
```

**Pass:** the line `Version:` starts with `5.2`.
**Fail:** run `pip install "django>=5.2.8,<5.3"`, then run `pip freeze > requirements.txt`.

- [ ] Passed

### Test 3: Migrations were made and applied

```powershell
python manage.py showmigrations
```

**Pass:** every line has `[X]`, and nothing has `[ ]`.
**Fail:** run `python manage.py migrate`.

- [ ] Passed

### Test 4: Tables are in MySQL

```powershell
mysql -u orgtracker_user -p orgtracker -e "SELECT COUNT(*) AS total_tables FROM information_schema.tables WHERE table_schema='orgtracker';"
```

Type your `MYSQL_PASSWORD` when it asks.

**Pass:** `total_tables` is about **47** (38 ours and 9 from Django).
**Fail:** if it is much lower, run `python manage.py migrate` again.

- [ ] Passed

### Test 5: Check some table names

```powershell
mysql -u orgtracker_user -p orgtracker -e "SHOW TABLES LIKE 'student_marks'; SHOW TABLES LIKE 'schools'; SHOW TABLES LIKE 'chatbot_messages';"
```

**Pass:** each line shows one table name.
**Fail:** if one is missing, check that the app is in `INSTALLED_APPS` and that you named it in `makemigrations`.

- [ ] Passed

### Test 6: Roles are added

```powershell
python manage.py seed_roles
mysql -u orgtracker_user -p orgtracker -e "SELECT scope, COUNT(*) AS total FROM roles GROUP BY scope;"
```

**Pass:** you see `platform 11` and `school 12`.
**Fail:** run `python manage.py seed_roles` again and read any error.

- [ ] Passed

### Test 7: Permissions are added, and no copies are made

Run the script a second time:

```powershell
python manage.py seed_roles
mysql -u orgtracker_user -p orgtracker -e "SELECT COUNT(*) AS roles FROM roles; SELECT COUNT(*) AS permissions FROM permissions; SELECT COUNT(*) AS role_permissions FROM role_permissions;"
```

**Pass:** `roles` is still **23**, and `permissions` and `role_permissions` are both more than 0.
**Fail:** if `roles` is more than 23, you have copies. Tell me before you go on.

- [ ] Passed

### Test 8: Git

```powershell
cd ..
git status
git log --oneline
```

**Pass:** `git status` does not show `.env` or `venv`, and `git log` shows `Phase 2: database and models`.
**Fail:** if `.env` or `venv` shows up, check `.gitignore`. If the commit is missing, run `git add .` and `git commit -m "Phase 2: database and models"`.

- [ ] Passed

---

## 6. Common problems

| Problem | What to do |
| --- | --- |
| `Access denied for user 'orgtracker_user'` | The password in `.env` is different from the one in MySQL. Run `ALTER USER 'orgtracker_user'@'localhost' IDENTIFIED BY 'your_password';` as root, with the same password as `.env`. |
| `MySQL 8.4 or later is required` | Use Django 5.2: `pip install "django>=5.2.8,<5.3"`. |
| `Can't connect to MySQL server` | MySQL is not running. Start the MySQL service. |
| `KeyError: 'DJANGO_SECRET_KEY'` | Django cannot find `.env`. It must be in the `OrgTracker` folder, not in `backend`. |
| `No module named ...` | Turn on the virtual environment, then run `pip install` again. |
| `mysqlclient` does not install | Update pip with `python -m pip install --upgrade pip`, then try again. |
| Error about `AUTH_USER_MODEL` or `accounts.User` | Check `settings.py`. If you migrated before setting it, drop the database and make it again. |

---

## 7. Phase 2 is complete when

- [ ] All 8 tests pass
- [ ] 38 tables of ours are in MySQL
- [ ] There are 23 roles (11 platform and 12 school/college)
- [ ] `.env` and `venv` are not in Git
- [ ] The commit `Phase 2: database and models` is saved

---

## 8. Next: Phase 3 (Django core and login)

In Phase 3 we will:

- Add login with tokens.
- Add separate login rules for the Platform portal and the School/College portal.
- Add the first-login password change.
- Add role and permission checks.
- Add the setup script that makes the first Platform Committee and MD.

Before you start, check that Phase 2 passes all the tests above.