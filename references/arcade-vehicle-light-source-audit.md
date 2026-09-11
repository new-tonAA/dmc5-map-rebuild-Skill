# Arcade Vehicle Light Source Audit

This reference prevents invented vehicle lights from being mistaken for DMC5 source parity.

## Verified Arcade resources

The resource table of `l02_01_arcade_propslarge.scn.19` directly references:

- `Props/mesh/sm7000_trailer/sm7000_trailer.mesh`.
- `Props/mesh/sm7000_trailer/sm7000_trailer_mat.mdf2`.
- `Props/mesh/sm7000_trailer/sm7000_trailer_Static.mesh`.
- `Props/mesh/sm7000_trailer/sm7000_trailer_Static_mat.mdf2`.
- `Props/mesh/sm7000_trailer/trailer_emissivecontrol.clip`.

That Arcade resource table does **not** directly reference `sm7000_trailer_entrance_emissive.mesh` or its material file. The entrance-emissive asset exists in the extracted game files, but its existence alone is not evidence that it belongs in the Arcade map.

The same Arcade scene's resource table contains no `via.render.Light` component for the trailer. The explicit Arcade light inventory remains the separate `l02_01_arcade.scn.19` inventory: 23 PointLights, 12 SpotLights, and 4 IESLights.

## Material and animation evidence

- `sm7000_trailer.mesh` contains `_Headlight`, `_neon_light1`, and `_neon_light2` mesh/material groups.
- The normal Arcade trailer MDF identifies `_Headlight` with `headlight_ATOS`, a `Character_EmissiveSpreadAnim_Transparent` shader family, and shader-controlled emissive color/intensity parameters. A static REI import can report zero effective output when the runtime control is not evaluated; the MDF and clip must be read together.
- The Arcade static `_light` material uses `light_ALBM` and has no verified emissive output.
- `trailer_emissivecontrol.clip` contains `ClipTrack`/`ClipGroup` data targeting `sm7000_trailer_UI` and `sm7000_trailer`, with `Mesh`/`Materials` tracks and `ValueF` entries. This is material/animation-control metadata, not proof of a source PointLight or SpotLight. Decode its curve/property IDs before reproducing any animated glow.
- The separate `sm7000_trailer_entrance_emissive` material file uses emissive shader families and neon submeshes, but it must remain excluded from Arcade until a scene/prefab reference is found.

## Verified vehicle SpotLight axis

The two Arcade `30000` SpotLight records at source object-table indices `178` and `182` sit on the trailer's front plane, with a shared source X position and two source Z positions separated across the vehicle width. They are the source-backed vehicle headlights, not invented helper lights.

Their transform quaternion conversion remains `(qx, qz, qy, -qw)`, but the verified vehicle headlight emission axis is local `-X`. UE's `SpotLightComponent` emits along actor local `+X`. Therefore the UE actor rotation must apply a local 180-degree yaw correction after the reflected-basis quaternion conversion:

```text
q_ue = (qx, qz, qy, -qw)
q_vehicle_spot = q_ue * Quaternion(local yaw 180 degrees)
```

The corrected UE forward vectors are approximately `[0.029255, -0.976645, -0.212861]` and `[0.065283, -0.975371, -0.210689]`, matching the trailer's UE forward direction `[0.082724, -0.996573, 0]` within the source headlight pitch.

Do not apply this vehicle-axis correction blindly to every DMC5 SpotLight. Classify the light by its source fixture/object relationship first. The nearby `SpotLight_nico` record is not included in the two-headlight correction.

The clip parses as DMC5 Clip version 27 with `1030` frames, `4` timeline tracks, `14` properties, and `220` keys. It has two `Mesh` tracks under `sm7000_trailer_UI` and `sm7000_trailer`, each with three animated `Materials` entries and `ValueF` curves. Frame-zero values are `5.0`, `2.8`, and `0.4`; the current UE material pass maps these, by the three dynamic trailer material groups, to `_neon_light1`, `_neon_light2`, and `_Headlight` respectively. This material-group mapping is source-order based and remains a validation item for event playback.

The current UE pass restores source texture roles without adding invented vehicle helper lights:

- `_neon_light1` -> `neonsign_ALP`, source color `(0, 0.0509804, 0.2039216)`, clip frame-zero intensity `5.0`.
- `_neon_light2` -> `NeonTest_ALBA`, clip frame-zero intensity `2.8` and source `EmissiveColorControl=0.7`.
- `_Headlight` -> `headlight_ATOS` mask, source high-color white, clip frame-zero intensity `0.4`.
- `_ExteriorShell_02` -> `ExteriorShell_02_EMI`, source color `(0, 0.2, 1)`, source emissive intensity `1.0`.
- `_lamp` remains non-emissive because its source `Emissive_Intensity` and control are `0.0`.

Generic corridor balance changes must not modify the two source-backed vehicle headlight actors. If the rear of the vehicle remains dark, investigate camera side, source light direction, IBL/light-probe fill, and post-process exposure before adding any invented rear light.

The current target uses three separate `M2_Arcade_RoadFill_*` compatibility lights for the missing vehicle-road environment fill. These are not vehicle light actors and must not be confused with the two source-backed headlight SpotLights.

The current saved pass removes those temporary road-fill actors after connecting the converted `Arcade00_Cube` environment to `M2_Arcade_SkyLight`. The remaining vehicle-road mismatch is now tracked as incomplete IBL/LightProbe/post-process parity rather than an unverified vehicle helper-light problem.

The current source-authoritative pass restores the original Arcade local-light parameters and uses the decoded `PZ_M02_arcade` manual exposure baseline. Do not reintroduce subjective local-light scales while comparing the vehicle or its road.

The vehicle-road comparison must include both source Arcade probe objects. `LP_M02_arcade` is centered near the trailer/Arcade area, while `LP_M02_arcade_hokan` is a second coverage object with a different source flag and spacing value. A missing probe-equivalent can make three roads dark even when all 39 explicit local lights are present.

The normal `LC_M02_arcade00` LocalCubemap is now rebuilt with distinct source faces. Its earlier duplicate-face conversion was invalid and must not be used for vehicle-road comparisons.

## UE reconstruction rule

- Do not add vehicle headlight SpotLights or PointLights from visual guesses. The Arcade target uses only the two source-backed records at object indices `178` and `182`.
- Keep all other vehicle source-light additions blocked unless the SCN/prefab/event data identifies an actual light component or verified fixture relationship.
- Reproduce the Arcade vehicle first with the exact mesh/material/ATOS data and the decoded `trailer_emissivecontrol.clip` behavior.
- Only after a source-backed local-light relationship is confirmed may a small UE light be added, and it must record the source object/resource, transform chain, color, intensity, radius, and approximation status.
- If the source evidence remains material-only, document the remaining difference rather than compensating with a broad or bright helper light.

## Current target state

The target UE map has no `M2_DMC5_VehicleHeadlight_*` approximation actors. The two source-backed Arcade SpotLights at indices `178` and `182` remain under the normal `M2_DMC5_LocalLight_*` naming. The saved validation state is 483 total actors, 440 StaticMeshActors, and 42 LightActors (2 DirectionalLights, 1 SkyLight, and 39 Arcade local-light representations). Lumen remains disabled only as a UE hardware choice; MegaLights is untouched.
