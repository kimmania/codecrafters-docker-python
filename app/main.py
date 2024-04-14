'''Main worker'''
import subprocess
import sys
import os
import tempfile
import shutil
import urllib.request
import json
import tarfile

def get_docker_token(image_name: str) -> str:
    '''Get the token from GitHub '''
    # You need to get an auth token, but you don't need a username/password
    # Say your image is busybox/latest, you would make a GET request to this 
    # URL: https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/busybox:pull
    url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/{image_name}:pull"
    res = urllib.request.urlopen(url)
    res_json = json.loads(res.read().decode())
    return res_json["token"] 

def build_docker_headers(token: str) -> dict:
    '''Generate the docker headers for requests'''
    return {
        "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        "Authorization": f'Bearer {token}'
    }

def get_docker_image_manifest(headers: dict, image_name:str) -> dict:
    '''retrieve the image manifest from docker hub'''
    manifest_url = (
        f"https://registry.hub.docker.com/v2/library/{image_name}/manifests/latest"
    )
    request = urllib.request.Request(
        manifest_url,
        headers=headers,
    )
    res = urllib.request.urlopen(request)
    res_json = json.loads(res.read().decode())
    return res_json

def download_image_layers(headers: dict, image: str, layers) -> str:
    '''download the layers and extract the files'''
    dir_path = tempfile.mkdtemp()
    # loop the layers to pull down each manifest
    for layer in layers:
        url = f"https://registry.hub.docker.com/v2/library/{image}/blobs/{layer['digest']}"
        sys.stderr.write(url)
        request = urllib.request.Request(
            url,
            headers=headers
        )
        res = urllib.request.urlopen(request)
        tmp_file = os.path.join(dir_path, "manifest.tar")
        with open(tmp_file, "wb") as f:
            shutil.copyfileobj(res, f)
        with tarfile.open(tmp_file) as tar:
            tar.extractall(dir_path)
    os.remove(tmp_file)
    return dir_path

def execute_command(dir_path, command, args):
    '''Execute the command'''
    #The unshare command is used to run a program with some namespaces
    #unshared from the parent process.
    #The -f flag is for forking a new process
    # -p creates a new PID namespace
    # -u creates a new UTS namespace (which allows isolation of hostname and domain name).

    #chroot is called to change the root directory,
    #and then the original command is executed within this isolated environment.
    completed_process = subprocess.run(
        ["unshare", "-fpu", "chroot", dir_path, command, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False
    )
    sys.stdout.buffer.write(completed_process.stdout)
    sys.stderr.buffer.write(completed_process.stderr)
    sys.exit(completed_process.returncode)


def main():
    '''Main execution'''
    image = sys.argv[2]
    command = sys.argv[3]
    args = sys.argv[4:]
    # 1. get token from Docker auth server by making GET req using image from args
    token = get_docker_token(image_name=image)
    # 2. create header for docker calls
    headers = build_docker_headers(token)
    # 3. get image manifest for specified image from Docker Hub
    manifest = get_docker_image_manifest(headers, image)
    # 4. Download layers from manifest file and put result a tarfile (call it manifest.tar)
    dir_path = download_image_layers(headers, image, manifest["layers"])
    # 5. Run the command
    execute_command(dir_path, command, args)

if __name__ == "__main__":
    main()
