# AOC CLI

(using same commands as apexatoll/aoc-cli)

## Usage:

### Install

```bash
cd <some project folder>
git clone https://github.com/yspreen/aoc.git
cd aoc
sudo python3 main.py install
echo '^ make sure to install all missing requirements that are printed out by this command'
chmod 755 main.py # make usable by other users.
```

### Solve the Puzzles

```
cd <the folder you use for aoc>
 aoc login <your cookie>
mkdir 2022
cd 2022
aoc year 2022 # will set THIS FOLDER as the one for 2022.
aoc day 02 # will create a NEW FOLDER called `02` that contains this day.
cd 02
echo "now do some coding and solve this puzzle 🧠"
aoc solve 1234 # part one.
aoc solve 2345 # part two.
```

### My Cookie? What's That

You can copy it from safari, chrome, or any browser that has dev tools while you're on adventofcode.com.
Simply go to the storage or application tab in your dev tools, go to adventofcode.com and copy the `session` value.
That's your key that you can use with ` aoc login <session>`.
Super secret hint: if you add a space in front of a command in bash and most shells, it won't get added to your history so you can't accidentally reveal it later when doing a backwards history search.

![image](https://user-images.githubusercontent.com/12631527/205678570-427c4ee7-5746-4e73-b48e-a775375eadfc.png)


### Available Commands:

```
aoc -d <day> / aoc day <day>:
  Will create a new folder to solve the day numbered <day>.

aoc -y <year> / aoc year <year>:
  Will set up the current folder to contain puzzles for year <day>.

aoc -s <answer> / aoc solve <answer>:
  Will attempt to solve the current puzzle with answer <answer>.

aoc -k <param> / aoc login <param>:
  Will use your auth cookie to sign you in. Credentials stored (and git ignored automatically) in the current directory.

aoc -r <param> / aoc refresh <param>:
  Will reload the puzzle markdown and input.

aoc -i <param> / aoc install <param>:
  Will install this script in /usr/local/bin.
  (requires sudo.)
```

## Feedback?

Reach out on twitter @spreen_co

https://github-readme-twitter.gazf.vercel.app/api?id=spreen_co
