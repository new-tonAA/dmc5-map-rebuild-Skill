---
name: dmc5-arcade
description: Reconstruct DMC5 / Devil May Cry 5 RE Engine maps in UE5 from SCN, mesh, MDF, and TEX assets. Use for DMC5 map extraction, location02 / M2, l02_01_arcade / Arcade, PropsLarge, transform assembly, material repair, texture import, or UE5 scene restoration.
metadata:
  short-description: DMC5 to UE5 arcade scene restoration
---

# Purpose

Use this skill for DMC5 RE Engine scene reconstruction in Unreal Engine 5, especially areas containing architecture, PropsLarge, roofs, signs, fake lights, and original materials.

This is a workflow skill, not an asset pack. It does not require a bundled `.uproject`, `.umap`, `.uasset`, extracted game files, textures, or meshes.

Before using it, define local paths for the target UE project, UE executable, DMC5 extraction, Blender REI add-on, and backup directory. Use placeholders such as `<UE_PROJECT>`, `<UE_ROOT>`, `<DMC5_EXTRACT>`, `<REI_ADDON>`, and `<BACKUP_ROOT>` in scripts and notes.

# Safety and scope

- Operate only on the user-selected `<UE_PROJECT>`.
- Before any Unreal operation, inspect `UnrealEditor.exe` command lines and refuse to kill, restart, or modify unrelated projects.
- Use a dedicated final level such as `/Game/Maps/M2_Arcade_Final`; do not continue old half-finished levels.
- Put backups under the user-selected `<BACKUP_ROOT>`.
- On a 4 GB GPU, validate one area at a time; do not open a total M2 overview or load all regions together.

# Proven workflow

1. Parse source meshes with the DMC5 REI Blender add-on using the matching mesh and MDF. Do not use `from_pydata` or temporary grid placement as the final export path.
2. Parse SCN resource paths and compose each `via.Transform` through its full parent chain. Place the UE actor using the resulting world transform, not the mesh origin or an arbitrary local transform.
   - With the source-to-UE basis `UE=(source X, source Z, source Y)`, convert source quaternion `(qx,qy,qz,qw)` to UE quaternion `(qx,qz,qy,-qw)`. The final `-qw` is required by the reflected basis.
   - A generated label such as `Arcade_Corrected_####` uses the sequential record index from the corrected instance JSON, not the SCN `object_index`.
3. Use source textures exported by REI only after checking them in Blender or as image files. Treat an unverified TEX decoder or noisy PNG as invalid.
4. Build or repair exact materials with this mapping:
   - `ALBM` -> Base Color, sRGB on.
   - `NRMR` -> Normal, sRGB off, normal-map compression.
   - `ATOS` -> alpha/transmission/occlusion-style inputs when supported; never connect it directly to Emissive.
   - `EMI`, `ALP`, or `ALBA` -> Emissive only when the MDF identifies that role.
   - Inspect the REI material shader type before choosing UE blend mode. A `Tran` / Transparent Shader material must not be left as UE Opaque. For glass, keep ALBM and NRMR as the surface maps, keep ATOS as packed data, and use a documented opacity approximation only when the original RE shader cannot be reproduced.
5. Inspect both StaticMesh material slots and material graph/instance parameters. A populated slot can still reference a bad glTF material or placeholder texture.
6. Replace legacy glTF materials that reference `T_White_srgb`, `T_Generic_N`, or other `/InterchangeAssets/gltf` placeholders.
   - Audit every submesh of every multi-part prop variant. A correct static/body variant does not prove that the full/exterior variant has correct material slots.
7. Treat `NullWhite` and `NullNormalRoughness` on dedicated illumination/fake-light materials as potentially valid; do not replace them blindly.
8. For texture review, use UE viewport `Unlit` / `无光照`:
   - `r.EyeAdaptation.CachedLightingPreExposure 8`
   - `r.LocalExposure 0`
   - `r.ExposureOffset 0`
9. Save all dirty assets and the level before a backup. Verify asset paths, material slots, texture references, actor count, bounds, transforms, and a viewport or Blender screenshot.
10. Restore intended scene lighting after diagnostic preview changes. The Arcade validation baseline is DirectionalLight intensity `4.0`, SkyLight intensity `0.35`, and indirect/volumetric scattering `1.0`; do not save temporary exposure tuning as final lighting.

# Validation gates

- Blender render shows recognizable building, ground, and walls without checker/noise artifacts.
- Every active StaticMeshActor has a valid mesh and intended material slot.
- Base Color points to an ALBM-like texture and Normal points to an NRMR-like texture unless intentionally untextured or emissive-only.
- PropsLarge and architecture both exist; the scene has at least 30 valid StaticMesh actors/instances.
- Actors are distributed at SCN-derived positions rather than stacked at one origin.
- No `Video memory exhausted` or bulk texture duplication occurs.

For the portable debugging history, read [references/arcade-case-study.md](references/arcade-case-study.md).
