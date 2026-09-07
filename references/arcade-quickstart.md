# Arcade Golden-Case Quickstart

Use this as the shortest reliable path for reconstructing one DMC5 region.

## Inputs

Set these placeholders before running any commands:

```text
<UE_PROJECT>    UE project containing the target level
<UE_ROOT>       UE 5.x installation
<DMC5_EXTRACT>  extracted DMC5 natives/x64 directory
<REI_ADDON>    Blender RE Engine Importer directory
<BLENDER>      Blender 4.5.x executable
<BACKUP_ROOT>  private backup directory, preferably another drive
```

Work on one region only:

```text
region = l02_01_arcade
level  = /Game/Maps/M2_Arcade_Final
```

## One-pass order

1. Import each source mesh through REI Blender with its matching MDF; do not use `from_pydata` or a temporary grid.
2. Export/import StaticMeshes, then bind materials by the complete REI submesh key, not filename order.
3. Parse SCN parent chains and convert each world quaternion with `(qx, qz, qy, -qw)`.
4. Build materials from `ALBM`, `NRMR`, and MDF-confirmed auxiliary maps.
5. Inspect REI shader type and `Emissive_Intensity` before choosing UE blend mode or Emissive.
6. Assemble the final level only; keep old import/test levels out of the validation pass.
7. Inventory the region-specific light SCN before adding any UE helper light. For `l02_01_arcade`, inspect PointLight, SpotLight, IESLight, IBL, LightProbes, LUT, and post-process records; do not infer lighting from `l02_common` alone.
8. Review textures in Unlit, then review source/diagnostic lighting in Lit. Treat a small DirectionalLight/SkyLight setup as incomplete until local light records are audited.
9. Run the UE validation script, save the level, and create a private backup.

## Material rules

```text
ALBM  -> Base Color, sRGB on
NRMR  -> Normal, sRGB off, normal compression
ATOS  -> packed auxiliary data; never direct Emissive
EMI/ALP/ALBA -> Emissive only when MDF role and non-zero intensity confirm it
Tran / Dithered -> normally Masked/Dithered with documented opacity channel
```

If a populated StaticMesh slot still renders white, inspect the material graph for `/InterchangeAssets/gltf` placeholders before changing exposure.

## Lighting status gate

The Arcade lighting pass is incomplete unless the source region file has been scanned. The known Arcade source inventory includes 23 PointLight, 12 SpotLight, and 4 IESLight records in `l02_01_arcade.scn.19`, in addition to the 2 common DirectionalLight records. Do not replace this inventory with two DirectionalLights, one SkyLight, or temporary fixture lights.

## Final checks

Run the portable sample validator from the repository root:

```powershell
python scripts/validate_arcade_case.py
```

Then run `scripts/ue_arcade_validation.py` through UE Python/Remote Execution against `<level>`. The expected golden values are in `references/arcade-golden-result.json`.

Do not upload `.uproject`, `.umap`, `.uasset`, extracted DMC5 files, meshes, or textures to this public skill repository. Keep those in a private asset repository or local backup.
