# Appendix

## Strength and Design Formulas

Note: Equations A.1 through A.10 were adapted from Appendix A of API RP7G (reference 1).

## A.1 Makeup Torque Calculations for Rotary Shouldered Connections

Recommended makeup torque for rotary shouldered connections is the amount of torque required to achieve a desired stress level in the weaker member, pin or box. Makeup torque is calculated using Equation A.1:

$$
T = \frac{SA}{12} \left( \frac{P}{2\pi} + \frac{R_f}{cos\phi} + R_s t \right) \tag{A.1}
$$

Where:

- A = Smaller of pin or box cross-sectional area (in²)
- T = Makeup torque (ft·lb)
- S = Desired stress level from makeup (see below)

|  Connection | Desired Stress (psi)  |
| --- | --- |
|  Used tool joints | 72,000  |
|  New tool joints (break-in) | 72,000  |
|  PAC drill collars | 62,500  |
|  H-90 drill collars | 56,200  |
|  Other drill collars | 62,500  |

$$
A_b = 0.25\pi \left| OD^2 - (Q_c - E)^2 \right| \quad \text{(A.2)}
$$

$$
A_r = 0.25\pi \left| (C - B)^2 - [D^2] \right| \quad \text{(A.3)}
$$

$$
B = (H - 2S_0) + \frac{tpr}{96} \quad \text{(A.4)}
$$

$$
E = \frac{3tpr}{96} \quad \text{(A.5)}
$$

- H = Thread height (in) (API Spec. 7-2)
- $S_p$ = Root truncation (in) (API Spec. 7-2)
- P = Lead of threads (in)
- $R_t$ = Average mean radius of thread (in)
- $R_s$ = Mean shoulder radius (in)
- t = Coefficient of friction (assume 0.08)
- $\phi$ = 1/2 thread angle (API Spec. 7-2)
- $tpr$ = Thread taper (in/ft)

The variables $R_t$ and $R_s$ are calculated using the following equations:

$$
R_t = \frac{(Q_c + OD)}{4} \tag{A.6}
$$

The maximum value of $R_t$ is limited to the value obtained from the calculated OD where $A_p = A_r$.

$$
R_r = 0.25 \left| C + \left( C - (L_p - 0.625) + \frac{tpr}{12} \right) \right| \tag{A.7}
$$

Where:

- $Q_c$ = Box counterbore (in)
- $L_p$ = Length of pin (in)
- $C$ = Gage point pitch diameter (in)
- OD = Outside diameter (in)
- ID = Inside diameter (in)

## A.2 Drill Collar Bending Strength Ratio

The bending strength ratios in this standard were determined by application of the following equation:

$$
BSR = \frac{Z_b}{Z_r} - \left( \frac{D^2 - b^2}{D} \right) - \left( \frac{R^2 - d^2}{R} \right) \tag{A.8}
$$

Where:

- BSR = Bending Strength Ratio
- $Z_b$ = Box Section Modulus (in²)
- $Z_r$ = Pin Section Modulus (in²)
- D = Outside Diameter of Box (in)
- d = Inside Diameter of pin (in)
- b = Thread root diameter of box threads at end of pin (in)
- R = Thread root diameter of pin threads (in)

To use Equation A.8, perform the following calculations:

$$
\text{Dedendum} = (0.5H - f_{rn}) \tag{A.9}
$$

Where:

- H = Thread height not truncated (in) (API Spec. 7-2)
- $f_{rn}$ = Root truncation (in) (API Spec. 7-2)
- $b = C - \left[ \frac{tpr(L_{p1} - 0.625)}{12} \right] + (2 \cdot \text{dedendum}) \tag{A.10}
$$

Where:

- C = Pitch diameter (in)
- $tpr$ = Taper (inch per foot on diameter)
- $L_{p1}$ = Length of pin (in)
- $R = C - (2 \times \text{dedendum}) \cdot tpr / 96$

## A.3 Bevel Diameter

The maximum and minimum bevel diameters in this standard were determined using the following equations:

$$
BD = Q_c + 2W_s \tag{A.11}
$$

$$
W_s = \frac{Q_c}{2} \left| \sqrt{1 + \frac{4W_s}{Q_r}} - 1 \right| \tag{A.12}
$$