'''Main worker'''
import subprocess
import sys
import os
import shutil
import tempfile

#Details on inclusions
#The `os` module provides a way to interact with the operating system, which is necessary for operations like changing the root directory with `chroot`. 
#The `shutil` module offers file operations, such as copying files, which we'll need to move the binary into a new temporary directory. 
#Lastly, the `tempfile` module is used to create temporary directories that we can use as isolated environments for our container. 
#These imports are essential for setting up filesystem isolation, ensuring that the program we execute is restricted to a specific directory and cannot access the host machine's filesystem.


def main():
    '''Main execution'''
    command = sys.argv[3]
    args = sys.argv[4:]

    #tempfile.TemporaryDirectory() which is used as a context manager. This means that the directory is automatically cleaned up when the block of code is done executing.
    with tempfile.TemporaryDirectory() as tmpdirname:
        shutil.copy2(command, tmpdirname) # used to copy the command (which is a binary file) into the temporary directory.
        command_at_new_root = os.path.join("/", os.path.basename(command))
        os.chroot(tmpdirname) #changing the root directory with os.chroot, all paths will be relative to the new root. This works for posix systems
        # subprocess.run is used to execute the command in the new isolated environment. The command is now prefixed with the new root directory path to ensure it is executed within the chroot environment
        completed_process = subprocess.run(
            [command_at_new_root, *args], check=False, capture_output=True
        )


    sys.stdout.buffer.write(completed_process.stdout)
    sys.stderr.buffer.write(completed_process.stderr)
    sys.exit(completed_process.returncode)

if __name__ == "__main__":
    main()
