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
mkdir 2022
cd 2022
aoc -y 2022 # will set THIS FOLDER as the one for 2022.
aoc -d 02 # will create a NEW FOLDER called `02` that contains this day.
cd 02
echo "now do some coding and solve this puzzle 🧠"
aoc -s 1234 # part one.
aoc -s 2345 # part two.
```
