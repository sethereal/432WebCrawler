import os
import json
from collections import defaultdict


memento_counts = defaultdict(int)
timemap_files = os.listdir('../archive')


for filename in timemap_files:
    with open(os.path.join('../archive', filename), 'r') as f:
        lines = f.readlines()

    json_start = next((i for i, line in enumerate(lines) if line.startswith('{')), None)

    if json_start is not None:
        json_data = ''.join(lines[json_start:])
        timemap = json.loads(json_data)


        mementos = timemap.get('mementos', {}).get('list', [])
        memento_count = len(mementos)
        memento_counts[memento_count] += 1


print("| Mementos | URI-Rs |")
print("|----------|--------|")
for memento_count, uri_count in sorted(memento_counts.items()):
    print(f"| {memento_count} | {uri_count} |")
    