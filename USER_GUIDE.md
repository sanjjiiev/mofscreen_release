# mofscreen — User Setup Guide & How to Run

## What is mofscreen?

`mofscreen` is a Python library that automates DFT-based screening of
Metal-Organic Frameworks (MOFs) as Li-ion battery anode materials.
It wraps CP2K and computes 4 properties from a single CIF file:

  1. Electronic bandgap (single-point DFT)
  2. Li adsorption energy (GEO_OPT of MOF + Li)
  3. Formation energy (instant, from #1)
  4. Volume expansion (instant, from #2)

---

## Step 1 — Install CP2K (required dependency)

CP2K is the quantum chemistry engine. Install it once using conda:

```bash
# Create a dedicated DFT environment
conda create -n dft_env python=3.11 -y
conda activate dft_env

# Install CP2K and required packages
conda install -c conda-forge cp2k ase numpy -y
```

Verify CP2K is working:
```bash
cp2k --version
# Should print: CP2K version 2024.x ...
```

---

## Step 2 — Install mofscreen

```bash
conda activate dft_env
pip install mofscreen
```

---

## Step 3 — Find Your CP2K Data Directory

CP2K needs its data files (basis sets, potentials). You must tell
mofscreen where they are. Find your path like this:

```bash
conda activate dft_env

# Find the cp2k binary location, then navigate to data:
which cp2k
# e.g. /home/user/miniconda/envs/dft_env/bin/cp2k

# Data is usually at: <conda_env_prefix>/share/cp2k/data
ls ~/miniconda/envs/dft_env/share/cp2k/data/BASIS_MOLOPT
# If this file exists, your data dir is:
# /home/user/miniconda/envs/dft_env/share/cp2k/data
```

Common paths:
  - `~/miniconda/envs/dft_env/share/cp2k/data`
  - `~/anaconda3/envs/dft_env/share/cp2k/data`
  - `~/mambaforge/envs/dft_env/share/cp2k/data`

**Set it permanently in your environment (recommended):**
```bash
echo 'export CP2K_DATA_DIR=~/miniconda/envs/dft_env/share/cp2k/data' >> ~/.bashrc
source ~/.bashrc
```

---

## Step 4 — Prepare Your CIF File

`mofscreen` requires a **relaxed** MOF structure in CIF format.

Requirements for the CIF:
  - Must have periodic boundary conditions (unit cell defined)
  - Should be geometry-optimized (relaxed) before screening
  - File must be readable by ASE (`ase.io.read`)

If your CIF is unrelaxed, the library will warn you:
```
WARNING: Very short bond: 0.75 Å — CIF may be unrelaxed!
```

---

## How to Run — Python API

### Option A: Run Everything (Recommended)

```python
from mofscreen import MOFScreener

screener = MOFScreener(
    cif_path      = "my_mof.cif",
    cores         = 16,                    # adjust to your machine
    cp2k_data_dir = "/home/user/miniconda/envs/dft_env/share/cp2k/data",
)

results = screener.run_all()

# Access results
print(f"Bandgap       : {results.bandgap.bandgap_ev:.3f} eV")
print(f"Classification: {results.bandgap.classification}")
print(f"E_ads (Li)    : {results.adsorption.e_ads_ev:.4f} eV")
print(f"E_form/atom   : {results.formation.e_form_per_atom_ev:.4f} eV/atom")
print(f"Volume exp.   : {results.volume.expansion_pct:.2f} %")
```

Save this as `run_mof.py` and execute:
```bash
conda activate dft_env
python run_mof.py
```

---

### Option B: Run Only Bandgap

```python
from mofscreen import MOFScreener

screener = MOFScreener(
    cif_path      = "my_mof.cif",
    cores         = 16,
    cp2k_data_dir = "/path/to/cp2k/data",
)

result = screener.calc_bandgap()

print(f"Bandgap : {result.bandgap_ev:.3f} eV")
print(f"Type    : {result.classification}")
print(f"HOMO    : {result.homo_ev:.3f} eV")
print(f"LUMO    : {result.lumo_ev:.3f} eV")
print(f"Time    : {result.elapsed_min:.1f} min")
```

---

### Option C: Run Only Li Adsorption Energy

```python
from mofscreen import MOFScreener

screener = MOFScreener(
    cif_path      = "my_mof.cif",
    cores         = 16,
    cp2k_data_dir = "/path/to/cp2k/data",
)

# Insert 1 Li ion (default)
result = screener.calc_adsorption(n_li=1)

# Or insert 4 Li ions
result = screener.calc_adsorption(n_li=4)

print(f"E_ads : {result.e_ads_ev:.4f} eV")
print(f"Verdict: {'Good anode!' if result.e_ads_ev < -0.3 else 'Weak binding'}")
```

---

### Option D: Run Only Formation Energy

```python
from mofscreen import MOFScreener

screener = MOFScreener(
    cif_path      = "my_mof.cif",
    cores         = 16,
    cp2k_data_dir = "/path/to/cp2k/data",
)

result = screener.calc_formation()

print(f"E_form       : {result.e_form_ev:.4f} eV")
print(f"E_form/atom  : {result.e_form_per_atom_ev:.4f} eV/atom")
print(f"Refs complete: {result.refs_complete}")
```

---

### Option E: Run Only Volume Expansion

```python
from mofscreen import MOFScreener

screener = MOFScreener(
    cif_path      = "my_mof.cif",
    cores         = 16,
    cp2k_data_dir = "/path/to/cp2k/data",
)

result = screener.calc_volume()

print(f"V before : {result.v_before_A3:.2f} Å³")
print(f"V after  : {result.v_after_A3:.2f} Å³")
print(f"Expansion: {result.expansion_pct:.2f} %")
```

---

### Option F: High Accuracy + Self-Consistent References

For publication-quality results:

```python
from mofscreen import MOFScreener

screener = MOFScreener(
    cif_path      = "my_mof.cif",
    cores         = 32,
    mpi_ranks     = 4,                # multi-node MPI
    cp2k_data_dir = "/path/to/cp2k/data",
    high_accuracy = True,             # TZV2P basis set
)

# Compute elemental references first (important for formation energy accuracy)
refs = screener.compute_references()
print("References computed:", refs)

# Then run full pipeline
results = screener.run_all(
    n_li         = 2,
    cell_opt     = True,    # relax cell (needed for true volume expansion)
    compute_refs = True,
)
```

---

## How to Run — Command Line

If you prefer the terminal instead of writing Python scripts:

```bash
conda activate dft_env

# Set CP2K data dir once (or put in ~/.bashrc)
export CP2K_DATA_DIR=~/miniconda/envs/dft_env/share/cp2k/data

# Full pipeline — all 4 properties
mofscreen my_mof.cif --cores 16

# Or pass the data dir directly
mofscreen my_mof.cif --cores 16 --cp2k-data ~/miniconda/envs/dft_env/share/cp2k/data

# Bandgap only
mofscreen my_mof.cif --cores 16 --only bandgap

# Adsorption energy only (2 Li ions)
mofscreen my_mof.cif --cores 16 --only adsorption --n-li 2

# Formation energy only
mofscreen my_mof.cif --cores 16 --only formation

# Volume expansion only
mofscreen my_mof.cif --cores 16 --only volume

# High accuracy + compute references
mofscreen my_mof.cif --cores 16 --high-accuracy --compute-refs

# Fast screening (lower cutoffs, for testing)
mofscreen my_mof.cif --cores 8 --fast

# With MPI (4 MPI ranks × 8 threads = 32 cores total)
mofscreen my_mof.cif --cores 8 --mpi-ranks 4
```

---

## Batch Screening (Multiple MOFs)

To screen many CIF files automatically:

```python
from mofscreen import MOFScreener
import glob, json, os

cif_files = glob.glob("mof_dataset/*.cif")
all_results = {}

for cif in cif_files:
    name = os.path.basename(cif).replace(".cif", "")
    print(f"\n{'='*50}")
    print(f"  Screening: {name}")
    print(f"{'='*50}")
    try:
        screener = MOFScreener(
            cif_path      = cif,
            cores         = 16,
            cp2k_data_dir = "/path/to/cp2k/data",
            fast_mode     = True,    # faster for batch screening
        )
        results = screener.run_all()
        all_results[name] = {
            "bandgap_ev"        : results.bandgap.bandgap_ev,
            "classification"    : results.bandgap.classification,
            "e_ads_ev"          : results.adsorption.e_ads_ev,
            "e_form_per_atom_ev": results.formation.e_form_per_atom_ev,
            "expansion_pct"     : results.volume.expansion_pct,
        }
    except Exception as e:
        print(f"  ERROR for {name}: {e}")
        all_results[name] = {"error": str(e)}

# Save summary
with open("batch_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

print("\nBatch complete. Results in batch_results.json")
```

---

## Understanding the Output

### Live progress bar during calculation:
```
  ⚙ Bandgap              [████████████░░░░░░░░░░░░░░░░░░░░░░░] 127/300  SCF 127   | E=-45231.2847 eV    2m14s
```

### Result box when a calculation finishes:
```
┌──────────────────────────────────────────────────────────────┐
│  ✓  BANDGAP RESULT                                           │
├──────────────────────────────────────────────────────────────┤
│  Gap (PBE)        : 1.8421 eV                                │
│  Classification   : SEMICONDUCTOR                            │
│  HOMO             : -5.2341 eV                               │
│  LUMO             : -3.3920 eV                               │
│  SCF converged    : True                                     │
│  Elapsed          : 24.3 min                                 │
│                                                              │
│  NOTE: PBE underestimates real gap by ~30-50%.               │
└──────────────────────────────────────────────────────────────┘
```

### Final summary:
```
═════════════════════════════════════════════════════════════════
  FINAL SUMMARY
═════════════════════════════════════════════════════════════════
  MOF: C48H36Fe3N12O12  (111 atoms)
  ─────────────────────────────────────────────────────────────
  Bandgap        : 1.8421 eV  [SEMICONDUCTOR]
  E_ads (Li×1)   : -0.7843 eV
  E_form/atom    : -0.4312 eV/atom
  Volume exp.    : 2.143 %
  ─────────────────────────────────────────────────────────────
  Output dir     : /path/to/results/
═════════════════════════════════════════════════════════════════
```

---

## How to Interpret Results

### Bandgap
| Classification | Range | Meaning for Anode |
|---|---|---|
| METALLIC | < 0.01 eV | Good electronic conductivity |
| SEMI-METAL | 0.01–0.5 eV | Acceptable |
| SEMICONDUCTOR | 0.5–3.0 eV | Common for MOFs |
| INSULATOR | > 5.0 eV | Poor conductivity, needs doping |

### Li Adsorption Energy
| E_ads (eV) | Assessment |
|---|---|
| < -1.0 | STRONG — excellent Li storage |
| -1.0 to -0.3 | MODERATE — Li is stable |
| -0.3 to 0 | WEAK — Li barely binds |
| > 0 | UNFAVORABLE — Li won't stay |

### Formation Energy
| E_form/atom | Assessment |
|---|---|
| < -1.0 eV/atom | HIGHLY STABLE |
| < 0 eV/atom | STABLE |
| > 0 eV/atom | UNSTABLE |

### Volume Expansion
| Expansion | Assessment |
|---|---|
| < 1% | EXCELLENT — rigid framework |
| 1–5% | VERY GOOD |
| 5–10% | GOOD — acceptable for anode |
| 10–20% | MODERATE — may limit cycle life |
| > 20% | HIGH — poor cycle stability |

---

## Troubleshooting

**CP2K not found:**
```
ERROR: CP2K not found. Activate your dft_env conda environment.
```
→ Run `conda activate dft_env` before your script.

**CP2K data dir error:**
```
WARNING: CP2K_DATA_DIR not set!
```
→ Pass `cp2k_data_dir=` to MOFScreener, or `export CP2K_DATA_DIR=...`

**SCF did not converge:**
```
WARNING: SCF did NOT converge — bandgap unreliable!
```
→ Try increasing MAX_SCF, or check if your CIF is properly relaxed.

**No void sites found:**
```
RuntimeError: No void sites found. Ensure CIF is relaxed with open pores.
```
→ Your MOF may not have pores large enough for Li. The structure should
  be a porous MOF, not a dense solid.

**Very short bond warning:**
```
WARNING: Very short bond: 0.75 Å — CIF may be unrelaxed!
```
→ Your CIF needs geometry optimization before using mofscreen.

---

## Output Files Reference

```
results/
├── bandgap.inp              CP2K input for bandgap calculation
├── bandgap.out              CP2K output (contains eigenvalues, etc.)
├── bandgap.out.stderr        Error output from CP2K
├── mof_bandgap-RESTART.wfn  Wavefunction checkpoint (for restarts)
├── adsorption.inp           CP2K input for adsorption calc
├── adsorption.out           CP2K output for adsorption
├── mof_with_li.cif          MOF structure with Li ion(s) inserted
├── elemental_refs/          Elemental reference calculations
│   ├── ref_C.inp / ref_C.out
│   ├── ref_Li.inp / ref_Li.out
│   └── ref_energies.json    Cached reference energies
├── summary.json             All 4 results in machine-readable JSON
└── run.log                  Full timestamped log of the run
```

**Restart support:** If a calculation is interrupted (power cut, time limit),
simply re-run the same script. mofscreen automatically detects existing
checkpoint files and resumes from where it left off.

---

## System Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| CPU cores | 4 | 16–64 |
| RAM | 16 GB | 64+ GB |
| Disk | 5 GB | 50+ GB |
| OS | Linux | Linux |
| Python | 3.9 | 3.11 |
| CP2K | 2023.x | 2024.x |

**Note:** DFT calculations are computationally intensive. A typical MOF
with ~100 atoms takes 30–120 minutes per calculation on 16 cores.

---

*For issues or questions, open an issue on the GitHub repository.*
