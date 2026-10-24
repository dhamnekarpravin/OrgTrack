# Phase 1 Status: Project Setup

**Plan day:** Day 1
**Status:** Done
**Next phase:** Phase 2 (Database)

Save this file inside your `docs` folder: `orgtracker/docs/phase_1_status.md`

---

## 1. What we did in this phase

- Checked that all the tools are installed.
- Made the main folder `orgtracker` and the small folders inside it.
- Made the empty files.
- Started Git.
- Filled `.gitignore`, `.env.example`, and `README.md`.
- Made the real `.env` file with our own passwords and secret keys.
- Saved the first commit in Git.

---

## 2. Final folder list

```text
orgtracker/
├── platform-web/    website for OrgTracker staff
├── school-web/      website for schools and colleges
├── shared-ui/       parts used by both websites
├── gateway/         Spring Boot gateway
├── backend/         Django backend
├── ai-service/      FastAPI chatbot
├── database/        MySQL scripts
├── docker/          Docker files
├── docs/            notes and documents
├── docker-compose.yml
├── .env.example
├── .env             (secret, never saved in Git)
├── .gitignore
└── README.md
```

---

## 3. Important notes

| Item | Note |
| --- | --- |
| `.env` | Has our real passwords and secret keys. Never share it. Never save it in Git. |
| `.env.example` | A sample file. It has no real passwords, so it is safe in Git. |
| `.gitignore` | Tells Git which files to skip. `.env` must be the first line. |
| `MYSQL_PASSWORD` and `MYSQL_ROOT_PASSWORD` | Two different passwords. Do not forget them, we need them in Phase 2. |
| `DJANGO_SECRET_KEY` and `JWT_SECRET` | Two different long random texts. |
| `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` | Empty for now. We fill them in the AI phase. |
| If `.env` is saved in Git by mistake | Change every password and key inside it. Git keeps the old version. |

---

## 4. Testing guide

Open the terminal inside the `orgtracker` folder and do each test. Tick the box when it passes.

### Test 1: Tools are installed

```bash
git --version
python --version
node --version
java --version
mysql --version
docker --version
```

*On a Mac, use `python3` if `python` does not work.*

**Pass:** each line shows a version number.
**Fail:** an error means that tool is not installed. Install it first.

- [ ] Passed

### Test 2: All folders are there

Mac or Linux:
```bash
ls
```

Windows (PowerShell):
```powershell
dir
```

**Pass:** you see `platform-web`, `school-web`, `shared-ui`, `gateway`, `backend`, `ai-service`, `database`, `docker`, `docs`.
**Fail:** a folder is missing. Make it with `mkdir folder_name`.

- [ ] Passed

### Test 3: All files are there

Mac or Linux:
```bash
ls -a
```

Windows (PowerShell):
```powershell
dir -Force
```

**Pass:** you see `docker-compose.yml`, `.env.example`, `.env`, `.gitignore`, `README.md`, and `.git`.
**Fail:** a file is missing. Make it again with Step 4 or Step 8 of Phase 1.

- [ ] Passed

### Test 4: Git is working

```bash
git log --oneline
```

**Pass:** you see one line that says `Phase 1: project folders`.
**Fail:** if you see an error like "does not have any commits", run `git add .` and then `git commit -m "Phase 1: project folders"`.

- [ ] Passed

### Test 5: `.env` is hidden from Git

```bash
git status
git check-ignore .env
```

**Pass:** `git status` does not list `.env`, and `git check-ignore .env` prints `.env`.
**Fail:** if `.env` shows up, open `.gitignore`, make sure `.env` is on the first line, and save.

- [ ] Passed

### Test 6: `.env` has real values

Mac or Linux:
```bash
grep -E "change_me|type_your|paste_" .env
```

Windows (PowerShell):
```powershell
Select-String -Pattern "change_me|type_your|paste_" .env
```

**Pass:** nothing is printed. That means no sample text is left.
**Fail:** the lines printed still have sample text. Open `.env` and put real values in those lines.

- [ ] Passed

### Test 7: `.env.example` has no real secrets

Open `.env.example` in your editor.

**Pass:** it shows only sample text like `change_me`.
**Fail:** if you see a real password or key, replace it with sample text, save, and commit again.

- [ ] Passed

---

## 5. Common problems

| Problem | What to do |
| --- | --- |
| `python` not found | On a Mac or Linux use `python3`. On Windows, install Python and tick "Add to PATH". |
| `mysql` not found | Install MySQL 8, or add its folder to PATH. |
| `docker` not found | Install Docker Desktop and start it. |
| `.env` shows in `git status` | Add `.env` to the first line of `.gitignore`. |
| Command `ni` not working | Use PowerShell, not the old Command Prompt. |

---

## 6. Phase 1 is complete when

- [ ] All 7 tests pass
- [ ] The folder list matches section 2
- [ ] `.env` is not in Git
- [ ] The first commit is saved

---

## 7. Next: Phase 2 (Database)

In Phase 2 we will:

- Start MySQL.
- Create the Django project in the `backend` folder.
- Make the 38 tables.
- Add the starting roles and permissions.

Before you start, check that MySQL is running and keep your `.env` file open.