import os
import json


memgator_uri_hash = {}

try:
    archive_files = os.listdir('./archive')
except Exception as e:
    print(f"Error listing files in ./archive: {e}")
    exit(1)

for filename in archive_files:

    try:
        with open(os.path.join('./archive', filename), 'r') as f:
            lines = f.readlines()

        json_start = next(i for i, line in enumerate(lines) if line.startswith('{'))

        json_data = ''.join(lines[json_start:])

        data = json.loads(json_data)

    except Exception as e:
        print(f"Error loading file {filename}: {e}")
        continue

    original_uri = data.get('original_uri')

    hash_value = filename.replace('-tm.json', '')

    memgator_uri_hash[original_uri] = hash_value


with open('./data/memgator_uri_hash.json', 'w') as f:
    json.dump(memgator_uri_hash, f)

print("Finished creating memgator_uri_hash.json.")
