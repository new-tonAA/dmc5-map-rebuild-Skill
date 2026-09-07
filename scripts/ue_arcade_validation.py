"""Run inside UE Python/Remote Execution after opening M2_Arcade_Final."""

import unreal


actors = unreal.EditorLevelLibrary.get_all_level_actors()
static_meshes = [actor for actor in actors if isinstance(actor, unreal.StaticMeshActor)]
missing_mesh = []
missing_material = []
for actor in static_meshes:
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if not component or not component.static_mesh:
        missing_mesh.append(actor.get_actor_label())
        continue
    if not any(component.get_material(index) for index in range(component.get_num_materials())):
        missing_material.append(actor.get_actor_label())

vehicle = [
    actor for actor in static_meshes
    if actor.get_actor_label().startswith(('Arcade_TrailerFull_', 'Arcade_TrailerStaticCorrected_'))
]
vehicle_yaws = sorted({round(actor.get_actor_rotation().yaw, 4) for actor in vehicle})
lights = [
    actor for actor in actors
    if isinstance(actor, (unreal.DirectionalLight, unreal.SkyLight, unreal.PointLight, unreal.SpotLight, unreal.RectLight))
]
print('ARCADE_LEVEL_VALIDATION')
print('ACTORS_TOTAL', len(actors))
print('STATIC_MESH_ACTORS', len(static_meshes))
print('LIGHT_ACTORS', len(lights))
print('VEHICLE_SUBMESH_ACTORS', len(vehicle))
print('VEHICLE_YAWS', vehicle_yaws)
print('MISSING_MESH', len(missing_mesh), missing_mesh[:10])
print('MISSING_MATERIAL', len(missing_material), missing_material[:10])
assert len(static_meshes) >= 30
assert not missing_mesh
assert not missing_material
assert len(vehicle) == 34
assert len(vehicle_yaws) == 1
