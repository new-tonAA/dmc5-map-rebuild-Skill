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
- The normal Arcade trailer MDF identifies `_Headlight` with `headlight_ATOS` and a `Character_EmissiveSpreadAnim_Transparent` shader family, but the REI audit reports `Emissive_Intensity = 0.0` for the Arcade `_Headlight` material.
- The Arcade static `_light` material uses `light_ALBM` and has no verified emissive output.
- `trailer_emissivecontrol.clip` contains `ClipTrack`/`ClipGroup` data targeting `sm7000_trailer_UI` and `sm7000_trailer`, with `Mesh`/`Materials` tracks and `ValueF` entries. This is material/animation-control metadata, not proof of a source PointLight or SpotLight. Decode its curve/property IDs before reproducing any animated glow.
- The separate `sm7000_trailer_entrance_emissive` material file uses emissive shader families and neon submeshes, but it must remain excluded from Arcade until a scene/prefab reference is found.

## UE reconstruction rule

- Do not add vehicle headlight SpotLights or PointLights from visual guesses.
- Keep vehicle source-light actor count at zero unless the SCN/prefab/event data identifies an actual light component or a verified fixture relationship.
- Reproduce the Arcade vehicle first with the exact mesh/material/ATOS data and the decoded `trailer_emissivecontrol.clip` behavior.
- Only after a source-backed local-light relationship is confirmed may a small UE light be added, and it must record the source object/resource, transform chain, color, intensity, radius, and approximation status.
- If the source evidence remains material-only, document the remaining difference rather than compensating with a broad or bright helper light.

## Current target state

The target UE map has no `M2_DMC5_VehicleHeadlight_*` approximation actors. After removal, the saved validation state is 483 total actors, 440 StaticMeshActors, and 42 LightActors (2 DirectionalLights, 1 SkyLight, and 39 Arcade local-light representations). Lumen remains disabled only as a UE hardware choice; MegaLights is untouched.
