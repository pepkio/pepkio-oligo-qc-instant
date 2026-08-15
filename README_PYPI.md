# Pepkio Oligo QC Instant

High-throughput batch primer quality checker and forward/reverse PCR primer pair thermodynamic matching client for Python.

# What It Does

The `pepkio-oligo-qc-instant` package evaluates batch oligonucleotides (up to 100 primers) and forward/reverse PCR primer pairs. It computes multi-method melting temperatures, analyzes $\Delta T_m$ compatibility, calculates polymerase-specific recommended annealing temperatures ($T_a$), and flags 3′-end heterodimer and hairpin hazards across Q5, Phusion, Taq, and KAPA HiFi reaction buffers.

# Features

- **Polymerase-Specific $T_a$ Optimization**: Buffer models for Q5, Phusion, Standard Taq, KAPA HiFi, and Custom buffers.
- **Forward & Reverse Pair Matching**: Computes individual $T_m$, pair $\Delta T_m$, 3′-end cross-dimerization, and recommended annealing temperature ($T_a$).
- **High-Throughput Batch QC**: Validates up to 100 oligonucleotides simultaneously from FASTA, CSV/TSV, or text strings.
- **Multi-Method Tm Algorithms**: Wallace rule, SantaLucia 1998 unified nearest-neighbor, and Owczarzy 2008 salt-corrected thermodynamics.
- **Secondary Structure Scan**: Intramolecular hairpin and intermolecular dimer $\Delta G$ evaluation at 37°C.
- **IUPAC Degeneracy Handling**: Full support for standard ambiguous nucleotide bases with accurate GC and Tm weighting.
- **CLI & Python SDK**: Scriptable interface for automated bioinformatics pipelines and laboratory workflows.

# Installation

```bash
pip install pepkio-oligo-qc-instant
```

Or using `uv`:

```bash
uv add pepkio-oligo-qc-instant
```

# Quick Example

```python
from pepkio_oligo_qc_instant import PepkioClient

with PepkioClient() as client:
    # Evaluate a GAPDH primer pair for Q5 Polymerase
    qc = client.run({
        "mode": "pair",
        "name": "GAPDH",
        "fwd_seq": "GAAGGTGAAGGTCGGAGTC",
        "rev_seq": "GAAGATGGTGATGGGATTTC",
        "polymerase_id": "q5"
    })

    pair = qc.result["pair"]
    print("Status:", pair["overall_status"])
    print("Recommended Ta (°C):", pair["recommended_ta"])
    print("Delta Tm (°C):", pair["delta_tm"])
```

# Typical Use Cases

- **PCR & RT-qPCR Primer Pair Validation**: Screen candidate forward and reverse primer pairs for compatible $T_m$ and absent 3′-end cross-dimerization.
- **Multiplex Primer Screening**: Batch-verify dozens of primers for uniform annealing kinetics in targeted amplicon sequencing panels.
- **High-Fidelity Buffer Setup**: Accurately predict annealing temperatures in Q5 and Phusion master mixes.
- **Pre-Synthesis QC**: Validate multi-well plate oligonucleotide orders before placing commercial synthesis requests.

# Scientific Background

Thermodynamic melting temperatures are calculated using SantaLucia (1998) nearest-neighbor values combined with Owczarzy (2008) salt and divalent cation corrections. Recommended annealing temperatures are derived from the minimum primer $T_m$ adjusted for polymerase-specific processivity: $T_a = \min(T_m^{\text{fwd}}, T_m^{\text{rev}}) - 5^\circ\text{C}$ (clamped to master mix ranges). Heterodimers overlapping the last 5 nucleotides of the 3′-end with $\Delta G < -2.0\text{ kcal/mol}$ are flagged as primer-dimer risks.

# Web Application

For interactive primer pair design and graphical batch validation, a hosted web interface is available without installation.

Web Application: https://www.pepkio.com/tools/oligo-qc-instant

# Documentation and Resources

- GitHub Repository: https://github.com/pepkio/pepkio-oligo-qc-instant
- Web Application: https://www.pepkio.com/tools/oligo-qc-instant
- PyPI Package: https://pypi.org/project/pepkio-oligo-qc-instant/

# About Pepkio

Pepkio (https://www.pepkio.com/) develops software tools and bioinformatics solutions for life science researchers, including laboratory calculators and analysis services (https://www.pepkio.com/cro).

# Keywords

oligo QC instant, batch primer checker, PCR primer pair Tm, Q5 primer Tm calculator, Phusion annealing temperature, primer heterodimer, multiplex primer screening, FASTA primer validator, primer delta Tm, recommended annealing temperature Ta, 3-prime end overlap, primer dimer prevention, KAPA HiFi buffer, Taq primer check, reverse transcription primer pair, GAPDH primer QC, qPCR primer design, synthetic oligonucleotide QC, DNA primer quality control, nearest-neighbor Tm calculation, SantaLucia 1998 Tm, Owczarzy 2008 salt correction, primer hairpin analysis, degenerate primer IUPAC, 96-well plate primer QC, molecular biology tool
