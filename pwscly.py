#!/usr/bin/env python3

import os
import sys
import pypwsafev3
from pypwsafev3 import PWSafe3
from getpass import getpass
from subprocess import run

SEPARATOR = ".:."

null = open(os.devnull, "w")
stderr = sys.stderr


def endline(string):
    string = string.strip().replace("\r\n", " ")
    string = string.strip().replace("\n", " ")
    return string


try:
    path = os.environ.get("PWCLYFILE") or sys.argv[1]
except IndexError:
    stderr.write(
        "You must specify filename on commandline or by PWCLYFILE variable.\n"
    )
    exit(2)

password = getpass("[{0}] password > ".format(path))

sys.stderr = null
try:
    safe = PWSafe3(filename=path, password=password, mode="RO")
except pypwsafev3.errors.PasswordError:
    # raise Exception("Invalid password")
    stderr.write("Error: Invalid password\n")
    exit(1)
finally:
    sys.stderr = stderr

data = ""
passwords = {}
for record in safe:
    record_data = [
        ",".join(record["Group"]),
        record["Title"],
        # "" if not record["Group"] else record["Group"][0],
        record["Username"],
        record["URL"],
        record["Notes"],
    ]
    record_data = map(endline, record_data)
    line = SEPARATOR.join(record_data) + "\n"
    data += line
    passwords[line] = record["Password"]

fzy = run(["fzy"], input=data.encode("utf8"), capture_output=True)

line = fzy.stdout.decode("utf8")
if not line:
    print("Noinput")
    exit(0)
group, title, username, url, notes = line.strip().split(SEPARATOR)
print(
    f"""Group: {group}
Title: {title}
Username: {username}
URL: {url}
Notes: {notes}"""
)

run(["xclip", "-i"], input=passwords[line].encode("utf8"))
