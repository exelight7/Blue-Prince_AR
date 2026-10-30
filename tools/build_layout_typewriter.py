"""Isolated B follow-up: explicit logical wrapping, lam-alef and stock typewriter probe."""
import copy
import argparse
import json
import UnityPy
from project import ROOT,sha256,write_new
from schemas import Schemas
from build_poc import encode
from arabic_plain import visual_line,wrap_plain


def main():
    if not __debug__:raise RuntimeError('Verification requires Python without -O')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision',choices=['3','4','5'],default='5')
    revision=parser.parse_args().revision
    suffix='' if revision=='3' else f'_v{revision}'
    source=ROOT/'build/runtime_matrix_v2/b/BLUE PRINCE_Data/level1'
    env=UnityPy.load(str(source));baseline={o.path_id:o.get_raw_data() for o in env.objects}
    tmp_node=Schemas().get('Unity.TextMeshPro','TMPro.TextMeshPro')
    expected={}
    lamalef='لا   لأ   لإ   لآ\nمرحبا، كيف حالك؟'
    long='هذا اختبار طويل للتأكد من أن النص العربي يلتف داخل مساحة الواجهة بشكل صحيح ولا يخرج خارج حدود العنصر.'
    lines,wrapped=wrap_plain(long,17.0)
    for pid,text in [(3568,'\n'.join(visual_line(x) for x in lamalef.split('\n'))),(3456,wrapped)]:
        obj=env.file.objects[pid];data=obj.read_typetree(nodes=tmp_node)
        assert encode(data,tmp_node)==baseline[pid]
        data['m_text']=text
        # Explicit rows prevent TMP from reordering visual-order paragraph fragments.
        data['m_enableWordWrapping']=0
        data['m_enableAutoSizing']=1
        data['m_fontSizeMin']=1.0
        data['m_fontSizeMax']=2.0 if pid==3568 else (1.5 if revision in ('4','5') else 2.5)
        expected[pid]=data;obj.set_raw_data(encode(data,tmp_node))
    fsm_node=Schemas('AssetStudio').get('PlayMaker','PlayMakerFSM')
    data=json.loads((ROOT/'research/runtime_textflow/adapted_typewriter_data.json').read_text())
    sentence='مرحبا بك في القصر، الغرفة رقم 27.'
    data['fsm']['states'][0]['actionData']['fsmStringParams'][0]['value']=visual_line(sentence)
    data['fsm']['states'][0]['actionData']['fsmFloatParams'][0]['value']=0.25
    if revision in ('4','5'):data['fsm']['states'][0]['actionData']['fsmBoolParams'][0]['value']=True
    if revision=='5':
        data['fsm']['preprocessed']=False
        data['fsm']['states']=data['fsm']['states'][:1]
    new_id=1000000001
    assert new_id not in env.file.objects
    added=copy.copy(env.file.objects[3741]);added.path_id=new_id
    added.set_raw_data(encode(data,fsm_node));env.file.objects[new_id]=added
    go_obj=env.file.objects[170];go=go_obj.read_typetree()
    go['m_Component'].append(dict(component=dict(m_FileID=0,m_PathID=new_id)))
    go_obj.save_typetree(go)
    fsm_expected={new_id:data};go_expected={170:go}
    if revision=='5':
        control=copy.deepcopy(data)
        control['m_GameObject']=dict(m_FileID=0,m_PathID=78)
        control['fsm']['name']='English typewriter control'
        control['fsm']['states'][0]['actionData']['fsmStringParams'][0]['value']='English control 123'
        control['fsm']['states'][0]['actionData']['fsmPropertyParams'][0]['TargetObject']['value']=dict(m_FileID=0,m_PathID=3380)
        control_id=new_id+1
        wrapper=copy.copy(env.file.objects[3741]);wrapper.path_id=control_id
        wrapper.set_raw_data(encode(control,fsm_node));env.file.objects[control_id]=wrapper
        control_go=env.file.objects[78].read_typetree()
        control_go['m_Component'].append(dict(component=dict(m_FileID=0,m_PathID=control_id)))
        env.file.objects[78].save_typetree(control_go)
        go_expected[78]=control_go;fsm_expected[control_id]=control
        ctrl=env.file.objects[3380].read_typetree(nodes=tmp_node)
        ctrl['m_fontAsset']=dict(m_FileID=2,m_PathID=244);ctrl['m_sharedMaterial']=dict(m_FileID=2,m_PathID=43)
        ctrl['m_fontStyle']=0;ctrl['m_characterSpacing']=0.0;ctrl['m_lineSpacing']=0.0
        expected[3380]=ctrl;env.file.objects[3380].set_raw_data(encode(ctrl,tmp_node))
    output=env.file.save();out=ROOT/f'build/runtime_layout_typewriter{suffix}/BLUE PRINCE_Data/level1'
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists() and out.read_bytes()!=output:raise FileExistsError(out)
    if not out.exists():out.write_bytes(output)
    reopened=UnityPy.load(str(out));assert len(reopened.file.objects)==len(baseline)+len(fsm_expected)
    for pid,value in fsm_expected.items():assert reopened.file.objects[pid].read_typetree(nodes=fsm_node)==value
    for pid,value in go_expected.items():assert reopened.file.objects[pid].read_typetree()==value
    for pid,raw in baseline.items():
        if pid in expected:assert reopened.file.objects[pid].read_typetree(nodes=tmp_node)==expected[pid]
        elif pid not in go_expected:assert reopened.file.objects[pid].get_raw_data()==raw
    assert reopened.file.save()==output
    write_new(ROOT/f'tests/runtime_layout_typewriter{suffix}_manifest.json',dict(status='PASS_OFFLINE',
        source=str(source),source_sha256=sha256(source),output=str(out),sha256=sha256(out),
        changed_existing_objects=sorted(set(expected)|set(go_expected)) if revision=='5' else [3568,3456,170],new_objects=list(fsm_expected),
        unchanged_relative_to_b=len(baseline)-len(expected)-len(go_expected),lamalef_logical=lamalef,
        wrapping_logical_source=long,wrapping_logical_lines=lines,max_width_em=17.0,
        typewriter_logical=sentence,typewriter_input=visual_line(sentence),
        typewriter_target_tmp=3411,typewriter_target_go=170,interval_seconds=0.25,
        note='Stock game action, no executable modification; reveal direction is deliberately under test'))
    print('PASS: logical-wrap and lam-alef follow-up plus stock typewriter probe')


if __name__=='__main__':main()
