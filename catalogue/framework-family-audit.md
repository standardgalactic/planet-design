# Framework Family Audit (8% cap)

Scope: all 440 catalogue entries, each assigned to exactly one family by its Framework field. Cap: no family above 8% of the catalogue, which is at most 35 entries.

## Result

Under this 26-family taxonomy **no family exceeds the cap**. The largest are Optimization, search and scheduling (35), Bayesian updating, bias and sampling (31), Dynamics, feedback and oscillation (28). Optimization sits exactly at the cap (35 of 440, 7.95%) with no headroom, and Bayesian has 4 spare. Any added or reassigned entry in Optimization breaches the cap, so that family is closed to new entries.

| Rank | Family | Entries | Share | Headroom to 35 |
|---|---|---|---|---|
| 1 | Optimization, search and scheduling | 35 | 8.0% | 0 |
| 2 | Bayesian updating, bias and sampling | 31 | 7.0% | 4 |
| 3 | Dynamics, feedback and oscillation | 28 | 6.4% | 7 |
| 4 | Game theory and strategic interaction | 25 | 5.7% | 10 |
| 5 | Logic, computation and formal languages | 24 | 5.5% | 11 |
| 6 | Graphs, networks and topology | 23 | 5.2% | 12 |
| 7 | Coding, cryptography and information | 21 | 4.8% | 14 |
| 8 | Institutions, culture and social relation | 20 | 4.5% | 15 |
| 9 | Language, meaning and convention | 17 | 3.9% | 18 |
| 10 | Symmetry, groups and algebra | 17 | 3.9% | 18 |
| 11 | Statistics: distributions, power laws and extremes | 17 | 3.9% | 18 |
| 12 | Inverse problems and inference from traces | 16 | 3.6% | 19 |
| 13 | Growth, decay and population dynamics | 15 | 3.4% | 20 |
| 14 | Thresholds, tipping points and cascades | 14 | 3.2% | 21 |
| 15 | Fair division, allocation and social choice | 14 | 3.2% | 21 |
| 16 | Queues, flows and throughput | 14 | 3.2% | 21 |
| 17 | Geometry, space and scale | 13 | 3.0% | 22 |
| 18 | Physical and engineering limits | 13 | 3.0% | 22 |
| 19 | Measurement, error and uncertainty propagation | 13 | 3.0% | 22 |
| 20 | Economics: value, scarcity and externalities | 13 | 3.0% | 22 |
| 21 | Coordination, protocols and distributed knowledge | 12 | 2.7% | 23 |
| 22 | Identity and continuity | 11 | 2.5% | 24 |
| 23 | Causal inference and performative feedback | 11 | 2.5% | 24 |
| 24 | Memory, cognition and embodied skill | 11 | 2.5% | 24 |
| 25 | Number, notation and calendars | 6 | 1.4% | 29 |
| 26 | Infinity, limits and continuity | 6 | 1.4% | 29 |
| | **Total** | **440** | 100% | |

## What the result depends on

The cap test is only as strict as the taxonomy is fine. The same catalogue gives different answers at different granularities, so the taxonomy has to be fixed before the cap means anything.

- **Inference and evidence (merging 4 families):** 75 entries, 17.0%. Breaches the cap if read as one family.
- **Dynamical systems (merging 3 families):** 57 entries, 13.0%. Breaches the cap if read as one family.
- **Strategic and economic structure (merging 4 families):** 64 entries, 14.5%. Breaches the cap if read as one family.

The inference cluster is the one to watch. The catalogue leans on evidence, selection and reconstruction as a motif, so a reviewer who treats those as one family would find about 17% of the catalogue in it. If the 8% cap is meant to protect against that kind of dominance, the taxonomy should be agreed on those terms. This audit uses the finer split because the families differ in the mathematics they actually require (Bayes' rule, inverse problems, causal graphs and heavy-tailed statistics are different tools).

## Method and its limits

- Each entry was given one family, assigned from its Framework text by keyword rules in priority order, then every assignment was read and corrected by hand. 22 entries matched no rule and were assigned by hand, and about 20 more were reassigned after review (for example a keyword match on "graph" inside "autobiographical").
- Single assignment hides overlap. Many entries belong to two families (for example 17.01 temporal sampling is both inverse-problem and sampling). A multi-label count would be higher for every family.
- The assignment uses the Framework field only. It does not test whether two entries with different framework labels dramatise the same story shape.
- Conceptual (C) entries are spread over Language, Identity, Institutions, Memory and Economics families, so the cap is tested for them too, but they are the least reliably categorised.
- Cycle 01 entries use a slightly different line format ("| Scale M") and were parsed together with the rest. All 440 matched.

## Recommendations

1. Adopt this 26-family list as the operational definition for the cap.
2. Treat Optimization (35, at cap) as closed and Bayesian (31) as near cap. Replacement entries should come from lower-count families such as Number and calendars, Infinity and limits, Identity, Causal inference or Memory.
3. Resolve the inference cluster question explicitly, since it is the one place where the answer changes with the reading.
4. Run the second audit (graphic treatments, the Look field) before committing the other five slate projects.
5. Keep the CSV beside the catalogue so the check can be rerun after any edit.

## Slate projects by family

- 01.01 The Department of Unclaimed Rooms: Language, meaning and convention
- 03.01 The Last Projectionist: Inverse problems and inference from traces
- 04.01 The Society for Perfect Endings: Logic, computation and formal languages
- 07.01 The Whale Beneath the Railway: Optimization, search and scheduling
- 08.01 Seven Minutes of Summer: Optimization, search and scheduling
- 11.01 A Country Made of Footnotes: Logic, computation and formal languages

Two pairs of slate projects share a family: 07.01 and 08.01 (Optimization), and 04.01 and 11.01 (Logic and formal languages). Optimization is at the cap, so one of 07.01 or 08.01 is a candidate for a different framing if any entry has to move. Otherwise the slate spans four families.

## Full assignment by family

### Optimization, search and scheduling (35)

- 01.20 Zoning the Dead: packing problems
- 03.02 The Ferry Without a River: optimal stopping
- 03.05 The Lighthouse Keeper's Shift Table: constraint satisfaction
- 03.07 The Cobbler of the Closed Mill: local versus global optima
- 03.14 The Night Watchmen's Round: art gallery theorem, coverage
- 03.15 The Salt Road Porters: knapsack and packing
- 05.09 The Dam's Operating Manual: minimax decisions under uncertainty
- 05.16 The Elevator to Nowhere: reachable states
- 07.01 The Whale Beneath the Railway: network dependence, constrained optimization
- 08.01 Seven Minutes of Summer: bounded reachability
- 09.02 Pilgrim's Shortest Road: traveling salesman, heuristics
- 09.03 The Repair Fleet: scheduling
- 09.06 The Lighthouse Circuit: Chinese postman problem
- 09.08 The Ferrymen of the Lagoon: state-space search
- 09.15 The Homing Pigeons' Map: gradient following
- 10.12 The Money Changers' Loop: arbitrage, negative cycles
- 10.20 The Last Ferry Home: interval scheduling
- 11.13 The Translation Tournament: optimization with competing objectives
- 13.12 The Expedition That Turned Back: optimal stopping, option value
- 13.14 The Factory’s Shorter Day: productivity curves, fatigue
- 14.01 The Woman Who Returned the Sun: scheduling, precedence constraints
- 14.03 The Minotaur of Building C: partially observable search
- 14.04 Twelve Tasks Before Closing: resource-constrained scheduling
- 14.09 The Stone on the Loading Ramp: potential functions, progress measures
- 14.11 The House of Opened Gifts: irreversible decisions, option value
- 15.02 A Door Wide Enough: constraint satisfaction, inclusive design
- 15.14 The Stair Count: path cost, heterogeneous metrics
- 16.12 The Marriage of Separate Calendars: periodic scheduling, institutional time
- 16.14 The Two Authors of One Ending: constraint negotiation, incompatible objectives
- 17.03 The House of Impossible Statements: satisfiability, minimal inconsistent subsets
- 20.06 The Detective of Missing Socks: combinatorics, search-space reduction
- 20.07 The Town That Optimized Its Picnic: multi-objective optimization, Pareto efficiency
- 21.02 The Room That Forgets One Object: finite memory, eviction policies
- 21.19 The Orchard of Branching Days: branching time, irreversible choice
- 22.17 Three Journeys of the Same Distance: heterogeneous path costs

### Bayesian updating, bias and sampling (31)

- 01.11 The Water Tower Census: sampling and survivorship bias
- 02.01 The Lodger's Arithmetic: Bayesian updating under filtered evidence
- 02.12 The Cellar Census: capture and recapture estimation
- 03.13 The Almanac Compilers: forecast calibration
- 04.03 The Court of Small Probabilities: base rates, prosecutor's fallacy
- 04.07 The Laboratory of Replicated Results: multiple comparisons
- 04.16 The Inspectorate of Honest Mistakes: error types
- 04.17 The Bell Curve Tribunal: regression to the mean
- 06.02 The Seed Vault Expedition: sampling, representativeness
- 06.11 The Bone Counters: minimum number of individuals
- 06.15 The Typology Wars: clustering, classification
- 06.18 The Reconstruction Committee: overfitting
- 06.20 The Last Dig Season: Bayesian search
- 10.18 The Interpreter at the Gate: base rates, false matches
- 12.01 The Census of Closed Curtains: missing-not-at-random data
- 12.02 The Photograph’s Other Edge: framing, evidential selection
- 12.03 The Catalogue of Almost Matches: entity resolution, nontransitive similarity
- 12.04 The Five Who Agreed: correlated evidence
- 12.07 The Archive Fire Lottery: survivorship bias
- 12.09 The Museum of Borrowed Faces: classification thresholds, asymmetric error costs
- 12.13 The Historian’s Favourite Century: selection bias, denominator neglect
- 12.16 The Unopened Boxes: value of information, search costs
- 16.11 The Roommate’s Probability: Bayesian inference, differing priors
- 17.05 The Inspector’s Elegant Theory: overfitting, model selection
- 17.06 The Duplicate Confession: source dependence, textual copying
- 17.08 A Fingerprint for Every Passenger: multiple testing, false discovery
- 17.09 The Map of Accusations: observation bias, spatial intensity
- 20.19 The Fortune-Teller’s Calibration Party: calibration, sharpness
- 20.20 The Museum of Successful Failures: hindsight bias, selection effects
- 21.17 The Carnival of Incompatible Chances: probability coherence
- 22.11 The Photograph before It Was Taken: framing, collective production

### Dynamics, feedback and oscillation (28)

- 01.02 Municipal Weather: feedback and control
- 01.12 Rotary: fixed-point theorems
- 02.08 The House That Settled: attractors, fixed points
- 02.09 Three Clocks in the Hall: coupled oscillators, synchronization
- 05.01 The Pump That Counts: feedback, limit cycles
- 05.05 The Seawall Engine: Fourier analysis, tidal harmonics
- 05.06 The Orrery Mechanic: gear ratios, continued fractions, resonance
- 05.07 A Radio That Hears Itself: positive feedback, oscillation
- 07.04 The Moss Cartographers: reaction-diffusion patterns
- 07.05 The Tide Pool Republic: Lotka-Volterra predator-prey cycles
- 07.12 A Garden of Slow Predators: separation of timescales
- 07.15 The Coral Zoning Board: bistability, tipping points
- 08.05 The Long Dark Rota: entrainment of oscillators
- 08.06 Thaw Season Ferries: hysteresis, phase change
- 08.13 The Forecast Office at the End of the Line: chaos, sensitive dependence
- 08.15 Tides Without a Moon: resonance, forced oscillation
- 08.20 The Aurora Watchers: excitable systems
- 09.09 The Caravan Without a Leader: flocking, alignment dynamics
- 10.09 The Migration of the Quiet Language: Schelling segregation
- 15.16 The Tailor’s Moving Client: tracking, delayed feedback
- 16.08 The Musician and the Metronome Maker: synchronization, expressive deviation
- 16.20 The Distance That Kept Them Close: coupling strength, interaction dynamics
- 18.17 The City That Paid for Applause: positional goods, feedback
- 19.09 The Farm beyond the Tipping Point: bistability, hysteresis
- 20.14 The Orchestra of Independent Conductors: conflicting controllers, coupled systems
- 21.08 The River Running through Its Own Source: fixed points, self-consistency
- 21.10 The Town of Delayed Reflections: delay systems, stale observations
- 22.04 The Building across Four Seasons: coupled processes, timescale separation

### Game theory and strategic interaction (25)

- 01.05 Traffic That Remembers: Braess's paradox, equilibrium
- 02.07 The Thermostat War: repeated games, tit-for-tat
- 03.16 The Piece-Rate Choir: incentives, principal and agent
- 07.02 The Lichen Parliament: stag hunt, mutualism
- 07.17 The Bird Language Interpreters: honest signaling, handicap principle
- 09.16 The Salt Water Diplomat: bargaining, alternating offers
- 09.17 The Crossing Council: coordination games, focal points
- 10.06 The Smuggler's Gradient: inspection games
- 11.03 The Silence Clause: signaling games, strategic silence
- 13.06 The Treaty’s Third Signatory: coalition games, bargaining power
- 13.15 The Newspaper That Printed the Retraction: reputation, informational cascades
- 13.20 The Peace That Changed Its Conditions: repeated games, equilibrium stability
- 16.01 The Apartment of Two Temperatures: bargaining, asymmetric preferences
- 16.05 The Friend Who Always Agreed: preference falsification, relational uncertainty
- 16.10 The Gift Ledger: reciprocity, non-equivalent exchange
- 16.15 The Honest Surprise: information asymmetry, consent
- 16.16 The Friendship after the Contest: zero-sum episodes, continuing relationships
- 17.14 The Honest Pair of Liars: strategic communication, incentive compatibility
- 18.02 The Auction of Unwritten Books: common-value auctions, winner’s curse
- 18.03 The Price of Standing First: all-pay auctions, rent dissipation
- 18.04 The Shop That Raised Its Prices Kindly: signaling, price-quality inference
- 18.05 The Currency of Favours: obligation networks, reciprocity
- 18.08 The Queue Outside the Empty Shop: informational cascades
- 18.11 The Prize for Being Second: mechanism design, strategic response
- 18.12 The Landlord’s Perfect Tenant: adverse selection, screening

### Logic, computation and formal languages (24)

- 01.16 The Block That Wouldn't Die: cellular automata
- 02.16 Liars at the Breakfast Table: logic puzzles, truth-teller and liar
- 04.01 The Society for Perfect Endings: termination conditions, definitions of completion
- 04.02 The Ministry of Lost Appeals: halting problem
- 04.05 The Committee on Committees: recursion, self-reference
- 04.08 The Registry of Names: self-reference, barber paradox
- 04.09 The Department of Forms: formal grammars
- 04.11 The Auditors of the Moon: infinite regress of verification
- 05.03 The Loom with Memory: programmable machines, universal computation
- 05.13 The Vending Oracle: finite state machines
- 05.14 The Rail Signal Box: Boolean logic, deadlock
- 10.03 The Customs House Contradiction: inconsistent rule sets
- 10.10 A Citizen of the Empty Set: domains, partial functions
- 10.16 The Two-Way Bridge: mutual exclusion, deadlock
- 11.01 A Country Made of Footnotes: formal languages, interpretive context
- 11.04 The Dictionary of Forbidden Examples: extensional and intensional definitions
- 11.09 The Two Grammars of Winter: ambiguity in formal grammars
- 14.05 The Thread Seller: graph traversal, external memory
- 14.15 The Seamstress’s Endless Cloth: recursion, base cases
- 17.07 The Locked Room’s Open Window: model checking, omitted transitions
- 20.09 The Restaurant of Random Seating: randomized algorithms, probabilistic guarantees
- 20.13 The Accountant’s Imaginary Goat: abstraction, category errors
- 21.07 The Palace of Unfinished Proofs: proof obligations, conditional conclusions
- 22.19 The Last Light in Each Room: terminal actions, closure conditions

### Graphs, networks and topology (23)

- 01.03 The Sewer Cartographers: graph coloring
- 01.04 A Bridge for Every Sunday: Eulerian paths
- 01.06 The Parish of Bells: Voronoi partitions
- 01.09 Fifty Floors of Rumour: percolation, epidemic thresholds
- 01.17 The Last Stop on the Loop: topology, orientability
- 02.05 The Dinner Table Problem: independent sets, graph constraints
- 06.14 The Layer of Ash: cross-dating, dependency graphs
- 07.03 The Orchard of Borrowed Bees: nested bipartite networks
- 07.14 The Last Pollinator Guild: network robustness, extinction cascades
- 10.01 The Checkpoint at Two Villages: connectedness, enclaves
- 10.07 The Enclave Postal Service: graph connectivity
- 10.14 The Lighthouse Zone: medial axis, equidistance
- 12.10 The Last Address Book: temporal graphs
- 12.14 The Family Tree with a Loop: directed acyclic graphs, inconsistent constraints
- 13.02 The Bridge That Was Never Built: network topology, accessibility
- 17.12 The Chain of Custody Dinner: provenance graphs, broken continuity
- 19.01 The Last Bus on Tuesday: accessibility thresholds, dependency networks
- 19.05 The Shop after Its Customers Left: network effects, critical participation
- 19.18 The Bridge Closed for Good: cut sets, network resilience
- 21.18 The House with Two Interiors: topology, local and global structure
- 21.20 The Sleeper Who Could Change One Rule: rule systems, dependency consequences
- 22.03 The Journey of the Red Coat: temporal paths, contact networks
- 22.18 The Quilt of Unfinished Tasks: dependency networks, distributed continuation

### Coding, cryptography and information (21)

- 01.13 The Night Clerks of the Central Library: sorting cost, information entropy
- 02.04 Grandmother's Recipe, Corrupted: noisy channels, error correction
- 02.17 The Thin Walls: information leakage, signal and noise
- 03.03 The Telegraph Operators' Last Message: coding theory
- 05.04 The Dial Telephone Valley: numeral systems, pulse coding
- 05.18 The Lock Maker's Pins: combinatorial keyspaces
- 05.19 The Printing Press Chain: copying fidelity, exponential spread
- 06.05 The Museum of Receipts: compression, lossy records
- 06.07 The Interpreter of Ruined Alphabets: frequency analysis, decipherment
- 06.10 The Time Capsule Dispute: channel coding across time
- 09.05 Translators on the Slow Boat: channel capacity with delay
- 10.15 The Language of Stamps: checksums, error detection
- 11.05 A Message in Eleven Pieces: secret sharing, threshold reconstruction
- 11.06 The Festival of Misheard Names: noisy channels, decoding ambiguity
- 11.11 The Village of Short Names: prefix-free codes, unique decoding
- 11.15 The Password of the Bereaved: authentication, replay attacks
- 11.19 The Letter That Could Not Be Shortened: incompressibility, description length
- 15.11 The Braille Printer’s Apprentice: coding under physical constraints
- 17.02 The Perfect Alibi Machine: cryptographic commitments, evidential scope
- 19.08 The Library’s Final Catalogue: information preservation, operational access
- 19.15 The Archive’s Expiring Key: cryptographic access, key loss

### Institutions, culture and social relation (20)

- 04.19 The Hospital Triage Tribunal: competing ethical frameworks
- 06.08 The Cairn of Standard Gauge: path dependence
- 12.05 The Index of Erased Occupations: ontology design, archival visibility
- 13.04 The Loom Patent Refused: path dependence, institutional selection
- 13.18 The Observatory’s Wrong Appointment: discovery processes, institutional access
- 14.02 Orpheus at the Answering Service: grief, mediated presence
- 14.06 Persephone’s Second Address: role conflict, negotiated belonging
- 14.14 The Fire Taken Home: diffusion of innovation, complementary resources
- 14.20 The Flood Story Club: cultural transmission, adaptive retelling
- 15.07 The Prosthetic Workshop’s Promise: participatory design, situated expertise
- 16.07 The Promise with No Deadline: liveness, unspecified obligations
- 17.04 The Crime That Changed Names: institutional classification, retrospective judgment
- 17.10 The Restorer’s Invisible Repair: authenticity, provenance, intention
- 17.20 The Acquittal Nobody Understood: burdens of proof, epistemic and legal conclusions
- 18.07 The Replica with Better Memories: authenticity, experiential value
- 19.11 The Marriage of Unpaid Repairs: accumulated obligations, relational maintenance
- 19.17 The Last Edition of the Local Paper: public knowledge, shared attention
- 20.10 The Man Who Outsourced His Apologies: delegated action, relational sincerity
- 20.15 The Auctioneer Who Sold Silence: scarcity by convention, institutional enforcement
- 22.06 The Room between Performances: invisible labor, conditions of appearance

### Language, meaning and convention (17)

- 01.01 The Department of Unclaimed Rooms: map versus territory, classification
- 06.06 Scholars of the Traffic Light: signs, symbol grounding
- 06.17 The Burial of the Standard Meter: conventions and units
- 11.02 The Interpreter’s Missing Word: lexical gaps, paraphrase
- 11.07 The Last Fluent Sister: distributed linguistic knowledge
- 11.10 The Messenger Who Never Lies: pragmatics, implicature
- 11.12 The Courtesy That Closed the Door: speech acts, institutional authority
- 11.14 Names for the Same Mountain: reference, situated description
- 11.16 The Child Who Corrected the Map: prototypes, category boundaries
- 11.18 The Choir of Separate Meanings: conceptual alignment, apparent agreement
- 11.20 The Gesture Returned: embodied convention, contextual meaning
- 13.13 The Schoolhouse with Two Languages: language policy, institutional reproduction
- 15.17 The Workshop of Quiet Signals: interoception, interpretive uncertainty
- 16.09 The Language They Built Together: emergent convention, private shorthand
- 16.17 The House of Different Silences: communication norms, ambiguous behavior
- 19.12 The Island That Lost Its Translation: interpretive infrastructure, institutional access
- 22.08 The Bell Passed from Hand to Hand: convention, changing authority

### Symmetry, groups and algebra (17)

- 02.02 Seven Keys to One Door: permutations, cycle structure
- 02.03 The Wallpaper Group: plane symmetry groups
- 02.11 The Mirror Cousin: chirality, symmetry
- 02.14 The Landlady's Ledger: invariants, conservation
- 09.20 The Closed Route: cyclic groups
- 10.02 Passport of Nine Names: equivalence classes
- 12.12 The Duplicate Children: counting with overlapping sets
- 12.18 The Archive That Forgot Its Order: permutations, sequence-dependent meaning
- 20.01 The Mayor’s Unsortable Parade: partial orders, topological sorting
- 20.02 The Society of Unlucky Hats: derangements
- 20.05 The Baker’s Noncommutative Breakfast: noncommutative operations
- 20.17 The Tailor of Reversible Trousers: reversible transformations, information loss
- 21.05 The Forest of Identical Entrances: symmetry, indistinguishability
- 21.06 The Sleeper’s Conservation Law: invariants
- 21.09 The Garden of Negative Flowers: signed quantities, cancellation
- 21.14 The Library of All Rearrangements: permutations, semantic constraints
- 21.16 The Dreamer’s Undo Tax: reversibility, residual state

### Statistics: distributions, power laws and extremes (17)

- 02.13 Hand-Me-Downs: Markov chains, stationary distributions
- 02.15 The Birthday House: birthday paradox
- 03.04 The Typesetter's Alphabet: permutations, frequency distributions
- 03.08 The Ledger Keepers of a Vanished Bank: Benford's law
- 03.17 The Apprentice Who Outlived the Trade: power law of practice
- 05.12 The Weighing Machine of Saint Ardel: noise averaging, law of large numbers
- 05.20 The Last Spare Part: Poisson failures, reliability
- 06.03 Rival Readings of the Plastic Strata: law of superposition
- 06.16 The Fossil Keyboard: Zipf's law
- 08.04 The Hundred-Year Flood Committee: return periods, extreme value statistics
- 08.14 The Dust Year: diffusion, random walks
- 08.17 The Hail Insurers: heavy tails, ruin
- 10.05 A Border Drawn with a Ruler: fractal dimension, coastline paradox
- 15.04 The Uniform Maker: distributions, multivariate variation
- 17.11 The Number That Accused Him: Benford analysis, diagnostic limits
- 17.16 The Thief of Almost Nothing: cumulative sums, sequential detection
- 20.11 The Village’s Most Average Citizen: multivariate averages

### Inverse problems and inference from traces (16)

- 03.01 The Last Projectionist: inverse problems, underdetermination
- 05.15 The Mechanical Turk's Heirs: observational equivalence, hidden operators
- 06.01 The Parking Lot Temple: abductive inference, priors
- 06.09 The Excavation of a Shopping Mall: underdetermination of function
- 06.13 The Radio Silence Fellowship: absence of evidence
- 06.19 The Hall of Misattributed Tools: equifinality, form versus function
- 12.08 The Ten-Year Blank: interpolation, non-identifiability
- 12.11 The Deposition of the Empty Chair: absence of evidence, search adequacy
- 12.20 The Day They Recorded Everything: observability, measurement limits
- 17.01 The Verdict in the Missing Frame: temporal sampling, underdetermination
- 17.17 The Scene Rebuilt for the Jury: sensitivity analysis, reconstruction assumptions
- 22.02 One Street, Forty Mornings: repeated observation, latent change
- 22.13 The Map Folded Forty Times: representation damage, recoverability
- 22.14 The Night of Separate Windows: local knowledge, incomplete observability
- 22.15 The Rehearsal in Reverse: dependency reconstruction, causal direction
- 22.16 The Square after Everyone Leaves: traces, inference without presence

### Growth, decay and population dynamics (15)

- 02.19 A Quiet Inheritance of Debt: exponential growth, compounding
- 04.15 The Pension Fund's Long Dinner: compounding, time inconsistency
- 06.04 The Dig at Lot 12: radioactive decay, half-life
- 07.07 The Fig Wasp Treaty: coevolution, Red Queen dynamics
- 07.09 Rivers That Keep Accounts: mass balance, nutrient cycling
- 07.13 The Salt Marsh Census: species-area relationship
- 07.16 The Migrating Forest: dispersal, travelling waves
- 07.18 The Beaver Engineers: niche construction
- 07.19 The Plague of Helpful Species: logistic growth, Allee effects
- 07.20 The Quiet Meadow Under the Parking Lot: seed banks, bet-hedging
- 09.04 A Cargo of Seeds: founder effect, genetic drift
- 09.11 The Closed Ark: minimum viable population
- 09.14 The Medicine Boat: exponential decay, rationing
- 13.11 The Quarantine That Opened Early: epidemic dynamics, decision uncertainty
- 16.02 Letters with Different Horizons: discounting, intertemporal choice

### Thresholds, tipping points and cascades (14)

- 01.10 The Tenants of the Fault Line: self-organized criticality
- 03.12 The Chimney Sweeps of the Gas City: cascading failure
- 04.14 The Office of Permanent Temporary Measures: hysteresis, ratchet effects
- 05.10 The Furnace Inheritance: phase transitions, annealing
- 07.06 The Wolves of the Underground Station: trophic cascades
- 08.08 Heat Dome Etiquette: nonlinear thresholds
- 08.10 The Monsoon Calendar: bifurcation, onset
- 08.19 The Orchard That Lost Its Winter: threshold accumulation, degree-days
- 10.17 The Quarantine Line: SIR models, reproduction thresholds
- 19.04 The Reservoir’s Last Useful Inch: nonlinear constraints, thresholds
- 19.13 The Farewell Scheduled Too Late: deadlines, irreversible state transitions
- 19.14 The Market after the Last Stall: coordination, threshold participation
- 19.20 The Ending That Left a Door: terminal states, residual capabilities
- 22.12 The Orchard’s Empty Year: delayed effects, accumulated conditions

### Fair division, allocation and social choice (14)

- 01.15 The Stairwell Committee: social choice, Arrow's impossibility
- 02.06 Whose Turn to Wash: fair division, envy-freeness
- 02.18 The Spare Room Lemma: Hall's marriage theorem
- 04.20 The Republic of Alphabetical Order: agenda-setting, ordering effects
- 10.13 The Mountain Pass Lottery: random allocation, fairness
- 10.19 The Territory of Overlapping Claims: cake cutting, fair division
- 13.09 The Station Built on the Other Bank: spatial allocation, agglomeration
- 13.10 The Election with Another Agenda: Condorcet cycles, sequential voting
- 13.17 The Census That Counted Children: apportionment, representation
- 15.10 The Runner’s Hidden Reserve: constrained optimization, resource allocation
- 15.12 The Queue for Sitting Down: allocation under unequal need
- 16.04 The Shared Garden Boundary: fair division with heterogeneous values
- 18.16 The Heir to the Waiting List: tradable access, allocation rules
- 18.18 The Wedding of Equal Contributions: proportionality, unequal capacity

### Queues, flows and throughput (14)

- 03.06 The Elevator Attendants: queueing theory
- 03.10 The Switchboard Women: circuit versus packet routing
- 04.10 The Ombudsman's Waiting Room: priority inversion, queues
- 04.18 The Procurement of Ladders: bullwhip effect
- 07.11 The Mycelial Telegraph: network flow
- 08.11 Drought Arithmetic: stocks and flows
- 10.08 The Visa Queue: Little's law
- 13.05 The Harbour Without a Toll: congestion, externalities
- 13.16 The Canal with a Different Lock: bottlenecks, throughput
- 14.18 The Feast That Never Ended: replenishment, throughput constraints
- 18.06 The Debt That Arrived Early: liquidity constraints, timing
- 19.07 The Winter They Spent the Buffer: reserve depletion, stochastic demand
- 22.05 A Day in the Water’s Account: conservation, stocks and flows
- 22.10 The Queue from Every Position: queueing, unequal waiting experience

### Geometry, space and scale (13)

- 01.14 The Hyperbolic Quarter: hyperbolic geometry
- 03.11 The Mapmaker's Last Contract: projection distortion, curvature
- 04.13 The Academy of Proportion: square-cube law
- 05.17 The Siren Test: Doppler shift
- 08.02 The Fog Ledger: attenuation, Beer-Lambert law
- 08.09 The Lightning Rod Wars: field geometry, point discharge
- 08.18 The Sundial Dispute: equation of time, solar geometry
- 09.07 The Long Way Around Cape Nothing: great circles, spherical geometry
- 09.10 Letters from the Outbound: light-time delay
- 09.19 The Unmapped Meridian: coordinate conventions
- 10.11 The Boundary Conditions: boundary value problems
- 15.08 The Weight of the Giant Costume: square-cube scaling, mechanical advantage
- 21.01 The City of Borrowed Lengths: metric spaces, changing distance

### Physical and engineering limits (13)

- 03.09 The Rope Walkers' Guild: stability, inverted pendulum
- 03.18 The Clock Winders: conservation of energy, impossibility of perpetual motion
- 03.19 The Stoker's Apprentice: Carnot limits, thermodynamic efficiency
- 08.03 The Wind Tax: Betz limit
- 08.12 The Snow Surveyors: angle of repose, stability thresholds
- 08.16 The Greenhouse Town: energy balance, steady states
- 14.07 The Man Who Held Up the Ceiling: load paths, structural redundancy
- 14.16 The Boy with the Wax Badge: operating envelopes, safety margins
- 15.18 The Wheelchair on the Sand Road: robust design, environmental variability
- 19.02 The Factory That Kept Its Lights: viability constraints, admissible degradation
- 19.10 The Theatre without a Back Door: safety invariants, single-point failure
- 19.16 The Town That Sold Its Spare: redundancy, fault tolerance
- 20.08 The Groom’s Backup Groom: redundancy, common-mode failure

### Measurement, error and uncertainty propagation (13)

- 03.20 The Retired Calculators: error propagation
- 04.06 The Bureau of Standard Weights: measurement, calibration chains
- 04.12 The Parliament of Rounding: rounding error, aggregation
- 05.02 Lathe No. 9: tolerances, error accumulation
- 06.12 The Atlas of Wrong Maps: datum and coordinate error
- 09.01 The Return Voyage of the Mapless: dead reckoning, error accumulation
- 09.12 The Navigator's Table of Stars: interpolation, tabulated functions
- 12.17 The Memorial of Rounded Numbers: uncertainty propagation, interval estimates
- 13.08 The Missing Zero in the Treasury: positional notation, error propagation
- 15.03 The Dancer’s Borrowed Balance: sensor fusion, weighted estimation
- 15.06 The Mirror Measurement: measurement error, proxy selection
- 20.18 The Clerk Who Rounded Himself Up: discrete allocation, rounding rules
- 21.15 The Village That Changes Scale: dimensional analysis, scaling relations

### Economics: value, scarcity and externalities (13)

- 04.04 The School That Taught the Test: Goodhart's law
- 07.10 The Pasture Commons Revisited: commons governance
- 13.19 The Inheritance Divided Equally: wealth dynamics, initial conditions
- 14.08 The Golden Touch Account: commodification, incommensurable values
- 14.10 The Apple at the Reunion: positional competition, scarce recognition
- 14.12 The Boatman’s Subscription: cross-subsidy, budget constraints
- 18.01 The Collector’s Last Empty Shelf: marginal utility, changing preferences
- 18.09 The Subscription Nobody Used: sunk costs, prospective choice
- 18.10 The Market for Certainty: risk pooling, correlated losses
- 18.13 The Cost of the Free Workshop: externalities, hidden resource transfers
- 18.14 The Merchant of Limited Editions: scarcity, endogenous value
- 18.15 The Bargain Beneath the Floorboards: opportunity cost, complementarity
- 18.20 The Object Everyone Wanted to Give Away: negative value, disposal constraints

### Coordination, protocols and distributed knowledge (12)

- 01.19 The Clock Tower That Disagrees: distributed time, consensus
- 07.08 The Termite Archivists: stigmergy
- 11.08 Instructions for a Stranger: common knowledge, coordination
- 11.17 The Unfinished Conversation: interactive protocols, acknowledgement
- 12.06 A Ledger with Two Histories: append-only records, provenance
- 13.03 A Calendar Adopted Too Soon: coordination costs, standards adoption
- 13.07 The Well That Stayed Public: institutional commons, credible commitments
- 15.19 The Breath Between Lines: temporal coordination, adaptation
- 16.19 The Agreement to Disagree Tomorrow: revision rules, dynamic commitments
- 17.18 The Signature Borrower: authorization, scope of delegation
- 19.19 The Festival Nobody Could Restart: coordination capital, interrupted traditions
- 20.12 The Queue Jumpers’ Association: coordination failure, positional competition

### Identity and continuity (11)

- 02.20 The Heirloom Ship: identity under replacement
- 12.19 The Name on the Wrong Grave: identity criteria, evidential conflict
- 15.13 The Actor’s Second Voice: identity, social recognition
- 15.15 The Body Double Contract: resemblance, substitutability
- 15.20 The Portrait That Would Not Sit Still: dynamic identity, representation
- 16.18 The Shared Object: identity, attachment, stewardship
- 17.19 The Case of the Returning Object: state identity, reversible transformations
- 21.12 The Island of Perfect Copies: personal identity, branching continuity
- 22.01 The Life of a Borrowed Cup: object biography, situated value
- 22.09 Seven Repairs to One Chair: identity under transformation, maintenance
- 22.20 A World Carried Forward: continuity through transformation, selective inheritance

### Causal inference and performative feedback (11)

- 08.07 The Rainmakers' Guild: confounding, causal inference
- 13.01 The Letter Delivered Before Dawn: causal models, interventions
- 14.17 The Three Fates of the Tailoring Shop: prediction, intervention, causal feedback
- 17.13 The Defendant of Tomorrow: prediction, performative feedback
- 17.15 The Accident with Three Causes: causal attribution, explanatory plurality
- 18.19 The Resale of Tomorrow: expectations, speculative feedback
- 20.04 The Committee for Spontaneous Fun: performative contradiction, institutional scripting
- 20.16 The Emergency Rehearsal Emergency: simulation fidelity, intervention effects
- 21.04 The Market Where Tomorrow Is Visible: strategic anticipation, reflexive prediction
- 21.13 The Weather of Forgotten Promises: state dependence, latent variables
- 22.07 Variations on a Missed Train: causal counterfactuals, branching structure

### Memory, cognition and embodied skill (11)

- 12.15 The Testimony Rehearsal: reconstructive memory, social influence
- 14.13 Echo in the Call Centre: recognition, scripted interaction
- 14.19 The Messenger’s Borrowed Shoes: affordances, person-environment fit
- 15.01 The Hand That Learned Twice: motor learning, transfer
- 15.05 The Marathon of Small Repairs: pacing, fluctuating capacity
- 15.09 The Piano with Unequal Keys: embodied skill, environmental adaptation
- 16.03 The Couple Who Remembered Opposite Days: autobiographical memory, salience
- 16.06 Two Maps for One Journey: representation, task-dependent models
- 16.13 The Caretaker’s Substitute: tacit knowledge, role transfer
- 19.03 The Orchestra after the Missing Note: constitutive practices, collective identity
- 19.06 The Village of One Remaining Expert: distributed competence, institutional memory

### Number, notation and calendars (6)

- 01.07 Street Names for the Dead: pigeonhole principle, finite namespaces
- 01.08 The Tram That Skips: modular arithmetic, Chinese remainder theorem
- 05.08 The Cogwheel Parish: least common multiples, wear patterns
- 05.11 The Abacus Factory: positional notation, base systems
- 09.13 The Cicada Road: prime periods
- 09.18 The Harbor of Many Clocks: calendar arithmetic, Metonic cycle

### Infinity, limits and continuity (6)

- 01.18 Hotel Infinity Street: Hilbert's hotel, infinite sets
- 02.10 The Estate of Unequal Halves: convergent series
- 10.04 The River That Moved the Border: continuity and definitions
- 20.03 The Hotel Inspector’s Infinite Upgrade: countable infinity, reindexing
- 21.03 The Staircase of Rational Steps: density of the rationals, order
- 21.11 The Door with No Last Lock: infinite sequences, limit completion
