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

## Required restoration order

1. Parse `l02_01_arcade.scn.19` with an RSZ object-table pass before full field decoding.
2. Decode Point/Spot/IES fields with the correct schema and preserve object index/name.
3. Compose each light Transform through its complete parent chain and convert with `UE=(source X, source Z, source Y)` and quaternion `(qx, qz, qy, -qw)`.
4. Group IES resources with their owning light; do not count an IES profile as an independent UE light if it is a component on the same GameObject.
5. Restore lights in small batches, starting with enabled Arcade fixtures and low-risk shadow settings.
6. After every batch, validate actor count, bounds, Lit/Unlit views, frame time, GPU memory, and forward-light warnings.

## Hardware warning

On a GTX 1650 4 GB, the current Arcade editor pass can already approach the practical memory limit when another UE project is open. Do not restore all 39 local Arcade Point/Spot/IES records in one blind batch. The `Video memory has been exhausted` warning is a hard stop for further lighting additions until the memory source is isolated.

The Lumen exposure/clipping warning and the ForwardShadingPriority warning are diagnostic signals, not evidence that the source lighting is complete. Keep Lumen/exposure console changes separate from saved source-light values.
