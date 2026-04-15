# 5.7.16 Seal Width

Type: B

Basis: Minimum seal width is established to reduce the probability of leaking and galling at the seal surfaces.

Required: Minimum seal width is that which would result in a seal bearing pressure (at nominal makeup torque) equal to the yield stress of the tool joint or component material.

Reference: DS-1: Table 3.7.1-3.7.17 and 3.7.25-3.7.29, as applicable. RP7G-2: Paragraph 10.26.5.

Effects: A higher probability of connection leaks exists if seal width is not controlled.

Adjustment: None recommended.

Comments: Confusion often exists between shoulder width and seal width. Shoulder width (of the box) is the distance from the counterbore to the outside diameter of the box, neglecting bevel. Seal width (of the box) is the distance from the counterbore to the inside diameter of the bevel. Shoulder width is primarily a torsional strength issue, while seal width bears more on connection sealability.

The method by which the minimum seal width given in DS-1 Table 3.7.1 were calculated is as follows.

1. Seal radius.
$$
R_s = \frac{W_s + Q_s}{2} \tag{5.1}
$$

2. Seal area:
$$
A_s = \pi \left[ (W_s + Q_s) + W_s^2 \right] \tag{5.2}
$$

Where:
$Q_s$ = Box counterbore diameter (in)
$R_s$ = Seal radius (in)
$A_s$ = Seal area (in²)
$W_s$ = Minimum seal width (in)

Equations 5.1 and 5.2 are substituted into the torsional strength equation (equation A.14) and rearranged to produce a third-degree polynomial in terms of $W_s$. This equation is solved with an iterative technique to determine minimum seal width.

Seal width values in API RP7G-2 are arbitrarily set at the minimum box shoulder width less 3/64 inch.

Mechanism: Connection leak

Inspection: Dimensional 2 (Seal width is not measured in Dimensional 1 inspection.)

# 5.7.17 Shoulder Flatness

Type: C

Basis: Shoulders must be flat and perpendicular to the connection axis for uniform loading and adequate leak resistance.

Required: No visible gap is allowed when a straightedge and/or a flat plate is placed on the shoulder.

Reference: DS-1: Visual Connection Procedure RP7G-2: Paragraph 10.14.8.1.5. (DS-1 and RP7G-2 are identical.)

Effects: A connection's capacity to makeup and seal properly requires that the shoulders be flat and perpendicular to the connection axis.

Adjustment: None recommended.

Mechanism: Connection leak

Inspection: Visual Connection (Shoulder flatness is not measured in Dimensional 1 inspection.)

# 5.7.18 Pin Neck Length

Type: B

Basis: Excessive pin neck length may result from improper machining or excessive field relaxing.

Required: Pin neck length may not be more than the minimum counterbore depth on the mating box minus 1/16 inch. This ensures that box threads will always have full depth pin threads with which to mate.

Reference: DS-1: Dimensional 2 and Dimensional 3 inspection procedures. RP7G-2: Paragraph 10.26.5. (DS-1 and RP7G-2 are identical.)

Effects: If this dimension is too long, thread crests may not have mating pin thread roots. In that event, severe hoop stress would arise as box thread crests ride up onto the pin neck cylinder during makeup. Proper connection makeup would be impaired, and box failure by splitting would be much more likely.