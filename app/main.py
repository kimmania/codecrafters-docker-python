'''Main worker'''
import subprocess
import sys
import os

#Details on inclusions
#The `os` module provides a way to interact with the operating system

def main():
    '''Main execution'''
    command = sys.argv[3]
    args = sys.argv[4:]

    os.system("mkdir -p /tmp/usr/local/bin")
    os.system("cp /usr/local/bin/docker-explorer /tmp/usr/local/bin/")

    #The unshare command is used to run a program with some namespaces unshared from the parent process. 
    #The -f flag is for forking a new process, 
    # -p creates a new PID namespace, 
    # -u creates a new UTS namespace (which allows isolation of hostname and domain name).

    #chroot is called to change the root directory, and then the original command is executed within this isolated environment.
    completed_process = subprocess.run(
        ["unshare", "-fpu", "chroot", "/tmp", command, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, 
        check=False
    )

    sys.stdout.buffer.write(completed_process.stdout)
    sys.stderr.buffer.write(completed_process.stderr)
    sys.exit(completed_process.returncode)

if __name__ == "__main__":
    main()
