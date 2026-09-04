# Portable Arcade Case Study

This document records a successful DMC5 M2 Arcade reconstruction without including copyrighted game assets or a machine-specific UE project.

## Portability

- The user supplies the UE project, DMC5 extraction, REI add-on, Blender, and backup paths.
- Use placeholders such as `<UE_PROJECT>`, `<DMC5_EXTRACT>`, `<REI_ADDON>`, and `<BACKUP_ROOT>`.
- Do not commit `.uproject`, `.umap`, `.uasset`, extracted DMC5 files, meshes, or textures to a public Skill repository unless the distributor has the necessary rights and explicitly wants a separate asset repository.
- The Skill itself only needs workflow instructions, diagnostics, and optional scripts. The UE level is not required for Skill invocation.

## Material failure and fix

The most visible white surfaces were not primarily exposure or VRAM problems. Seven trailer submeshes still used legacy glTF-created MaterialInstance assets referencing placeholder textures such as:

- `/InterchangeAssets/gltf/Textures/T_White_srgb`
- `/InterchangeAssets/gltf/Textures/T_Generic_N`
- `/InterchangeAssets/gltf/Textures/T_White_Linear`

The StaticMesh slots appeared populated but rendered as white or black placeholder surfaces. The fix was to re-export the trailer materials through REI, import the corresponding source textures, enable the correct texture switches, and assign the real textures to the material-instance parameters.

The repaired material roles included:

- Exterior shell: `exteriorshell_02_albm`, `exteriorshell_02_nrmr`, `exteriorshell_02_emi`.
- Lamp: `glass_ex_albm`, `glass_ex_nrmr`, `glass_ex_emi`.
- Headlight: `light_albm`, `headlight_atos`.
- Glass and seat: corresponding `glass_ex_*` and `_3_seat01a_*` textures.
- Neon: `neonsign_albm`, `neonsign_nrmr`, with `neonsign_alp` or `neontest_alba` according to the MDF role.

Do not connect `ATOS` directly to Emissive. This washes out the model.

The trailer window needed a separate correction. REI reports `sm7000_trailer.mesh - _Exteriorshell_glass_ex` as `Tran` / Transparent Shader, while earlier UE repairs alternated between Opaque and Translucent. The validated approximation is:

- `glass_ex_albm` -> Base Color, sRGB on.
- `glass_ex_nrmr` -> Normal, sRGB off, normal compression.
- `glass_ex_atos` -> packed data, sRGB off; use its documented opacity-channel approximation for UE masked/dithered rendering rather than treating the whole RGB image as Emissive.
- UE material blend mode -> Masked/Dithered with clip value around `0.333`; use low glass roughness and validate in Unlit and Lit views.

This is a shader-equivalence fix, not an exposure fix. The Blender REI importer sets this family to Dithered; do not choose Translucent solely because the material name contains `glass`.

The full trailer also exposed a variant-audit failure: seven exterior meshes still referenced `/InterchangeAssets/gltf/MI_Default_Opaque` even though the static trailer pieces had correct materials. Count every mesh under each prop variant and verify every StaticMesh slot independently.

## Rotation assembly failure and fix

Repeated walls, signs, and windows appeared in the correct positions but faced backward. The source-to-UE conversion used the wrong reflected-basis quaternion. The incorrect conversion was:

```text
(qx, qz, qy, qw)
```

The validated conversion is:

```text
(qx, qz, qy, -qw)
```

Apply it consistently to generated PropsLarge actors. Do not globally add an arbitrary 180-degree rotation; some mesh families have legitimate different orientations. Verify representative wall, sign, roof, and window families with an Unlit A/B preview.

Keep the sequential generated record number separate from the SCN `object_index`. Mixing those identifiers can update the wrong actor.

## Missing-map diagnosis

The target Arcade scene is normally one DMC5 region, for example `l02_01_arcade`. Neighboring regions such as `l02_02_street01` are separate scene files. A missing neighboring region is not proof that the target SCN parser dropped geometry.

Check these separately:

1. SCN resource-table mesh count.
2. Extracted mesh file existence.
3. Corrected JSON record count.
4. UE StaticMeshActor count.
5. World bounds and camera coverage.

## Preview settings

For reliable texture inspection:

```text
r.EyeAdaptation.CachedLightingPreExposure 8
r.LocalExposure 0
r.ExposureOffset 0
```

Then use `Unlit` / `无光照`. Lit mode is for lighting review; cached lighting can make correct materials appear black or white.

After preview tests, restore saved scene lighting instead of leaving diagnostic values in the level. The Arcade baseline used here is DirectionalLight `4.0`, SkyLight `0.35`, and indirect/volumetric scattering `1.0`.

The Arcade common-light SCN could not be safely converted into complete UE point/spot lights because its RSZ parse was unreliable. The practical fallback is two low-intensity PointLights placed at the verified `sm0131_illumination` fixture centers, stored under a dedicated converted-fake-lights folder. Do not compensate for missing fake lights with a broad high-intensity floodlight.

## Private backup recipe

Save all dirty assets and the level, then copy project content to a private, user-controlled backup location such as `<BACKUP_ROOT>`:

- `<UE_PROJECT>/Content/Maps/<FINAL_LEVEL>.umap`
- The project content required by the reconstruction.

Keep a manifest with the project path, level path, timestamp, and material fixes. Do not place these project/game assets in the public Skill repository.
