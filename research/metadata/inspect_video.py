"""Read-only focused view of text/video/settings metadata definitions."""
import json
import re
import struct
from pathlib import Path
from inspect_metadata import inspect

output = Path(__file__).resolve().parent
metadata = Path(json.loads((output / 'metadata_evidence.json').read_text(encoding='utf-8'))['metadata'])
evidence, _ = inspect(metadata)
data = metadata.read_bytes()
sections = evidence['sections']


def name(index):
    start = sections['strings']['offset'] + index
    return data[start:data.index(b'\0', start)].decode('utf-8')


result = []
section = sections['types']
for index, offset in enumerate(range(section['offset'], section['offset'] + section['size'], 88)):
    rec = struct.unpack_from('<16i8H2I', data, offset)
    class_name, namespace = name(rec[0]), name(rec[1])
    if not re.search('VideoText|VideoManager|BP_Video|Settings|LanguageGroup', class_name, re.I):
        continue
    image = next((x['name'] for x in evidence['images'] if x['type_start'] <= index < x['type_start'] + x['type_count']), None)
    if image != 'Assembly-CSharp.dll':
        continue
    item = {'type_index': index, 'offset': offset, 'name': class_name, 'namespace': namespace,
            'image': image, 'methods': [], 'fields': []}
    for field_index in range(rec[8], rec[8] + rec[18]):
        at = sections['fields']['offset'] + 12 * field_index
        field = struct.unpack_from('<3i', data, at)
        item['fields'].append({'index': field_index, 'offset': at, 'name': name(field[0])})
    for method_index in range(rec[9], rec[9] + rec[16]):
        at = sections['methods']['offset'] + 36 * method_index
        method = struct.unpack_from('<7i4H', data, at)
        assert method[1] == index
        item['methods'].append({'index': method_index, 'offset': at, 'name': name(method[0]), 'parameter_count': method[-1]})
    result.append(item)
(output / 'video_settings_evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
for item in result:
    print(item)
