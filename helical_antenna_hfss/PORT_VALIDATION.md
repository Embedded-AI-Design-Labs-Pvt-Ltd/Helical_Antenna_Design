# Port Validation

## Missing from the source document

Coax geometry, dielectric, connector, reference impedance, port sheet size, integration line, feed gap, ground thickness.

The 50 Ω lumped port is an **ENGINEERING_ASSUMPTION**, not a source parameter.

## First-pass checks (after the model is built in HFSS)

1. PortSheet is a 2-D sheet in the XZ plane at the helix radius.
2. Integration line lies on PortSheet, from ground (z = 0) to helix start (z = 1.50 mm).
3. P1 impedance is 50 Ω, renormalize enabled.
4. FeedPost does not fuse the helix solidly into the ground (that would short the port).
5. P1 is inside RadBox.
6. Port validation / characteristic impedance in HFSS (after solve) is **NOT SIMULATED** until Analyze.

## Replacing with a coaxial feed

When drawings exist:

1. Delete P1 and PortSheet.
2. Model inner, dielectric, shield with measured radii.
3. Hole the ground plane for the shield.
4. Wave port or lumped port on the coax face.
5. Integration line inner → outer.
6. Re-solve. Do not keep lumped-gap S11 as if it were the connector model.

Details: `docs/feed_and_port.html`, `hfss/ports/port_definition.json`.
