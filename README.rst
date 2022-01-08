internet-speed-monitor
======================
DEVELOPMENT USE in Windows 10
=============================
Initialising Project
--------------------
1. Open terminal in target directory
2. $ pip install poetry
3. $ poetry shell
4. $ poetry install
5. $ pre-commmit run --all-files

GitHub Submission
-----------------
1. Open terminal in project parent directory
2. $ pre-commit run --all-files
    Address any failed tests and rerun step 2a
3. $ git add --all
4. $ git commit -m '<message>'
5. $ git push <destination>
    e.g. $ git push origin main
