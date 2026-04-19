"""Example: Run only Li adsorption energy."""
from mofscreen import MOFScreener

screener = MOFScreener(
    cif_path      = "my_mof.cif",
    cores         = 16,
    cp2k_data_dir = "/path/to/cp2k/data",
)

# Insert 1 Li ion (default)
result = screener.calc_adsorption(n_li=1)
print(f"E_ads (1 Li) : {result.e_ads_ev:.4f} eV")

# Insert 4 Li ions
# result = screener.calc_adsorption(n_li=4)
# print(f"E_ads (4 Li) : {result.e_ads_ev:.4f} eV")
