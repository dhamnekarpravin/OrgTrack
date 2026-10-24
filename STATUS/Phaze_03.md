# Phase 3 Status: Django Core and Login

**Plan days:** Day 4 and Day 5
**Status:** Done when all tests in section 7 pass
**Next phase:** Phase 4 (Platform accounts)

Save this file inside your `docs` folder: `orgtracker/docs/phase_3_status.md`

---

## 1. What we did in this phase

- Installed `djangorestframework-simplejwt` for login tokens.
- Made two separate logins: one for the Platform website and one for the School/College website.
- Made the first-login rule: a user with a temporary password must change it before using anything else.
- Made permission checks that follow the user's role.
- Made a setup script that creates the first Platform MD and committee.
- Wrote 10 automatic tests.
- Saved the work in Git.

---

## 2. Files made or changed

| File | What it does |
| --- | --- |
| `config/settings.py` | Added `REST_FRAMEWORK` (every page needs login by default) and `SIMPLE_JWT` (token settings) at the bottom |
| `config/urls.py` | Connects `api/auth/` to the `accounts` app |
| `accounts/services.py` | Two helpers: get a user's permission codes, and get a user's role codes |
| `accounts/permissions.py` | The rules: `PasswordChanged`, `IsPlatformPortal`, `IsSchoolPortal`, and `require("code")` |
| `accounts/serializers.py` | Checks the data sent for login, password change, and profile |
| `accounts/views.py` | The login, change password, and profile pages, plus 4 test pages |
| `accounts/urls.py` | The web addresses of those pages |
| `accounts/management/commands/setup_platform.py` | Makes the first MD and committee |
| `accounts/tests.py` | The 10 automatic tests |
| `requirements.txt` | Now includes `djangorestframework-simplejwt` |

---

## 3. Web addresses made in this phase

All addresses start with `http://127.0.0.1:8000/api/auth/`

| Address | Method | Who can use it | What it does |
| --- | --- | --- | --- |
| `platform/login/` | POST | Platform staff only | Sign in on the Platform website |
| `school/login/` | POST | School/College users only | Sign in on the School/College website |
| `refresh/` | POST | Anyone with a refresh token | Gets a new access token |
| `change-password/` | POST | Any signed-in user | Changes the password |
| `me/` | GET, PATCH | Any signed-in user | Shows or updates my own profile |
| `platform/ping/` | GET | Platform token only | Test page. We remove it later. |
| `school/ping/` | GET | School/College token only | Test page. We remove it later. |
| `finance-check/` | GET | Platform token with `finance.view` | Test page. We remove it later. |
| `marks-check/` | GET | Anyone with `student_marks.create` | Test page. We remove it later. |

---

## 4. Workflow

### A. First setup (done once)

1. Run `seed_roles` so the 23 roles and 88 permissions are in the database.
2. Run `setup_platform` with the MD's name and email.
3. The script makes the MD account with the roles `md` and `committee_member`.
4. The script makes any other committee members with the role `committee_member`.
5. Each person gets a **temporary password**. It is shown once on the screen.
6. The script records that the credentials were given on paper (`credential_deliveries`).
7. Every new account is set to `must_change_password = True`.

### B. Login

1. The user types email and password on their website.
2. The Platform website calls `platform/login/`. The School/College website calls `school/login/`.
3. Django checks the email and password. Wrong: `401`.
4. Django checks the user belongs to this website:
   - A platform user (no school) can only use `platform/login/`.
   - A school or college user can only use `school/login/`.
   - Wrong website: `403`.
5. For a school or college user, Django checks the school status is `active`. Not active: `403`.
6. Django makes two tokens and puts the **website name** (`portal`) and the `school_id` inside them.
7. Django sends back the tokens and the user's details: name, roles, permissions, and `must_change_password`.

### C. First login and password change

1. The user signs in with the temporary password.
2. `must_change_password` is `True`, so every page is blocked with `403`, except `me/` and `change-password/`.
3. The user sends the old password and a new one to `change-password/`.
4. Django checks the old password and the strength of the new one (not too short, not too common, not only numbers).
5. Django saves the new password and sets `must_change_password = False`.
6. All pages now open according to the user's role.

### D. What happens on every request

1. Is there a valid token? No: `401`.
2. Has the user changed the temporary password? No: `403`.
3. Does the token's website match the page (Platform page or School/College page)? No: `403`.
4. Does the user have the permission code the page needs? No: `403`.
5. All yes: the page opens.

### E. Which website each user can use

| User | `platform/login/` | `school/login/` |
| --- | --- | --- |
| Platform staff (Owner, committee, admins, HRs, associates) | Works | `403` refused |
| School/College user (Chairman to Parent) | `403` refused | Works |

### F. Refresh and log out

1. The access token lasts **30 minutes**. The refresh token lasts **1 day**.
2. When the access token ends, the website sends the refresh token to `refresh/` and gets a new access token.
3. To log out, the React website deletes both tokens from the browser.

---

## 5. How permission checks work

1. Every action has a code, like `finance.view` or `student_marks.create`.
2. Each role has a list of codes. The `seed_roles` script fills these lists (88 codes in total).
3. A user can have more than one role. Their permissions are all the codes from all their roles.
4. A page asks for a code with `require("code")`. If the user does not have it, they get `403`.

Examples from the tests:

| User role | `finance-check/` | `marks-check/` |
| --- | --- | --- |
| Platform committee member | Works (has `finance.view`) | `403` (no `student_marks.create`) |
| Teacher | Not on this website | Works (has `student_marks.create`) |

---

## 6. Important notes

| Item | Note |
| --- | --- |
| Token contents | The token holds the website name (`portal`) and the `school_id`. The gateway will use this later. |
| `JWT_SECRET` | The tokens are signed with this value from `.env`. If you change it, everyone is signed out. |
| Default rule | Every page needs a login and a changed password, unless it says otherwise. |
| Temporary password | Shown once by `setup_platform`. Save it right away. |
| Blocked users | A user who is inactive, rejected, pending approval, or deleted (`deleted_at` set) cannot sign in. |
| Suspended school | Users of a school that is not `active` cannot sign in. |
| Test pages | `ping`, `finance-check`, and `marks-check` are for testing only. We remove them later. |
| Test database | The tests use a temporary database called `test_orgtracker`. Your real data is not touched. |
| Secrets | Never paste temporary passwords or `.env` in a chat. |
| Not in this phase | Forgot password, account lockout, sending emails, and multi-factor sign-in. Creating the other accounts comes in Phase 4. |

---

## 7. Testing guide

Open the terminal in the `backend` folder. Turn on the virtual environment first (`venv\Scripts\activate`).

### Test 1: Files are there

```powershell
dir accounts
```

**Pass:** you see `models.py`, `views.py`, `urls.py`, `permissions.py`, `serializers.py`, `services.py`, and `tests.py`.
**Fail:** make the missing file again with `ni accounts\file_name.py`, paste the code, and save.

- [ ] Passed

### Test 2: Django check

```powershell
python manage.py check
```

**Pass:** `System check identified no issues`.

- [ ] Passed

### Test 3: The 10 automatic tests

```powershell
python manage.py test accounts
```

**Pass:** `Ran 10 tests` and `OK`. The lines `Done. Roles: 23, Permissions: 88` between the dots are normal.

| Test name | What it proves |
| --- | --- |
| `test_platform_login_works` | A platform user can sign in and gets a token |
| `test_wrong_password_is_refused` | A wrong password gives `401` |
| `test_platform_user_cannot_use_school_login` | A platform user is refused on the school website |
| `test_school_user_cannot_use_platform_login` | A school user is refused on the platform website |
| `test_school_token_cannot_open_platform_page` | A school token cannot open a platform page |
| `test_no_token_is_refused` | No token gives `401` |
| `test_temporary_password_blocks_pages_until_changed` | Pages are blocked until the password is changed |
| `test_weak_new_password_is_refused` | A weak new password is refused |
| `test_permission_check_follows_role` | The page opens only for the right permission |
| `test_user_can_update_own_profile` | A user can change their own name |

- [ ] Passed

### Test 4: First committee was made

```powershell
mysql -u orgtracker_user -p orgtracker -e "SELECT u.email, r.code FROM users u JOIN user_roles ur ON ur.user_id=u.id JOIN roles r ON r.id=ur.role_id;"
```

**Pass:** you see your email with the roles `md` and `committee_member`.
**Fail:** if the list is empty, run `setup_platform` (see section 4A).

- [ ] Passed

### Test 5: Try it by hand

Start the server:

```powershell
python manage.py runserver
```

Open a **second** PowerShell window. Use your own email and temporary password.

**a) Sign in on the Platform website:**
```powershell
$body = @{ email = "you@example.com"; password = "TEMP_PASSWORD" } | ConvertTo-Json
$r = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/auth/platform/login/ -Body $body -ContentType "application/json"
$r.user
```
**Pass:** you see your name, the roles `md` and `committee_member`, and `must_change_password : True`.

**b) Try a page before changing the password:**
```powershell
$h = @{ Authorization = "Bearer $($r.access)" }
try { Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/finance-check/ -Headers $h } catch { $_.ErrorDetails.Message }
```
**Pass:** `You must change your password first.`

**c) Change the password:**
```powershell
$p = @{ old_password = "TEMP_PASSWORD"; new_password = "MyNewPass#2026" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/auth/change-password/ -Headers $h -Body $p -ContentType "application/json"
```
**Pass:** `Password changed.` Use your own new password.

**d) Try the pages again:**
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/finance-check/ -Headers $h
try { Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/marks-check/ -Headers $h } catch { $_.ErrorDetails.Message }
```
**Pass:** the first shows `You can view finance.` The second shows `You do not have permission for this action.`

**e) Try the School/College website with the same account:**
```powershell
$body2 = @{ email = "you@example.com"; password = "MyNewPass#2026" } | ConvertTo-Json
try { Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/auth/school/login/ -Body $body2 -ContentType "application/json" } catch { $_.ErrorDetails.Message }
```
**Pass:** `This account cannot sign in on this website.`

Stop the server with `Ctrl + C`.

- [ ] Passed (a to e)

### Test 6: Git

```powershell
cd ..
git status
git log --oneline
```

**Pass:** `.env` and `venv` do not show in `git status`, and `git log` shows `Phase 3: login and permissions`.
**Fail:** if the commit is missing, run `git add .` and `git commit -m "Phase 3: login and permissions"`.

- [ ] Passed

---

## 8. Common problems

| Problem | What to do |
| --- | --- |
| Tests show `404` everywhere | The web addresses are not connected. Check `config/urls.py` and `accounts/urls.py`. Both must be saved and in the right folders. |
| `No module named 'accounts.services'` | The file `accounts/services.py` is missing or has the wrong name. Check with `dir accounts` and make sure it does not end with `.txt`. |
| `No module named 'rest_framework_simplejwt'` | Turn on `(venv)` and run `pip install djangorestframework-simplejwt`. |
| `Roles are missing` | Run `python manage.py seed_roles` first. |
| Tests say `Access denied ... test_orgtracker` | In MySQL as root run: ``GRANT ALL PRIVILEGES ON `test_orgtracker`.* TO 'orgtracker_user'@'localhost'; FLUSH PRIVILEGES;`` |
| `401` on every page by hand | The header must be `Bearer`, a space, then the token. |
| Temporary password lost | Ask the MD to reset it. For now, set a new one in the Django shell: `python manage.py changepassword you@example.com`. Then set `must_change_password` to `True` again if you want to test the rule. |
| `Ran 9 tests` instead of 10 | One test is missing from `tests.py`. Paste the file again. |

---

## 9. Phase 3 is complete when

- [ ] `python manage.py check` shows no issues
- [ ] `python manage.py test accounts` shows `Ran 10 tests` and `OK`
- [ ] The first MD and committee exist in the database
- [ ] The hand tests (a to e) give the results shown
- [ ] `.env` and `venv` are not in Git
- [ ] The commit `Phase 3: login and permissions` is saved

---

## 10. Next: Phase 4 (Platform accounts)

In Phase 4 we will:

- Add pages for the MD to add, edit, and delete committee members and the Owner.
- Add pages for the Owner to manage Platform Admins.
- Add pages for the Onboarding Admin to manage HRs, and for the Associate Manager HR to manage associates.
- Add the approval flow, where the Approvals Admin accepts or rejects new HRs and associates.
- Save every credential delivery and every change in the audit log.

Before you start, check that Phase 3 passes all the tests above.