import subprocess
import os
import sys
import re
from datetime import datetime

try:
    from typing import Optional
except:
    pass

CONFIG_FILE = ".meta"
SESSION_FILE = ".aoc.secret"
LOG_FILE = ".answers.log"


class Config:
    def __init__(self) -> None:
        self.directory_type = None  # type: Optional[str]
        self.year = None  # type: Optional[int]
        self.day = None  # type: Optional[int]
        self.part = None  # type: Optional[int]
        self.cookie = ""


shared_config = Config()


def write_meta_file(config=None):
    config = config if config is not None else shared_config
    with open(CONFIG_FILE, "w") as f:
        if config.directory_type is not None:
            f.write("dir=>%s\n" % config.directory_type)
        if config.year is not None:
            f.write("year=>%d\n" % config.year)
        if config.day is not None:
            f.write("day=>%d\n" % config.day)
        if config.part is not None:
            f.write("part=>%d\n" % config.part)


def o_int(text):
    if text is None:
        return None
    return int(text)


def read_config():
    wd = os.getcwd()
    depth = wd.count("/")
    search_path = "./"
    while not os.path.exists(search_path + SESSION_FILE):
        depth -= 1
        if depth < 0:
            print("No %s file present." % SESSION_FILE)
            return None
        search_path += "../"
    session_path = search_path + SESSION_FILE
    with open(session_path) as file:
        shared_config.cookie = file.read().splitlines()[0]

    try:
        with open(CONFIG_FILE) as file:
            lines = file.read().splitlines()

        options = {}
        for line in lines:
            key, value = line.split("=>")
            options[key] = value

        shared_config.directory_type = options["dir"]
        shared_config.year = int(options["year"])
        shared_config.day = o_int(options.get("day", None))
        shared_config.part = o_int(options.get("part", None))
        return True
    except:
        print("No %s file present." % CONFIG_FILE)
        return False


def curl(endpoint, data="", cookie="", method="POST"):
    added_header = (
        "-H 'Content-Type: application/x-www-form-urlencoded'"
        if method != "GET"
        else ""
    )
    host = endpoint.split("//")[1].split("/")[0]
    cmd = """curl '%s' -L \
        -X '%s' \
        %s \
        -H 'Pragma: no-cache' \
        -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
        -H 'Accept-Language: en-US,en;q=0.9' \
        -H 'Cache-Control: no-cache' \
        -H 'Host: %s' \
        -H 'Origin: https://%s' \
        -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15' \
        -H 'Cookie: %s' \
        --data '%s'""" % (
        endpoint,
        method,
        added_header,
        host,
        host,
        cookie,
        data,
    )
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        shell=True,
    )
    result = p.communicate()
    return result[0].decode()


def which(cmd):
    p = subprocess.Popen(
        "which %s" % cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        shell=True,
    )
    result = p.communicate()[0].decode()
    return result != ""


def pandoc(from_file, to_file=".tmp.md"):
    p = subprocess.Popen(
        "pandoc -s -r html %s -o %s" % (from_file, to_file),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        shell=True,
    )
    _ = p.communicate()[0].decode()


def log_line(text):
    with open(LOG_FILE, "a") as f:
        f.write("[%s] \n" % (datetime.now().isoformat(), str(text)))


def log(answer, result):
    log_line("%s: %s" % (str(answer), str(result)))


def day_directory():
    return shared_config.directory_type == "DAY"


def submit(answer):
    if not read_config():
        return

    if not day_directory():
        print("This is not an AOC day directory.")
        return

    part = 0 if shared_config.part is None else shared_config.part

    if not (1 <= part <= 2):
        print("You can only solve two puzzles, one and two.")
        return

    endpoint = "https://adventofcode.com/%d/day/%d/answer" % (
        shared_config.year,
        shared_config.day,
    )
    data = "level=%d&answer=%s" % (shared_config.part, str(answer))
    cookie = shared_config.cookie

    html = curl(endpoint, data, cookie)
    text = parse_answer_html(html)
    text.split("(")[0]

    correct = True
    if "too low" in text:
        print("Too low.")
        log(answer, "low")
        correct = False
    elif "too high" in text:
        print("Too high.")
        log(answer, "low")
        correct = False
    elif "wait" in text:
        print("Please wait %s." % get_wait_time(text))
        correct = False
    elif "not the right answer" in text:
        print("Not correct.")
        log(answer, "wrong")
        correct = False
    else:
        log(answer, "correct")

    if not correct or shared_config.part is None:
        return

    shared_config.part += 1
    write_meta_file()


def get_wait_time(text):
    return text.split(" left")[0].split(" ")[-1]


def parse_answer_html(html):
    text = html  # type: str
    text = text.split("<article>")[1]
    text = text.split("</article>")[0]
    text = text.replace("\n", " ")
    text = re.sub("<.*?>", "", text)
    text = re.sub("\\s+", " ", text)
    text = text.strip(" ")
    return text


def check_requirements():
    for cmd in ["curl", "pandoc"]:
        if not which(cmd):
            print("Please install %s with\n brew install %s" % (cmd, cmd))
            return False
    return True


def remove_titles(line):
    return re.sub("\\[(.*?)\\]\\{title=.*\\}", "\\1", line)


def clean_up_md(file_name):
    with open(file_name, "r") as f:
        lines = f.read().splitlines()

    lines = lines[:-6]
    idx = lines.index('::: {role="main"}') + 1
    lines = lines[idx:]
    lines = list(map(lambda l: l.replace('{target="_blank"}', ""), lines))
    lines = list(map(remove_titles, lines))

    with open(file_name, "w") as f:
        f.write("\n".join(lines) + "\n")


def download_puzzle(config_):
    config = config_  # type: Config
    download_input(config)

    endpoint = "https://adventofcode.com/%d/day/%d" % (config.year, config.day)
    with open(".puzzle.tmp.html", "w") as f:
        f.write(curl(endpoint, cookie=config.cookie, method="GET"))

    pandoc(".puzzle.tmp.html", "%d.md" % config.day)
    clean_up_md("%d.md" % config.day)


def download_input(config_):
    config = config_  # type: Config
    endpoint = "https://adventofcode.com/%d/day/%d/input" % (config.year, config.day)
    with open("input", "w") as f:
        f.write(curl(endpoint, cookie=config.cookie, method="GET"))


def new_day_directory(day_string):
    day = int(day_string)

    if not read_config():
        return

    if day_directory():
        print("This is not a year directory.")
        return

    year = shared_config.year
    os.makedirs("%02d" % day)
    os.chdir("%02d" % day)
    try:
        config = Config()
        config.directory_type = "DAY"
        config.year = year
        config.day = day
        config.part = 1
        config.cookie = shared_config.cookie
        write_meta_file(config)
        download_puzzle(config)
    except:
        print("Failed to create day directory.")
    os.chdir("..")


def new_year_directory(year_string):
    year = int(year_string)

    try:
        config = Config()
        config.directory_type = "ROOT"
        config.year = year
        write_meta_file(config)
    except:
        print("Failed to create year directory.")


def main():
    if not check_requirements():
        return False

    arg = sys.argv
    a_len = len(arg)
    if a_len > 1 and arg[-2] == "-d":
        return new_day_directory(arg[-1])
    if a_len > 1 and arg[-2] == "-y":
        return new_year_directory(arg[-1])
    if a_len > 1 and arg[-2] == "-s":
        return submit(arg[-1])

    print("🐮")


if __name__ == "__main__":
    main()
