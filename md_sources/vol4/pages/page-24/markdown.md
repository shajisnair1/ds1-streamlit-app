## 2.5 Basic Calculation Notes

This section addresses design patterns that are common to the industry with common load rating processes used. The specialty tool manufacturer shall use these patterns if applicable when performing a Basic Load Rating. If a manufacturer uses a different load-rating process for a scenario substantially similar to one of these patterns, the vendor shall explain the inconsistency in the Design File for that tool.

## 2.5.1 Rotary-Shouldered Connections

Rotary-shouldered drill-stem connections, similar to API single-shouldered connections, carry stress from makeup torque and string tension in the same cross section (the pin neck). This means that, at some point, an increase in makeup torque may decrease the tensile capacity.

Any tool component that uses a rotary-shouldered connection shall calculate the tensile capacity of the connection as a function of the makeup torque applied to it, using the methods explained in the Overload Design chapter of DS-1 Volume 2 (based on industry-standard formulas given in API RP7G). Even connections that are not API connections (e.g. a tapered stub acme thread with a shoulder) shall have their combined load capacities calculated using the same methods.

The torsional capacity of a rotary-shouldered drill-stem connection shall be equal to the makeup torque applied to it (presuming no supplemental torque resistance is used, such as keys or set screws). Additional makeup of a rotary-shouldered connection downhole shall be considered a failure of the tool because of the heightened risk of damage to the connection that results.

## 2.5.2 Capacities for Cylinders

If a tool contains an essentially-cylindrical section that will be loaded in a mostly-uniform way, the vendor shall calculate the tensile, torsional, internal pressure yield, and external pressure resistance capacities using methods outlined for drill stem and OCTG components in API Technical Report 5C3. (Ductile rupture calculations from that standard are not allowed as pressure capacities in this standard, though they may be helpful for finding "emergency" load limits.)

## 2.6 FEA Methods (Advanced)

The following process shall be followed to obtain an Advanced Load Rating using Finite Element Analysis (FEA) techniques.

## 2.6.1 Perform a Basic Load Rating

In doing this, the Basic capacities for each critical location will be known, including the limiting location.

## 2.6.2 Identify Critical Locations for FEA

The limiting critical location shall be analyzed using FEA, as well as any other critical location with a Basic load capacity less than the limiting Basic Load Rating times 1.67. Rotary-shouldered drill-stem connections, due to the industry's familiarity with them, do not need to be modeled in FEA to complete an Advanced Load Rating in tension or torsion.

## 2.6.3 Perform FEA on Critical FEA Locations

The FEA model of each critical location identified in section 2.6.2 shall:

- Be an elastic-plastic material model, ideally with representative strain-hardening properties included.
- Accurately model the geometry of the critical location, using the tolerance limits that result in the lowest load capacity.
- Have a fine mesh in any areas of stress concentration, with gradual changes in the mesh density moving away from those locations if the mesh size changes in different parts of the model. (Mesh density convergence checks should be considered.)
- Accurately model the boundary conditions and applied loads at the critical location.
- Adequately account for friction at contact surfaces, if necessary.
- Adequately account for large-deformation nonlinearity, if necessary.

The capacity of each critical location shall be determined as the smallest of the following:

a. Global Failure: The load which results in overall structural instability, such that the average principal strain in any loaded cross section reaches 2%.
b. Local Failure: The load which causes the equivalent von Mises plastic strain at any point to exceed:

$$
\varepsilon_{\mathrm{peq}} = \min \left[ 0.1; 0.5 \cdot \left(\frac{\sigma_{\mathrm{g}}}{\sigma_{\mathrm{u}}}\right) \right] \tag{2.1}
$$

Where:

$\varepsilon_{\mathrm{peq}} =$ equivalent plastic strain

$\sigma_{\mathrm{g}} =$ specified minimum yield strength

$\sigma_{\mathrm{u}} =$ specified minimum ultimate strength