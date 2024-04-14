'''Main worker'''
import subprocess
import sys


def main():
    '''Main execution'''
    command = sys.argv[3]
    args = sys.argv[4:]

    completed_process = subprocess.run([command, *args], check=False, capture_output=True)
    sys.stdout.buffer.write(completed_process.stdout)
    sys.stderr.buffer.write(completed_process.stderr)
    sys.exit(completed_process.returncode)

if __name__ == "__main__":
    main()
