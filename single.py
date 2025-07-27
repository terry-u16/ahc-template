import argparse
import shutil
import subprocess

CONTEST_NAME = "{{project-name}}"

def run_single(seed: int):
    subprocess.run(["cargo", "build", "--release"]).check_returncode()
    shutil.move(f"../target/release/{CONTEST_NAME}", f"./{CONTEST_NAME}")

    input_file = f"./pahcer/in/{seed:04}.txt"
    output_file = "./out.txt"
    err_file = "./err.txt"
    {% if is-interactive %}
    with open(input_file, "r") as i:
        with open(output_file, "w") as o:
            with open(err_file, "w") as e:
                subprocess.run(["./tester", f"./{CONTEST_NAME}"], stdin=i, stdout=o, stderr=e)

    with open(err_file, "r") as e:
        for line in e.readlines():
            print(line.strip())
    {% else %}
    with open(input_file, "r") as i:
        with open(output_file, "w") as o:
            with open(err_file, "w") as e:
                proc = subprocess.run(
                    [f"./{CONTEST_NAME}"], stdin=i, stdout=o, stderr=e
                )

    with open(err_file, "r") as e:
        for line in e.readlines():
            print(line.strip())

    proc.check_returncode()
    subprocess.run(["./vis", input_file, output_file]).check_returncode()
{% endif %}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--seed", type=int, required=True)
    args = parser.parse_args()
    run_single(args.seed)
