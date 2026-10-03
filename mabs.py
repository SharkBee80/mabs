import csv
import glob
import json
import os
import re
import sys

import requests
from dotenv import dotenv_values

default_env = {
    # "lang": "en",
    "username": "admin",
    "password": "admin123",
    "server": "http://127.0.0.1:8083",
    "booklist": "my books.csv",
}

"""load Env file"""

env: dict[str, str] = dict(dotenv_values())  # type: ignore

for k, v in default_env.items():
    if k not in env or not env[k]:
        env[k] = v

"""load Language file"""


def load_language() -> dict[str, str]:
    language_dict = {}
    json_files = glob.glob("language/*.json")
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if "0" in data:
                    filename = os.path.basename(file_path).replace(".json", "")
                    language_dict[filename] = data["0"]
                    if env.get("lang") and filename == env["lang"]:
                        return data
            except json.JSONDecodeError:
                continue

    question = {}
    for i, (k, v) in enumerate(sorted(language_dict.items())):
        question[i] = [k, v]

    # print(question)

    q = (
        "Choose a language (type the number):):"
        + "\n"
        + "\n".join([f"{i}. {question[i]}" for i in question])
        + "\n[0]: "
    )
    a = input(q)
    if a.isdigit() and int(a) in question:
        pass
    else:
        a = 0

    # print(question[int(a)])

    with open(f"language/{question[int(a)][0]}.json", "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise Exception("Language file is not valid")  # noqa: TRY002

    return data


language = load_language()

"""id"""


def input_id() -> list[str]:
    id = input(f"{language['book_id']} [1-3,5-7,9]:")
    # "1-3,5-7,9-11"
    id = id.replace("，", ",").split(",")
    ids = []
    for i in id:
        if "-" in i:
            a, b = i.split("-")
            ids += [str(j) for j in range(int(a), int(b) + 1)]
        else:
            ids.append(i)

    ids = list(dict.fromkeys(ids))

    print(",".join(ids))
    return ids


"""csv"""


def load_csv() -> list[str]:
    booklist = env["booklist"]
    booklist = input(f"{language['booklist_path']}_{booklist}:")

    ids = []
    try:
        with open(booklist, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for current_row in reader:
                if "id" in current_row or "\ufeffid" in current_row:
                    id = current_row.get("id", current_row.get("\ufeffid"))
                    ids.append(id)
                else:
                    print(
                        "No ID-field found in current row of csv file, check for seperation character (has to be ',') and spelling of 'id' field"
                    )
                    sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error on opening bookslist file: {e}")
        sys.exit(1)

    ids = list(dict.fromkeys(ids))
    print(",".join(ids))
    return ids


"""mode"""


def choose_mode() -> tuple[int, list[str]]:
    try:
        mode = None
        if env.get("mode") and env["mode"] in ["1", "2"]:
            mode = int(env["mode"]) - 1
        else:
            mode = int(
                input(f"0.{language['mode_1']}\n1.{language['mode_2']}\n[0]:") or 0
            )

        if mode == 0:
            ids = input_id()
            return mode, ids
        elif mode == 1:
            ids = load_csv()
            return mode, ids
        else:
            raise ValueError("Mode is not valid")
    except ValueError as e:
        print(f"Error on choosing mode: {e}")
        sys.exit(1)


"""login"""


def login():
    session = requests.session()
    if env.get("username") and env.get("password") and env.get("server"):
        pass
    else:
        print(language["login_err_env"])
        sys.exit(1)
    try:
        login_page = session.get(env["server"] + "/login")
        token = re.search(
            '<input type="hidden" name="csrf_token" value="(.*)">', login_page.text
        )
        assert token is not None
        resp = session.post(
            env["server"] + "/login?next=/",
            data={
                "username": env["username"],
                "password": env["password"],
                "submit": "",
                "remember_me": "on",
                "next": "/",
                "csrf_token": token.group(1),
            },
        )
    except Exception as e:
        print(f"{language['login_err_connect']} : {e}")
        session.close()
        sys.exit(1)

    if "login" in resp.text or resp.status_code != 200:
        print(language["login_err_sign"])
        session.close()
        sys.exit(1)
    # print(token.group(1))\

    return session, token.group(1)


"""add"""


def shelf_add(shelf_id, ids, session: requests.Session, token):
    try:
        headers = {"Referer": env["server"] + "/"}
        for id in ids:
            if id.isdigit():
                payload = {"csrf_token": token}
                add = session.post(
                    env["server"] + "/shelf/add/" + str(shelf_id) + "/" + id,
                    data=payload,
                    cookies=session.cookies,
                    headers=headers,
                )
                if add.status_code != 200:
                    print(language["shelf_add_err_1"].format(id, shelf_id))
                else:
                    message = re.findall(
                        'id="flash_.*class=.*>(.*)</div>', add.content.decode("utf-8")
                    )
                    if not message:
                        print(language["shelf_add_err_2"].format(id))
                    else:
                        print(language["shelf_add_ok"].format(id, message[0]))
            else:
                print(language["shelf_add_err_3"].format(id))
    except Exception as e:
        print(language["shelf_add_err"].format(e))


"""main"""


def main():
    # print(env)
    # print(language)
    shelf_id = int(input(f"{language['shelf_id']}:"))

    _mode, ids = choose_mode()

    session, token = login()

    shelf_add(shelf_id, ids, session, token)


if __name__ == "__main__":
    main()
