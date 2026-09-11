---
name: dmc5-arcade
description: Reconstruct DMC5 / Devil May Cry 5 RE Engine maps in UE5 from SCN, mesh, MDF, and TEX assets. Use for DMC5 map extraction, location02 / M2, l02_01_arcade / Arcade, PropsLarge, transform assembly, material repair, texture import, or UE5 scene restoration.
metadata:
  short-description: DMC5 to UE5 arcade scene restoration
---

# Purpose

Use this skill for DMC5 RE Engine scene reconstruction in Unreal Engine 5, especially areas containing architecture, PropsLarge, roofs, signs, fake lights, and original materials.

Lighting restoration is a separate, staged workstream. Do not describe an Arcade reconstruction as lighting-complete merely because a DirectionalLight, SkyLight, LUT, or a few helper lights are present. Read [references/arcade-lighting-status.md](references/arcade-lighting-status.md) before changing source lights.

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
   - Do not write prop-specific placement shortcuts with a positive `qw`. A hardcoded trailer rotation using `(qx,qz,qy,+qw)` produced a whole vehicle facing backward even though its position looked correct.
   - A generated label such as `Arcade_Corrected_####` uses the sequential record index from the corrected instance JSON, not the SCN `object_index`.
3. Use source textures exported by REI only after checking them in Blender or as image files. Treat an unverified TEX decoder or noisy PNG as invalid.
4. Build or repair exact materials with this mapping:
   - `ALBM` -> Base Color, sRGB on.
   - `NRMR` -> Normal, sRGB off, normal-map compression.
   - `ATOS` -> alpha/transmission/occlusion-style inputs when supported; never connect it directly to Emissive.
   - `EMI`, `ALP`, or `ALBA` -> Emissive only when the MDF identifies that role.
   - Preserve the REI/MDF emissive intensity. If Blender REI reports `Emissive_Intensity = 0.0`, do not directly connect the EMI/ALP/ALBA image to UE Emissive; keep it as a fake-inner/packed input or omit it in the UE approximation.
   - Inspect the REI material shader type before choosing UE blend mode. A `Tran` / Transparent Shader material should normally map to UE `Masked`/Dithered with a documented ATOS opacity channel, not automatically to `Translucent`. Keep ALBM and NRMR as the surface maps and never use packed ATOS RGB as Emissive.
   - When setting UE light colors through Python, remember `unreal.Color` is BGRA; source RGB `(r,g,b)` must be written as `unreal.Color(b,g,r,a)` and read back from the component for validation.
5. Inspect both StaticMesh material slots and material graph/instance parameters. A populated slot can still reference a bad glTF material or placeholder texture.
6. Replace legacy glTF materials that reference `T_White_srgb`, `T_Generic_N`, or other `/InterchangeAssets/gltf` placeholders.
   - Audit every submesh of every multi-part prop variant. A correct static/body variant does not prove that the full/exterior variant has correct material slots.
   - Never pair SCN material records with imported meshes using lexicographic order or only the first submesh number. Match the complete sanitized submesh tuple, such as `Submesh_-_10__0_0_0_10_` to `Submesh - 10 (0 0 0 10)`, then assign the corresponding material slot.
7. Treat `NullWhite` and `NullNormalRoughness` on dedicated illumination/fake-light materials as potentially valid; do not replace them blindly.
8. For texture review, use UE viewport `Unlit` / `无光照`:
   - `r.EyeAdaptation.CachedLightingPreExposure 8`
   - `r.LocalExposure 0`
   - `r.ExposureOffset 0`
9. Save all dirty assets and the level before a backup. Verify asset paths, material slots, texture references, actor count, bounds, transforms, and a viewport or Blender screenshot.
   - For multi-part vehicles, verify every submesh actor has the same SCN-derived world rotation and that representative interior, wheel, window, and shell pieces use the expected material family.
10. Audit the region-specific light SCN before claiming intended lighting is restored. Count `DirectionalLight`, `PointLight`, `SpotLight`, `IESLight`, `IBL`, `LightProbes`, and post-process objects from the RSZ object table, then parse relevant fields and full parent chains.
11. Keep diagnostic lighting and source-light restoration separate. The historical Arcade baseline of DirectionalLight `4.0`, SkyLight `0.35`, and indirect/volumetric scattering `1.0` is only a preview fallback, not proof of source-light parity.
12. When RE Engine fake-light materials cannot be reproduced, place a small number of low-intensity real lights at verified fixture/emissive actor centers only after the region light inventory is known. Keep them in a dedicated folder, avoid broad floodlights, disable unnecessary shadows on helper lights, and record every approximation as incomplete.
13. For vehicle lighting, read [references/arcade-vehicle-light-source-audit.md](references/arcade-vehicle-light-source-audit.md). Do not infer headlight PointLights/SpotLights from a mesh name, a material texture, or a visual screenshot. The Arcade source has two verified front-plane SpotLight records; convert their transform with `(qx, qz, qy, -qw)` and then apply the verified RE local `-X` to UE local `+X` axis correction. Do not apply that correction to unrelated SpotLights.
14. If the GTX 1650 target becomes overexposed or cyan-washed because IES profiles are unavailable, use a separate recorded compatibility override rather than changing the source manifest. Prefer reducing IES-as-PointLight fallbacks and repeated blue fixture fallbacks, then modestly raising SkyLight fill; do not touch the verified vehicle headlight source actors in a generic balance pass.
15. If the Arcade vehicle road remains black because source IBL/light-probe data is not yet imported, use at most a few explicitly labeled, low-intensity, no-shadow compatibility road-fill lights. Record their positions and remove them after IBL/probe restoration; do not treat them as source light parity.
16. For BC6H DMC5 Cubemaps that UE 5.8 Interchange rejects, extract the six cube faces, decode them to ordinary image data, rebuild a standard six-face DDS Cubemap, import it as `TextureCube`, and connect it to the region SkyLight. Keep the original `.tex.11` source and conversion manifest beside the target project; do not silently substitute a generic HDRI.
17. Treat `PZ_M02_arcade` post-process data as authoritative: DMC5 Arcade has `AutoExposure=0` and `EV=3`. Do not use broad UE Histogram exposure or subjective light scaling as the final restoration. Restore local source light parameters first; keep engine-equivalence mappings and unresolved IES/LightProbe work explicitly separate.
18. Audit every road/fixture group in the region SCN. For Arcade, explicit light count alone is insufficient: restore and validate `LP_M02_arcade`/`LP_M02_arcade_hokan` LightProbe coverage and distinguish normal `LC_M02_arcade00` from alternate/event cubemaps before concluding that a road is missing lights.
19. When extracting multi-image TEX Cubemaps, verify each face hash. Never assume a converter's `imageIndex` argument works; duplicate face hashes invalidate the environment and can make road lighting comparisons meaningless.
20. Diagnose apparent road/ground holes before adding mesh actors: audit the source environment mesh, every UE main-geometry submesh, material slots, and bounds first. For DMC5 pavement families using `AlphaTranslucentOcclusionSSSMap`, do not connect `ATOS.A` directly to UE `OpacityMask` unless source shader semantics and clip behavior are verified; low ATOS alpha can visually delete valid ground while the mesh actor is present. Use a new bounded opaque test parent, preserve AO from ATOS where appropriate, test only the exact pavement actors, and create PRE/POST backups.

# Recorded 2026-09-11 ground-gap and lighting boundary

- A perceived Street01 road/ground gap was not caused by a missing main environment mesh: source `l02_02_street01.scn.19` has one render mesh with five primary material slots, and UE contains all five corresponding geometry actors with valid meshes and source-derived textures.
- The visible holes were reproduced by the bounded Street geometry masked parent: pavement ATOS alpha was connected to `OpacityMask`, while source ATOS alpha was below `85` for about `51.37%` of `m02_pavement01` and `47.06%` of `m02_pavement02`; the user confirmed that the opaque diagnostic test removed the holes.
- The confirmed bounded state uses a new opaque test parent under `/Game/DMC5/M2/Materials/StreetGeometryTest/Street01OpaqueTest` on `11` non-dissolve pavement actors across Street01, Street02, and Street03. It excludes `pavement01_dissolve`, `l02_cliff_mat`, Arcade main geometry, and Arcade Props. Do not broaden it blindly: convert this diagnostic into a source-faithful graph only after ATOS semantic validation.
- The current lighting is not a game-light reproduction. `104/104` direct Point/Spot/IES actors have source-matched parameters, but `7` IES profiles remain unassigned; RE `IBL` AddBlend/trimming, LightProbe interpolation, `.prb.9` indirection, VLM behavior, and actual lit-render parity remain unresolved. Never summarize the current state as full lighting parity or compensate with broad helper lights.
- A bounded six-direction Ambient Cube candidate test may use the decoded `R9G9B9E5Sharedexp` values from `lp_m02_arcade.lprb.3` as no-shadow diagnostic directional lights. Keep direction order, unit conversion, and `.prb.9` interpolation explicitly unresolved; this is an environment-field experiment, not a source-exact light reproduction.

# Validation gates

- Blender render shows recognizable building, ground, and walls without checker/noise artifacts.
- Every active StaticMeshActor has a valid mesh and intended material slot.
- Base Color points to an ALBM-like texture and Normal points to an NRMR-like texture unless intentionally untextured or emissive-only.
- PropsLarge and architecture both exist; the scene has at least 30 valid StaticMesh actors/instances.
- Actors are distributed at SCN-derived positions rather than stacked at one origin.
- No `Video memory exhausted` or bulk texture duplication occurs.
- Source-light parity is not claimed unless region-specific Point/Spot/IES objects, IBL/reflection resources, LUTs, post-process zones, and parent-chain transforms have been audited.
- Vehicle-light parity is not claimed unless `trailer_emissivecontrol.clip`, the Arcade trailer MDF/material roles, and any scene/prefab light-component references have been audited.

For the portable debugging history, read [references/arcade-case-study.md](references/arcade-case-study.md).

For a one-pass reusable implementation, read [references/arcade-quickstart.md](references/arcade-quickstart.md), then compare against [references/arcade-golden-result.json](references/arcade-golden-result.json). Run `scripts/validate_arcade_case.py` before touching a UE project and `scripts/ue_arcade_validation.py` inside UE after assembly.
