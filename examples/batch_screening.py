"""Example: Batch screen multiple CIF files."""
from mofscreen import MOFScreener
import glob, json, os

cif_files = glob.glob("dataset/*.cif")   # ← point to your folder
all_results = {}

for cif in sorted(cif_files):
    name = os.path.basename(cif).replace(".cif", "")
    print(f"\nScreening: {name}")
    try:
        screener = MOFScreener(
            cif_path      = cif,
            cores         = 16,
            cp2k_data_dir = "/path/to/cp2k/data",
            fast_mode     = True,    # faster for batch
        )
        r = screener.run_all()
        all_results[name] = {
            "bandgap_ev"        : r.bandgap.bandgap_ev,
            "classification"    : r.bandgap.classification,
            "e_ads_ev"          : r.adsorption.e_ads_ev,
            "e_form_per_atom_ev": r.formation.e_form_per_atom_ev,
            "expansion_pct"     : r.volume.expansion_pct,
        }
    except Exception as e:
        all_results[name] = {"error": str(e)}
        print(f"  ERROR: {e}")

with open("batch_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print("\nDone! Results saved to batch_results.json")
