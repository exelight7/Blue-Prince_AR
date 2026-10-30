"""Read-only IL2CPP v31 localization evidence. Never loads executable code."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

SECTIONS = ('string_literals literal_data strings events properties methods parameter_defaults '
            'field_defaults default_data field_marshaled_sizes parameters fields generic_parameters '
            'generic_constraints generic_containers nested_types interfaces vtable_methods '
            'interface_offsets types images assemblies field_refs referenced_assemblies attribute_data '
            'attribute_ranges unresolved_types unresolved_ranges windows_type_names windows_strings '
            'exported_types').split()
RELEVANT = re.compile(r'localiz|language|subtitle|dialog|typewriter|typing|reveal|visiblechar|rtl|righttoleft|arabic|bidi|shap|textmesh|textmanager|textcontroller|textanim', re.I)


def inspect(path):
    data = path.read_bytes()
    magic, version = struct.unpack_from('<II', data)
    if magic != 0xFAB11BAF or version != 31:
        raise ValueError('Only validated IL2CPP metadata version 31 is supported')
    sections = {name: dict(zip(('offset', 'size'), struct.unpack_from('<II', data, 8 + i * 8)))
                for i, name in enumerate(SECTIONS)}
    for item in sections.values():
        if item['offset'] + item['size'] > len(data):
            raise ValueError('Metadata section exceeds file bounds')

    def records(name, fmt):
        item = sections[name]
        size = struct.calcsize(fmt)
        if item['size'] % size:
            raise ValueError(f'Unexpected {name} record size')
        return [(pos, struct.unpack_from(fmt, data, pos))
                for pos in range(item['offset'], item['offset'] + item['size'], size)]

    def string(index):
        item = sections['strings']
        if not 0 <= index < item['size']:
            raise ValueError('Invalid metadata name index')
        start = item['offset'] + index
        end = data.index(b'\0', start, item['offset'] + item['size'])
        return data[start:end].decode('utf-8')

    types = []
    for i, (offset, rec) in enumerate(records('types', '<16i8H2I')):
        types.append({'index': i, 'offset': offset, 'name': string(rec[0]), 'namespace': string(rec[1]),
                      'field_start': rec[8], 'method_start': rec[9], 'method_count': rec[16],
                      'field_count': rec[18], 'image': None})
    images = []
    for offset, rec in records('images', '<10i'):
        name, _, start, count = rec[:4]
        image = {'name': string(name), 'offset': offset, 'type_start': start, 'type_count': count}
        images.append(image)
        if start < 0 or start + count > len(types):
            raise ValueError('Invalid image type range')
        for ty in types[start:start + count]:
            ty['image'] = image['name']
    methods = []
    for i, (offset, rec) in enumerate(records('methods', '<7i4H')):
        name, declaring_type = rec[:2]
        if not 0 <= declaring_type < len(types):
            raise ValueError('Invalid method declaring type')
        ty = types[declaring_type]
        methods.append({'index': i, 'offset': offset, 'name': string(name),
                        'class': ty['name'], 'namespace': ty['namespace'], 'image': ty['image'],
                        'parameter_count': rec[-1], 'declaring_type_index': declaring_type})
    fields = []
    for i, (offset, rec) in enumerate(records('fields', '<3i')):
        fields.append({'index': i, 'offset': offset, 'name': string(rec[0])})
    for ty in types:
        start, count = ty['field_start'], ty['field_count']
        if count:
            if start < 0 or start + count > len(fields):
                raise ValueError('Invalid field range')
            for item in fields[start:start + count]:
                item.update({'class': ty['name'], 'namespace': ty['namespace'], 'image': ty['image']})
    literals = []
    for i, (offset, rec) in enumerate(records('string_literals', '<Ii')):
        length, index = rec
        section = sections['literal_data']
        if index < 0 or index + length > section['size']:
            raise ValueError('Invalid string literal span')
        start = section['offset'] + index
        literals.append({'index': i, 'record_offset': offset, 'data_offset': start,
                         'length_bytes': length, 'text': data[start:start + length].decode('utf-8')})
    evidence = {'metadata': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'magic': hex(magic),
                'version': version, 'sections': sections, 'images': images,
                'counts': {'types': len(types), 'methods': len(methods), 'fields': len(fields), 'literals': len(literals)},
                'relevant_types': [x for x in types if RELEVANT.search(x['name'])],
                'relevant_methods': [x for x in methods if RELEVANT.search(x['name'] + ' ' + x['class'])],
                'relevant_fields': [x for x in fields if RELEVANT.search(x['name'] + ' ' + x.get('class', ''))],
                'relevant_literals': [x for x in literals if RELEVANT.search(x['text'])]}
    return evidence, literals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('metadata', type=Path)
    args = parser.parse_args()
    output = Path(__file__).resolve().parent
    evidence, literals = inspect(args.metadata)
    for name, value in [('metadata_evidence.json', evidence), ('string_literals.json', literals)]:
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(evidence['counts']))
    for ty in evidence['relevant_types']:
        if ty['image'] in ('Assembly-CSharp.dll', 'Assembly-CSharp-firstpass.dll'):
            print(ty['image'], ty['index'], ty['name'], ty['offset'])
    print('Validated header, section bounds, record sizes, name decoding, type ranges and literal spans.')


if __name__ == '__main__':
    main()
