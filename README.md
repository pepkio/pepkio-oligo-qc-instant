# Pepkio Oligo QC Instant

High-throughput batch primer quality checker and forward/reverse PCR primer pair thermodynamic matching engine in Python and via web interface.

# Overview

High-throughput genomics, multiplex PCR panels, target enrichment workflows, and routine molecular cloning require rapid and rigorous quality control of large primer libraries. Designing primer pairs requires balancing forward and reverse melting temperatures ($\Delta T_m \le 2^\circ\text{C}$), preventing cross-primer heterodimer hybridization at 3′-ends, ensuring compatible GC content, and selecting annealing temperatures ($T_a$) optimized for specific DNA polymerases.

Manual inspection of dozens or hundreds of oligonucleotide sequences in spreadsheets is error-prone and lacks thermodynamic depth. Researchers need an instant, automated verification system that evaluates primer batches against exact buffer chemistry—such as NEB Q5, Thermo Phusion, Standard Taq, or KAPA HiFi—while identifying structural failure modes.

The **Pepkio Oligo QC Instant** delivers rapid, high-capacity oligonucleotide quality control. It evaluates single primers, high-throughput batches (up to 100 sequences), and forward/reverse primer pairs. It computes multi-method melting temperatures, analyzes 3′-end dimerization risks, determines optimal polymerase-specific annealing temperatures, and generates exportable QC summary tables.

The interactive hosted tool is available at the [Pepkio Oligo QC Instant](https://www.pepkio.com/tools/oligo-qc-instant) web application for immediate in-browser checking without installation. A lightweight Python package and CLI are provided in this repository for bioinformatic workflow automation.

Common search terms and alternative names for this tool include oligo QC instant, batch primer checker, PCR primer pair Tm matcher, Q5 primer Tm calculator, Phusion annealing temperature calculator, primer pair heterodimer checker, high-throughput oligo QC, multiplex primer screening tool, and FASTQ/FASTA primer batch validator.

# Features

- **Polymerase-Specific Annealing Temperature ($T_a$) Calculations**: Tailored buffer models for industry-standard DNA polymerases:
  - *Q5 High-Fidelity DNA Polymerase* (NEB)
  - *Phusion High-Fidelity DNA Polymerase* (Thermo Fisher)
  - *Standard Taq DNA Polymerase*
  - *KAPA HiFi HotStart DNA Polymerase* (Roche)
  - *Custom Buffer Formulation* (user-defined $\text{Na}^+$, $\text{Mg}^{2+}$, and dNTP concentrations).
- **Forward & Reverse Primer Pair Mode**:
  - Computes melting temperatures for both forward and reverse primers.
  - Calculates $\Delta T_m$ and flags mismatched pairs ($\Delta T_m > 2^\circ\text{C}$–$3^\circ\text{C}$).
  - Evaluates inter-primer heterodimer formation ($\Delta G$ at 37°C) and 3′-end cross-hybridization overlap.
  - Automatically calculates recommended reaction annealing temperature: $T_a = \min(T_m^{\text{fwd}}, T_m^{\text{rev}}) - 5^\circ\text{C}$ clamped to the enzyme's operating range.
- **High-Throughput Batch Processing**: Process up to 100 oligonucleotides in a single execution from FASTA strings, plain text lists, or CSV/TSV tables.
- **Multi-Method Thermodynamic Engine**: Computes Wallace rule (<14 bp), SantaLucia (1998) unified nearest-neighbor, and Owczarzy (2008) salt-corrected Tm values.
- **Secondary Structure Risk Screening**: Scans for intramolecular hairpins, self-dimers, and 3′-terminal stability hazards.
- **IUPAC Degeneracy Support**: Accepts IUPAC degenerate nucleotide codes (R, Y, S, W, K, M, B, D, H, V, N) with proper thermodynamic weighting.
- **Exportable Reports & Clean CLI**: Generate structured JSON responses or export tab-delimited QC reports.

# Common Use Cases

- **PCR & RT-qPCR Primer Pair Validation**: Screen candidate forward and reverse primer sets for GAPDH, ACTB, or target genes to confirm compatible $T_m$, minimal $\Delta T_m$, and absence of 3′-dimerization.
- **Multiplex PCR Library Verification**: Batch-check large panels of multiplex primers for uniform annealing kinetics across targeted amplicon sequencing workflows.
- **High-Fidelity Polymerase Protocol Setup**: Determine exact master mix annealing temperatures for Q5 and Phusion reactions without empirical gradient PCR trials.
- **Synthesis Order Pre-Screening**: Validate multi-well plate oligonucleotide orders from CSV spreadsheets before placing commercial synthesis requests.
- **Amplicon Sequencing Primer QC**: Evaluate Illumina/MGI locus-specific amplification primers with overhang adaptors.

# Why This Tool Exists

Commercial enzyme manufacturers host proprietary web calculators that are often isolated, limited to one enzyme brand, or incapable of programmatic batch execution. Conversely, generic web tools frequently fail to account for modern high-divalent buffer chemistries where $\text{Mg}^{2+}$ concentrations exceed 2.0 mM.

Furthermore, primer pair compatibility depends heavily on heterodimer stability at the 3′-hydroxyl terminus. Even when individual forward and reverse primers have identical 60°C melting temperatures, stable 3′-end cross-dimerization ($\Delta G < -3\text{ kcal/mol}$) will sequester primers and generate dominant primer-dimer amplicons.

The **Pepkio Oligo QC Instant** addresses these limitations by unifying polymerase-specific thermodynamic calculations, pair compatibility checks, and high-throughput batch screening into an open API and interactive web platform. Test primers online at the [oligo QC instant web app](https://www.pepkio.com/tools/oligo-qc-instant) or script batch verifications using the Python library.

# Installation

Install the Python client package from PyPI:

```bash
pip install pepkio-oligo-qc-instant
```

Or install using `uv`:

```bash
uv add pepkio-oligo-qc-instant
```

Package details are indexed on [PyPI](https://pypi.org/project/pepkio-oligo-qc-instant/).

# Quick Start

### Python API Usage

Set your API key as an environment variable:

```bash
export PEPKIO_API_KEY="your_pepkio_api_key"
```

Analyze primer pairs and batch oligonucleotides in Python:

```python
from pepkio_oligo_qc_instant import PepkioClient

with PepkioClient() as client:
    # 1. Evaluate a forward/reverse primer pair for Q5 Polymerase
    pair_qc = client.run({
        "mode": "pair",
        "name": "GAPDH_Exon2",
        "fwd_seq": "GAAGGTGAAGGTCGGAGTC",
        "rev_seq": "GAAGATGGTGATGGGATTTC",
        "polymerase_id": "q5"
    })

    result = pair_qc.result
    pair_data = result["pair"]
    print("Pair Name:", pair_data.get("name"))
    print("Overall Status:", pair_data.get("overall_status"))
    print("Recommended Annealing Ta (°C):", pair_data.get("recommended_ta"))
    print("Forward Tm (°C):", pair_data.get("fwd_tm"))
    print("Reverse Tm (°C):", pair_data.get("rev_tm"))
    print("Delta Tm (°C):", pair_data.get("delta_tm"))
    print("Heterodimer Delta G (kcal/mol):", pair_data.get("heterodimer_dg"))

    # 2. Batch check multiple oligonucleotides from plain text
    batch_qc = client.run({
        "mode": "batch",
        "polymerase_id": "phusion",
        "batch_text": "ATGCGTACGTACGTACGTACG\nGAAGGTGAAGGTCGGAGTCAAC\n"
    })

    print("\nBatch processed count:", len(batch_qc.result["batch"]))
```

### Command Line Interface (CLI)

The package provides a built-in CLI executable `pepkio-oligo-qc-instant`:

```bash
# View tool manifest and parameters
pepkio-oligo-qc-instant manifest

# Run the built-in GAPDH primer pair example
pepkio-oligo-qc-instant run --example pair_q5

# Run custom batch primer analysis
pepkio-oligo-qc-instant run --input-json '{
  "mode": "batch",
  "polymerase_id": "q5",
  "batch_text": "ATGCGTACGTACGTACGTACG\nGAAGGTGAAGGTCGGAGTCAAC\n"
}'
```

# Example Output

Representative JSON response for a forward/reverse primer pair evaluation:

```json
{
  "mode": "pair",
  "polymerase_id": "q5",
  "pair": {
    "name": "GAPDH_Exon2",
    "overall_status": "pass",
    "fwd_seq": "GAAGGTGAAGGTCGGAGTC",
    "rev_seq": "GAAGATGGTGATGGGATTTC",
    "fwd_length": 19,
    "rev_length": 20,
    "fwd_gc_pct": 57.89,
    "rev_gc_pct": 45.00,
    "fwd_tm": 61.2,
    "rev_tm": 60.5,
    "delta_tm": 0.7,
    "recommended_ta": 58.0,
    "heterodimer_dg": -1.2,
    "three_prime_overlap": false,
    "risk_level": "low"
  },
  "warnings": [],
  "all_failed": false
}
```

# Scientific Background

### Nearest-Neighbor Thermodynamics and Salt Adjustments

Melting temperature calculations for both individual primers and pairs utilize SantaLucia (1998) unified thermodynamic parameters:

$$\Delta G^\circ_{37} = \Delta H^\circ - T \Delta S^\circ$$

$$T_m = \frac{\Delta H^\circ}{\Delta S^\circ + R \ln(C_T / 4)} - 273.15$$

For high-fidelity enzyme buffers containing magnesium ions (e.g., Q5 and Phusion buffers at 2.0 mM $\text{Mg}^{2+}$), the Owczarzy (2008) salt correction adjusts the transition entropy ($\Delta S^\circ$) according to competitive cation-phosphate interactions.

### Optimal Annealing Temperature Calculation

In standard PCR protocols, the recommended annealing temperature is computed as:

$$T_a = \min\left(T_m^{\text{fwd}}, T_m^{\text{rev}}\right) - 5^\circ\text{C}$$

For specialized high-fidelity polymerases (Q5, Phusion, KAPA HiFi), $T_a$ is adjusted to operate at or near the lower primer Tm, preventing non-specific primer binding while maintaining high enzyme processivity.

### Cross-Dimer & 3′-End Overlap Scan

Heterodimerization between forward ($F$) and reverse ($R$) primers is evaluated by sliding $F$ against the reverse complement $\bar{R}$. Stems involving the terminal 5 nucleotides of either primer's 3′-end with free energy $\Delta G < -2.0\text{ kcal/mol}$ are flagged as high risk for primer-dimer amplification.

# Frequently Asked Questions

### What is the maximum acceptable $\Delta T_m$ between primer pairs?
For optimal PCR efficiency and specificity, the melting temperature difference ($\Delta T_m$) between forward and reverse primers should ideally be $\le 2^\circ\text{C}$, and should not exceed $5^\circ\text{C}$.

### How does the tool calculate recommended annealing temperature ($T_a$)?
For standard Taq polymerase, $T_a = \min(T_m^{\text{fwd}}, T_m^{\text{rev}}) - 5^\circ\text{C}$. For Q5 and Phusion enzymes, $T_a$ is optimized for the enzyme's buffer conditions and clamped within recommended master mix operating limits.

### What is the batch limit for oligonucleotides?
The tool supports up to 100 oligonucleotides per batch run, making it ideal for 96-well plate screening or multiplex panel verification.

### Which polymerase presets are supported?
Built-in presets include Q5 (NEB), Phusion (Thermo Fisher), Standard Taq, and KAPA HiFi (Roche), as well as fully customizable buffer formulations.

### How are degenerate bases handled?
IUPAC nucleotide ambiguity codes (R, Y, S, W, K, M, B, D, H, V, N) are accepted. GC content is calculated using standard 0.5 fractional contributions for dual ambiguities, and Tm is evaluated across resolved permutations.

### What causes a "fail" status on a primer pair?
A primer pair may fail due to extreme $\Delta T_m (>5^\circ\text{C})$, stable 3′-end heterodimer formation ($\Delta G < -4.0\text{ kcal/mol}$), severe hairpin formation, or non-IUPAC characters in the sequence.

### Can I paste sequences from a FASTA file?
Yes. Batch text input accepts standard multi-line FASTA headers (`>primer_1\nATGC...`) as well as raw newline-delimited sequence strings.

### What is the difference between Oligo QC Instant and Oligo QC Bench?
Oligo QC Instant is optimized for high-throughput batch checks (up to 100 primers) and forward/reverse primer pair compatibility matching with polymerase-specific $T_a$ recommendations. Oligo QC Bench provides in-depth biophysical profiling (extinction coefficients, molecular weight, optical density conversions, and DMSO gradient modeling).

### What is a primer heterodimer?
A heterodimer is an intermolecular duplex formed between the forward and reverse primers. When heterodimers form at the 3′-ends, DNA polymerase extends them into primer-dimer artifacts, severely depleting reaction reagents.

### Does the tool require an account to use online?
No. The web interface runs directly in your web browser without requiring account creation or software installation.

# Web Application

For interactive primer pair design and graphical batch validation, access the hosted web interface:

Web Application:
https://www.pepkio.com/tools/oligo-qc-instant

The web version provides an interactive interface, shareable links, protocol generation, printable worksheets, and visualization tools. It allows laboratory researchers to test primer pairs, visualize 3′-end alignments, and download formatted quality control worksheets.

# Related Resources

- GitHub Repository: https://github.com/pepkio/pepkio-oligo-qc-instant
- PyPI Package: https://pypi.org/project/pepkio-oligo-qc-instant/
- Web Application: https://www.pepkio.com/tools/oligo-qc-instant

# About Pepkio

Pepkio (https://www.pepkio.com/) develops software tools and bioinformatics solutions for life science researchers, including laboratory calculators and analysis services (https://www.pepkio.com/cro). Our platform provides molecular biology tools, NGS analysis pipelines, and experimental design utilities.

# Citation

If you use the Pepkio Oligo QC Instant tool in research, please cite:

```bibtex
@software{pepkio_oligo_qc_instant,
  author = {{Pepkio Open Science}},
  title = {Pepkio Oligo QC Instant: High-Throughput Batch Primer Quality Checker and Pair Annealing Temperature Engine},
  url = {https://www.pepkio.com/tools/oligo-qc-instant},
  year = {2026}
}
```

# License

Distributed under the MIT License. See `LICENSE` for details.

# Keywords

oligo QC instant, batch primer checker, PCR primer pair Tm matcher, Q5 primer Tm calculator, Phusion annealing temperature, primer heterodimer checker, high-throughput oligo QC, multiplex primer screening, FASTA primer validator, primer delta Tm calculator, recommended annealing temperature Ta, 3-prime end overlap checker, primer dimer prevention, KAPA HiFi buffer Tm, Taq polymerase primer check, reverse transcription primer pair QC, GAPDH primer QC, qPCR primer design verification, synthetic oligonucleotide QC, DNA primer quality control, amplicon sequencing primer check, nearest-neighbor Tm calculation, SantaLucia 1998 unified Tm, Owczarzy 2008 salt correction, primer hairpin analysis, degenerate primer IUPAC checker, 96-well plate primer QC, molecular biology laboratory tool, PCR troubleshooting assistant, primer synthesis validation, bioinformatic primer tool
