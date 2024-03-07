import subprocess
import hashlib
import time
import os

os.makedirs('archive', exist_ok=True)

with open('./data/unique_uris.txt', 'r') as f:
    for uri in f:
        uri = uri.strip()
        print(f"Processing URI: {uri}")
        hash_object = hashlib.md5(uri.encode())
        md5_hash = hash_object.hexdigest()
        command = f'docker run -it --rm oduwsdl/memgator -c "ODU CS432/532 sgrov009@odu.edu" -a https://raw.githubusercontent.com/odu-cs432-websci/public/main/archives.json -F 2 -f JSON "{uri}" > "./archive/{md5_hash}-tm.json"'
        subprocess.run(command, shell=True)
        print(f"Finished processing URI: {uri}")
        time.sleep(20)
