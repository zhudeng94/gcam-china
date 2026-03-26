# China Carbon Peak Uncertainty Scenario Framework

## Overview

This scenario framework addresses the uncertainty around China's carbon emission
peak timing. Due to energy transition, economic shifts, and evolving policy
dynamics, there is significant uncertainty about when China's CO2 emissions will
peak relative to its 2030 NDC commitment. This framework provides three
scenarios spanning the range of plausible peak timing outcomes.

## Scenario Design

All scenarios share the following assumptions:
- **Socioeconomic pathway**: SSP2 (middle-of-the-road)
- **Net-zero target**: China achieves carbon neutrality by 2060
- **Rest of world**: Global net-zero by 2060 (consistent with existing GCAM-China assumptions)
- **Emission units**: MtC (megatons of carbon; multiply by 3.67 to convert to MtCO2)

### Scenario 1: Early Peak (2025) — `carbon_peak_early_2025_CN.xml`

| Year | CO2 Cap (MtC) |
|------|---------------|
| 2025 | 3350 (peak)   |
| 2030 | 3100          |
| 2035 | 2583          |
| 2040 | 2066          |
| 2045 | 1550          |
| 2050 | 1033          |
| 2055 | 516           |
| 2060 | -2 (net-zero) |

**Key assumptions driving early peak:**
- Economic growth slowdown and structural transformation away from heavy industry
- Rapid renewable energy deployment (solar + wind capacity exceeding targets)
- Population peaking and beginning to decline
- Strong policy implementation of dual carbon goals
- Successful grid integration of variable renewable energy

### Scenario 2: Reference Peak (2030) — `carbon_cap_net_zero_2060_CN.xml`

| Year | CO2 Cap (MtC) |
|------|---------------|
| 2025 | 3400          |
| 2030 | 3550 (peak)   |
| 2035 | 2958          |
| 2040 | 2366          |
| 2045 | 1774          |
| 2050 | 1182          |
| 2055 | 590           |
| 2060 | -2 (net-zero) |

**Key assumptions (baseline NDC commitment):**
- Moderate economic growth aligned with SSP2 projections
- Gradual energy transition at current policy trajectory
- Carbon peak aligned with China's NDC 2030 commitment
- Linear decline from peak to net-zero by 2060

### Scenario 3: Delayed Peak (2035) — `carbon_peak_delayed_2035_CN.xml`

| Year | CO2 Cap (MtC) |
|------|---------------|
| 2025 | 3400          |
| 2030 | 3600          |
| 2035 | 3650 (peak)   |
| 2040 | 2920          |
| 2045 | 2190          |
| 2050 | 1460          |
| 2055 | 730           |
| 2060 | -2 (net-zero) |

**Key assumptions driving delayed peak:**
- Economic stimulus policies sustain industrial growth beyond expectations
- AI and data center energy demand creates additional electricity consumption
- Chemical industry demand growth from manufacturing expansion
- Grid integration challenges delay effective utilization of renewable capacity
- Higher-than-expected urbanization energy demand

## How to Run

### Individual Scenarios

Each scenario has a standalone configuration file in the `exe/` directory:

```bash
# Early Peak (2025)
./gcam.exe -C configuration_china_peak_early.xml

# Reference Peak (2030)
./gcam.exe -C configuration_china_peak_reference.xml

# Delayed Peak (2035)
./gcam.exe -C configuration_china_peak_delayed.xml
```

### Batch Run (All Scenarios)

To run all three scenarios in batch mode, use `configuration_china.xml` with
the batch file set to `batch_china_carbon_peak.xml`:

1. Edit `configuration_china.xml` and set:
   - `BatchFileName` to `batch_china_carbon_peak.xml`
   - `BatchMode` to `1`
2. Run: `./gcam.exe -C configuration_china.xml`

## File Structure

```
input/policy/
├── carbon_peak_early_2025_CN.xml          # Early peak scenario (2025)
├── carbon_cap_net_zero_2060_CN.xml        # Reference peak scenario (2030, existing)
├── carbon_peak_delayed_2035_CN.xml        # Delayed peak scenario (2035)
└── README_carbon_peak_scenarios.md        # This documentation

exe/
├── configuration_china_peak_early.xml     # Config for early peak
├── configuration_china_peak_reference.xml # Config for reference peak
├── configuration_china_peak_delayed.xml   # Config for delayed peak
└── batch_china_carbon_peak.xml            # Batch runner for all scenarios
```

## Potential Academic Contributions

This scenario framework enables several innovative research directions:

1. **Carbon Peak Timing Uncertainty Analysis**: Systematic exploration of when
   China's emissions will peak, quantifying the range of possible outcomes and
   their drivers across energy, economic, and policy dimensions.

2. **Sectoral Decomposition of Peak Drivers**: Analysis of how different sectors
   (power, industry, transport, buildings) contribute to peak timing differences,
   with particular focus on emerging factors like AI energy demand and chemical
   industry growth.

3. **Province-Level Carbon Peak Heterogeneity**: Leveraging GCAM-China's
   provincial resolution to analyze how different provinces may peak at different
   times, and how provincial policies interact with national targets.

4. **Implications for Carbon Neutrality Pathway**: Quantifying how different peak
   timing affects the steepness and feasibility of the post-peak decline required
   to achieve 2060 carbon neutrality — a delayed peak requires more aggressive
   post-peak reductions.

5. **Carbon Budget Implications**: Computing the cumulative carbon budget
   consumed under each peak timing scenario, with implications for global
   temperature targets.

6. **Technology Transition Requirements**: Analyzing how peak timing affects
   the required pace of technology deployment (renewables, CCS, hydrogen, DAC)
   in each scenario.

## References

- China's NDC: Peak CO2 emissions before 2030, achieve carbon neutrality by 2060
- GCAM Documentation: http://jgcri.github.io/gcam-doc/
- GCAM-China: https://umd-cgs.github.io/metarepo_gcam-china/
