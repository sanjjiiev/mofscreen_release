"""Example: Run only bandgap calculation."""
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
