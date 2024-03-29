import subprocess
import os
import stat
import sys
import re
from datetime import datetime
from time import sleep

try:
    from typing import Optional
except:
    pass

CONFIG_FILE = ".meta"
SESSION_FILE = ".aoc.secret"
LOG_FILE = ".answers.log"
DEBUG_HTML_FILE = "debug-full-aoc-response.html"


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


def find_in_tree(filename):
    wd = os.getcwd()
    depth = wd.count("/")
    search_path = "./"
    while not os.path.exists(search_path + filename):
        depth -= 1
        if depth < 0:
            return None
        search_path += "../"
    return search_path + filename


def write_git_ignore():
    lines = [SESSION_FILE, LOG_FILE]
    git_path = find_in_tree(".git")
    if git_path is None:
        return
    git_ignore_path = git_path + "ignore"

    for line in lines:
        try:
            with open(git_ignore_path, "r") as f:
                read_lines = f.read().splitlines()
                read_lines = list(map(lambda l: l.split(" #")[0], read_lines))
                read_lines = list(map(lambda l: l.split("#")[0], read_lines))
                assert line in read_lines
        except:
            with open(git_ignore_path, "a") as f:
                f.write("\n%s\n" % line)


def read_config():
    session_path = find_in_tree(SESSION_FILE)
    if session_path is None:
        print("No %s file present." % SESSION_FILE)
        print("You can log in with `aoc -k <cookie>`")
        return False
    with open(session_path) as file:
        shared_config.cookie = file.read().splitlines()[0]

    write_git_ignore()

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
        -H 'User-Agent: https://github.com/yspreen/aoc' \
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
    os.remove(from_file)


def log_line(text):
    with open(LOG_FILE, "a") as f:
        f.write("[%s] %s\n" % (datetime.now().isoformat(), str(text)))


def log(answer, result):
    log_line("%s: %s" % (str(answer), str(result)))


def day_directory():
    return shared_config.directory_type == "DAY"

def format_seconds(seconds):
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 60 * 60:
        return f"{seconds // 60}m {seconds % 60}s"
    return f"{seconds // 60 // 60}h {(seconds // 60) % 60}m {seconds % 60}s"

def wait(wait_text, answer):
    seconds = 0
    for part in wait_text.split(" "):
        if part.endswith("s"):
            seconds += int(part[:-1])
        if part.endswith("m"):
            seconds += int(part[:-1]) * 60
        if part.endswith("h"):
            seconds += int(part[:-1]) * 60
    while seconds >= 0:
        print(f"\rWaiting {format_seconds(seconds)} before retry... (ctrl+c to stop) ", end='')
        sleep(1)
        seconds -= 1
    print()
    submit(answer)

def submit(answer):
    if answer == "":
        return

    if not read_config():
        return

    if not day_directory():
        print("This is not an AOC day directory.")
        return

    try:
        with open(LOG_FILE, "r") as f:
            text = f.read()
        for line in text.splitlines():
            if line.split("] ", 1)[1].startswith(answer + ":"):
                return print("We already gave this answer.")
            if line.split("] ", 1)[1].startswith(
                answer + " (part %d):" % shared_config.part
            ):
                return print("We already gave this answer.")
    except Exception:
        pass

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

    correct = False
    log_answer = lambda result: log(answer, result)
    if " too low. " in text:
        print("Too low.")
        log_answer("low")
    elif " too high. " in text:
        print("Too high.")
        log_answer("high")
    elif "left to wait" in text:
        return wait(get_wait_time(text), answer)
    elif "not the right answer" in text:
        print("Not correct.")
        log_answer("wrong")
    elif "right answer" in text:
        print("Correct! Part %d complete." % shared_config.part)
        log_answer("correct")
        correct = True
    else:
        print(
            "Whelp. AOC CLI could not parse this server response. Here's what I got:\n"
        )
        print(text)
        print(
            "\nMaybe you can help make aoc cli better and report this. I also put the full html response into a temporary file in this directory called %s"
            % DEBUG_HTML_FILE
        )
        print("Might be helpful for debugging! Cheers 🎄")
        with open(DEBUG_HTML_FILE, "w") as f:
            f.write(html)
        return

    if not correct or shared_config.part is None:
        return

    shared_config.part += 1
    write_meta_file()
    refresh()


def get_wait_time(text):
    return text.split(" left")[0].split("have ")[-1]


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


def refresh():
    if not read_config():
        return
    download_puzzle(shared_config)
    download_input(shared_config)


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
        log_line("downloaded")
    except Exception as e:
        print("Failed to create day directory:", e)
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


def store_key(cookie_):
    cookie = cookie_.lower()  # type: str
    if cookie.startswith("cookie: "):
        cookie = cookie[len("cookie: ") :]
    if not cookie.startswith("session="):
        cookie = "session=" + cookie
    with open(SESSION_FILE, "w") as f:
        f.write(cookie)
    print("(Stored in %s)" % SESSION_FILE)
    write_git_ignore()


def install_script():
    raw = """
    #!/bin/sh

    "%s" "%s" "$@"
    """ % (
        sys.executable,
        __file__,
    )

    raw = raw.strip("\n").splitlines()
    raw = list(map(lambda l: l.strip(" \t"), raw))
    return "\n".join(raw + [""])


def install():
    exec = "/usr/local/bin/aoc"
    try:
        with open(exec, "w") as f:
            f.write(install_script())
        os.chmod(exec, os.stat(exec).st_mode | 0o555)
    except:
        print("Retry with sudo.")


def main():
    if not check_requirements():
        return False

    arg = sys.argv
    a_len = len(arg)
    if a_len > 1 and arg[-2] in ["-d", "day"]:
        return new_day_directory(arg[-1])
    if a_len > 1 and arg[-2] in ["-y", "year"]:
        return new_year_directory(arg[-1])
    if a_len > 1 and arg[-2] in ["-s", "solve"]:
        return submit(arg[-1])
    if a_len > 1 and arg[-2] in ["-k", "login"]:
        return store_key(arg[-1])
    if a_len > 0 and arg[-1] in ["-r", "refresh"]:
        return refresh()
    if a_len > 0 and arg[-1] in ["-i", "install"]:
        return install()

    print_help()

def print_help():
    print("Usage: aoc [command] [options]")
    print()
    print("Commands:")
    print("aoc -d <day> / aoc day <day>: ")
    print("  Will create a new folder to solve the day numbered <day>. ")
    print()
    print("aoc -y <year> / aoc year <year>: ")
    print("  Will set up the current folder to contain puzzles for year <day>. ")
    print()
    print("aoc -s <answer> / aoc solve <answer>: ")
    print("  Will attempt to solve the current puzzle with answer <answer>. ")
    print()
    print("aoc -k <param> / aoc login <param>: ")
    print("  Will use your auth cookie to sign you in. Credentials stored (and git ignored automatically) in the current directory. ")
    print()
    print("aoc -r <param> / aoc refresh <param>: ")
    print("  Will reload the puzzle markdown and input. ")
    print()
    print("aoc -i <param> / aoc install <param>: ")
    print("  Will install this script in /usr/local/bin. ")
    print("  (requires sudo.) ")
    print()
    print("For more information, visit https://github.com/yspreen/aoc")

if __name__ == "__main__":
    main()
