"""Validate the portable, asset-free Arcade golden-case files."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
golden = json.loads((ROOT / 'references' / 'arcade-golden-result.json').read_text(encoding='utf-8'))
materials = json.loads((ROOT / 'references' / 'arcade-material-map.sample.json').read_text(encoding='utf-8'))
transform = json.loads((ROOT / 'references' / 'arcade-transform-sample.json').read_text(encoding='utf-8'))

assert golden['level'] == '/Game/Maps/M2_Arcade_Final'
assert golden['actors_total'] >= golden['static_mesh_actors'] >= 30
assert golden['vehicle']['full_submeshes'] == 7
assert golden['vehicle']['static_submeshes'] == 27
assert golden['vehicle']['total_submesh_actors'] == 34
assert golden['validation']['vehicle_static_records_match_complete_submesh_keys'] is True
assert golden['validation']['no_direct_zero_intensity_emissive_links'] is True
assert materials['full_trailer']['S03']['blend'] == 'Masked'
assert materials['static_trailer_examples']['Submesh_-_10__0_0_0_10_']['record'].endswith('(0 0 0 10)')
assert materials['static_trailer_examples']['Submesh_-_14__0_0_0_14_']['record'].endswith('(0 0 0 14)')
assert transform['ue_quaternion_xyzw'][3] < 0
assert transform['ue_rotation_degrees']['yaw'] < 0
print('ARCADE_CASE_VALID')
print('LEVEL', golden['level'])
print('ACTORS', golden['actors_total'], 'STATIC_MESH_ACTORS', golden['static_mesh_actors'])
print('TRAILER_SUBMESH_ACTORS', golden['vehicle']['total_submesh_actors'])
