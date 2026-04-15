These specifications may be internal to the manufacturer or standard to the industry.

At a minimum, the material specification for a load-bearing component shall contain:

- Specified Minimum Yield Strength (SMYS)
- Specified Minimum Tensile Strength
- Ductility (% elongation)
- Specified Minimum Charpy V-Notch Impact Energy if the tool rotates with the drill string during operation (the specification shall also define the specimen size, specimen orientation, and test temperature for the Charpy test)

## 2.2.4 Customer Access

The customer or its authorized representative shall, upon request, have access to the Design File, including the calculation methods, the calculation or modeling results, and the referenced material specification documents. However, these documents are to be considered intellectual property and may not be copied or removed from the premises.

## 2.3 Basic and Advanced Load Ratings

This standard defines two categories of load-rating methods: Basic and Advanced. A Basic Load Rating is calculated using straightforward hand calculations, without taking stress concentration or large deflections into account. As the complexity of a tool increases, the Basic Load Rating is less likely to be accurate, but it may be adequate for a tool that is rarely if ever loaded near its capacity.

An Advanced Load Rating is intended to provide greater confidence in the accuracy of the capacity determination. It uses either Finite Element Analysis (FEA) or proof-load testing to determine the appropriate load rating. Though not required, manufacturers should consider providing an Advanced Load Rating if the specialty tool contains complex geometry and is routinely loaded above 60% of its Basic Load Rating. A manufacturer may provide the Advanced Load Rating of its own initiative or at the request of a customer.

## 2.4 Basic Calculation Process

The Basic Load Rating shall be calculated using the following process for every load case of interest.

### 2.4.1 Determine the Load Path

Identify and list each component in the specialty tool that will aid the tool in carrying the load of interest.

### 2.4.2 Define the Material Properties

For each load-bearing component, identify the required material specification as described in section 2.2.3 and list the provided SMYS.

### 2.4.3 Identify Critical Locations

For each load-bearing component, identify and list critical locations that need to have their load capacities calculated in order to determine the overall tool load capacity. This requires some engineering judgment from the tool designer, but generally:

- In tension and torsion load ratings, each component will have a "connection" on both ends to transfer load to the previous and next components in the load path. These may be typical threaded connections or some other means of load transfer (shoulders, splines, etc). These are always critical locations.
- In tension and torsion load ratings, a component may have a cross-sectional area reduction in the body of the component (stem holes, ring grooves, etc). The severest reduction in cross-sectional area in a given component is another critical location.
- In pressure load ratings, each component will have at least one "connection" where there is a potential leak path due to a break in the solid material that is sealed with threads, elastomers, or some other means. These are always critical locations.
- In pressure load ratings, each component will also carry pressure through simple material resistance. The "body" of the component is also a critical location.

### 2.4.4 Calculate Critical Location Capacities

At each of the critical locations identified above, calculate the load rating for that location using methods appropriate to the load type and the location. (See section 2.5 for specific design patterns.)

### 2.4.5 Identify the Limiting Component

The lowest rating from all the critical locations in the load path represents the final Basic Load Rating for the tool.

### 2.4.6 Prepare the Design File

The design file as described in section 2.2.2 shall contain all the drawings, material specification references, notes, calculations, and explanations needed to support and recreate the final Basic Load Rating.