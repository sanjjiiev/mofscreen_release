"""Example: Run full MOF screening pipeline."""
from mofscreen import MOFScreener

screener = MOFScreener(
    cif_path      = "my_mof.cif",          # ← change this
    cores         = 16,                     # ← adjust to your machine
    cp2k_data_dir = "/home/YOUR_USERNAME/miniconda/envs/dft_env/share/cp2k/data",  # ← change this
)

results = screener.run_all()

print(f"\nBandgap       : {results.bandgap.bandgap_ev:.3f} eV  [{results.bandgap.classification}]")
print(f"E_ads (Li)    : {results.adsorption.e_ads_ev:.4f} eV")
print(f"E_form/atom   : {results.formation.e_form_per_atom_ev:.4f} eV/atom")
print(f"Volume exp.   : {results.volume.expansion_pct:.2f} %")
