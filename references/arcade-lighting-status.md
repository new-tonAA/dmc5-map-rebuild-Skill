# Arcade Lighting Status

This reference records the current source-light inventory and prevents a diagnostic approximation from being mistaken for a DMC5 lighting restoration.

## Verified source inventory

For `location02`:

- `light/l02_common.scn.19`: 2 `via.render.DirectionalLight`, 3 `via.render.IBL`, and 3 `via.render.LightProbes`.
- `light/l02_01_arcade.scn.19`: 23 `via.render.PointLight`, 12 `via.render.SpotLight`, 4 `via.render.IESLight`, and 2 `via.render.LightProbes`.
- `location02_light.scn.19`: post-process zones and LUT references; it is not the complete local-light inventory.
- Other region light files contain additional Point/Spot/IES records and must not be loaded together on a 4 GB GPU.

The Arcade source therefore has substantially more explicit lighting than a UE level containing only two DirectionalLights and one SkyLight. The object counts above are RSZ class-instance counts; before spawning UE actors, resolve GameObject/component grouping, enabled state, parent chain, color, intensity, radius, cone angles, IES resource, and shadow flags.

## Current UE state

The safe diagnostic pass may contain:

- 2 converted DirectionalLights from `l02_common.scn.19`.
- The existing low-intensity SkyLight/IBL approximation.
- An imported/default LUT and post-process metadata.
- No temporary fixture lights unless explicitly recorded as an approximation.

This state is **not source-light parity**. It is only a controlled baseline for material and scene validation.

The current staged Arcade pass has 42 UE Light actors: 2 DirectionalLights, 1 existing SkyLight, and 39 local Point/Spot actors. The 23 PointLight and 12 SpotLight records are represented with source positions, colors, intensities, ranges, cone angles, and selected shadows. The 4 IESLight records are currently PointLight approximations because both UE 5.8 AssetTools and Interchange attempts returned no `TextureLightProfile` asset. This pass must remain marked incomplete until the IES profiles are imported or a validated equivalent is built.

## Required restoration order

1. Parse `l02_01_arcade.scn.19` with an RSZ object-table pass before full field decoding.
2. Decode Point/Spot/IES fields with the correct schema and preserve object index/name.
3. Compose each light Transform through its complete parent chain and convert with `UE=(source X, source Z, source Y)` and quaternion `(qx, qz, qy, -qw)`.
4. Group IES resources with their owning light; do not count an IES profile as an independent UE light if it is a component on the same GameObject.
5. Restore lights in small batches, starting with enabled Arcade fixtures and low-risk shadow settings.
6. After every batch, validate actor count, bounds, Lit/Unlit views, frame time, GPU memory, and forward-light warnings.

The first batch may use source-candela values with inverse-square falloff and disable low-impact shadows on a GTX 1650. Record that shadow policy as an approximation; do not silently turn it into a final parity claim.

## Lumen and ray-tracing decision

DMC5 source resources explicitly contain `Raytracing`, `ForceDisableRayTracing`, `OnlyRTSwitch`, `OptionRayTracing`, and `app.RayTracingMissionOptionOverwriter` records. The mission override exposes diffuse/specular resolution and specular secondary-bounce controls, including `Disable`, `Enable`, `Half`, and `Original` states.

This is an original DMC5 ray-tracing system, not UE5 Lumen GI. The DMC5 enum `via.render.LightPowerUnitType.Lumen` is only a photometric unit name and must not be confused with Lumen global illumination. It is valid to disable Lumen in the UE target for a 4 GB GPU, especially when the target editor reports Lumen exposure clipping or memory pressure. Keep these target-only console settings separate from source lighting data:

```text
r.Lumen.Reflections.Allow 0
r.Lumen.DiffuseIndirect.Allow 0
r.DynamicGlobalIlluminationMethod 0
r.ReflectionMethod 0
```

Disabling Lumen is a hardware compatibility choice, not proof that the scene's source GI, IBL, probes, or local lights are restored.

Do not claim that turning off UE Lumen reproduces DMC5's ray-tracing-off mode. If source RT parity is required, record the DMC5 RT switch/mission override separately and map it to UE ray-tracing, reflections, shadows, and post-process features as distinct decisions.

## Source-authoritative Arcade baseline

The `PZ_M02_arcade` post-process record is now decoded from `location02_light.scn.19`:

- `AutoExposure = 0`; the original Arcade zone does not use dynamic auto exposure.
- `EV = 3`.
- `BrightAdaptationRate = 0.03` and `DarkAdaptationRate = 0.05` are retained as source metadata, but are inactive when `AutoExposure = 0`.
- `MaxWhitePoint = 5`, `MinWhitePoint = 3.5`, and `WhiteRange = 0.95` remain source tone-mapping metadata pending a dedicated UE curve mapping.

The target UE post-process maps this to Manual exposure with bias/EV `3.0` and `r.LocalExposure 0`. This is a source-driven baseline, not a visual brightness adjustment.

All 39 Arcade local-light actors now restore source intensity, BGRA-corrected color, derived effective range, spot cone/spread, source radius, and source shadow flags. Their validation is saved in `Saved/source_light_parity_validation.json` and currently reports zero parameter errors. Four IES actors remain approximate only because the original IES profile path is not yet attached in UE.

Do not use `arcade_lighting_balance_override.json` or `final_environment_light_balance.json` as source truth. Those records describe prior diagnostic experiments. The authoritative local-light state is `Saved/arcade_source_light_values_restored.json`.

## Parameter parity

- Local Arcade Point/Spot records currently preserve source intensity and color; 35 non-IES range mappings also match after the source-meter to UE-centimeter conversion.
- The two common DirectionalLight colors and quaternions are preserved, but their UE intensity is intentionally normalized and must not be called numerically identical.
- IES profile application remains unresolved when UE AssetTools/Interchange produces no `TextureLightProfile`; keep those four lights marked as approximations.
- Unreal Python `unreal.Color` uses BGRA constructor order. Convert source RGB as `Color(b, g, r, a)` and validate actual component `r/g/b` values after saving.
- Do not map `ReferenceEffectiveRange` directly to the UE attenuation radius for every light. When `IlluminanceThreshold` is available, derive an effective source range with `sqrt(Intensity / IlluminanceThreshold)` in source units and use the larger of that value and `ReferenceEffectiveRange`; direct `v11` mapping made several 50k-candela lights look too bright with 2–4 m cutoffs.
- The source trailer `Headlight` material is `Transparent` with `headlight_ATOS` and shader-controlled emissive parameters; the static `_light` material is `DefS` with `light_ALBM` and no emissive map. Two source Arcade SpotLights at object indices `178` and `182` are positioned on the trailer front plane and are restored as the vehicle headlight light actors with the verified RE local `-X` axis correction. Read [references/arcade-vehicle-light-source-audit.md](arcade-vehicle-light-source-audit.md).
- `trailer_emissivecontrol.clip` is a material/animation-control resource that still needs curve/property decoding; it is not a license to add real lights.

## Hardware warning

On a GTX 1650 4 GB, the current Arcade editor pass can already approach the practical memory limit when another UE project is open. Do not restore all 39 local Arcade Point/Spot/IES records in one blind batch. The `Video memory has been exhausted` warning is a hard stop for further lighting additions until the memory source is isolated.

The Lumen exposure/clipping warning and the ForwardShadingPriority warning are diagnostic signals, not evidence that the source lighting is complete. Keep Lumen/exposure console changes separate from saved source-light values.

## Conservative UE balance layer

When the GTX 1650 target shows white clipping in the Arcade corridor or a cyan wash, do not overwrite the DMC5 source manifest. The target may use a separately recorded balance layer while IES profiles are unresolved:

- Reduce cyan IES-as-PointLight fallbacks strongly; the missing IES angular profile can make a 100,000-candela source appear as an omnidirectional blue flood.
- Reduce repeated blue PointLight fixtures only as a target-side compatibility override, keeping their source RGB/intensity in `dmc5_arcade_local_lights_applied.json`.
- Reduce nearby high-intensity white SpotLight fallbacks that produce local clipping.
- Raise SkyLight modestly for environment fill instead of adding a broad high-intensity floodlight.
- Never alter the two source-backed vehicle headlight SpotLights `037/038` as part of this generic balance pass.

The current target override is saved as `Saved/arcade_lighting_balance_override.json`. It is diagnostic/compatibility tuning, not numeric DMC5 parity. Remove or revise it after validated IES profiles, light probes, or RE post-process exposure are restored.

The target also has three explicitly labeled `M2_Arcade_RoadFill_00..02` low-intensity, no-shadow compatibility lights along the vehicle road. They compensate for the currently missing IBL/light-probe fill and are not counted as source Arcade lights. Keep them separate so they can be removed after the source environment resources are imported.

The saved post-process keeps Histogram exposure but reduces adaptation speed up/down to `0.5`; this limits visible exposure pumping without pretending that UE's exposure model is DMC5's.

The target now has a converted Arcade local cubemap at `/Game/DMC5/M2/Lighting/IBLTest/Arcade00_Cube`, connected to `M2_Arcade_SkyLight`. It was built from `lc_m02_arcade00.tex.11` by extracting six BC6H faces, decoding them with Blender, and rebuilding a standard six-face DDS Cubemap because the custom UE 5.8 Interchange path rejects BC6H DDS input. The source `IBL_M02_00/01` resources and `LP_M02_overall00/01` probe data are still not fully mapped; the cubemap is an environment-fill restoration pass, not complete LightProbe parity.

After the cubemap is active, remove the temporary `M2_Arcade_RoadFill_*` lights and retune local source-light scales against the environment. A black vehicle rear/corridor is no longer proof that another arbitrary PointLight is missing; check the cubemap, probe data, local light scale, and post-process exposure first.

The full Arcade source coverage audit is saved as `Saved/arcade_all_road_source_coverage.json`. It confirms 39 explicit lights are distributed across `display01`, `display02`, `display03`, `display04`, the `OCC_arcade00` fixture group, and the unnamed/street/vehicle group. It also confirms two Arcade LightProbe objects: `LP_M02_arcade` and `LP_M02_arcade_hokan`, both using `LP_M02_arcade.lprb` plus `LP_M02_merge_net.prb`. The three dark roads should be diagnosed against this probe coverage, not by assuming the `display01` walkway lights represent the whole map.

`LC_M02_arcade00`, `LC_M02_arcade01`, and `LC_M02_arcade_event` are distinct source cubemap states. Keep `arcade00` as the normal Arcade baseline; do not globally substitute the alternate or event cubemap.
