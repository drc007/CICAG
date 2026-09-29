# hERG bioactivity from ChEMBL

A Jupyter notebook that downloads hERG (KCNH2) IC50 data from ChEMBL using the official
[`chembl_webresource_client`](https://github.com/chembl/chembl_webresource_client), cleans and
aggregates it, and explores how potency relates to calculated physicochemical properties.

No SQL, no REST plumbing and no local database: everything is pulled live from the
[EMBL-EBI ChEMBL API](https://www.ebi.ac.uk/chembl/api/data/docs).

## Contents

| File | What it is |
|---|---|
| `herg_chembl.ipynb` | The analysis notebook |
| `herg_chembl_course.ipynb` | Teaching variant, with extra cells on the client's Django-style query syntax and the available resources |
| `User Contributions/herg_chemblcourse2.ipynb` | Contributed variant of the course notebook |
| `environment.yml` | Conda environment |
| `herg_ic50_exact_*.csv` | Output of the current notebook settings: the raw records and the per-compound table |

## Setup

```bash
conda env create -f environment.yml
conda activate chembl-herg
python -m ipykernel install --user --name chembl --display-name "Python (chembl)"
jupyter lab herg_chembl.ipynb
```

The notebook's saved kernel is named `chembl`. If you install it under a different name, pick
your kernel from the Jupyter menu instead.

A pip-only setup works just as well:

```bash
python3 -m venv .venv && .venv/bin/pip install numpy pandas matplotlib rdkit requests jupyterlab ipykernel nbconvert chembl_webresource_client
```

## What the notebook does

1. **Resolves the target.** Looks up `Voltage-gated inwardly rectifying potassium channel KCNH2`
   by preferred name, which gives **CHEMBL240**.
2. **Queries activities.** Asks for IC50 values reported in nM with an exact relation
   (`standard_relation = '='`), so `>` and `<` bounds are excluded server-side. About 12,000
   records.
3. **Cleans.** Drops records that ChEMBL flags in `data_validity_comment` or that have no
   structure, then converts to pIC50 and takes the **median per compound** across assays.
4. **Calculates properties and filters.** Computes RDKit descriptors, then removes compounds
   with **cLogP < 0** or **MW > 600**. Roughly 9,300 compounds remain.
5. **Explores.** Potency distribution and publication years, a structure grid of the most potent
   blockers, potency against cLogP / MW / TPSA, the effect of a basic centre, a carboxylic acid
   comparison, and the approved drugs in the set.
6. **Saves** the raw records and the per-compound table as CSV.

### Settings you're likely to change

| Setting | Where | Default |
|---|---|---|
| `IC50_CUTOFF_NM` | Query cell | `None` (no potency cutoff; set e.g. `10000` for IC50 < 10 µM) |
| cLogP and MW filters | "Calculated properties and filters" | `cLogP >= 0`, `MW <= 600` |
| `Settings.Instance().MAX_LIMIT` | Setup cell | `1000` rows per request |

The client defaults to 20 rows per request, which makes a pull this size take many minutes. The
setup cell raises it to the API maximum of 1000 and extends the timeout, bringing a full run down
to a couple of minutes. Responses are cached locally for 24 hours in `.chembl_ws_client__*`, so
re-runs are fast.

### SMARTS patterns

- **Carboxylic acid**, neutral or ionised: `[CX3](=O)[O-,OX2H1]`
- **Aliphatic amine**: sp3 nitrogen not attached to C=O / C=N / C=S, sulfonyl, an aromatic ring,
  or a multiple bond.
- **Amidine / guanidine**:
  `[CX3;!a;!$(C=[O,S]);!$(C~N~[$(C=[O,S]),$(S(=O)=O),$(C#N),$([N+](=O)[O-]),$(N=O),$(O)])](=[NX2])-[NX3]`
  Matches basic amidines and guanidines, and rejects the non-basic ones where a nitrogen carries
  an acyl, sulfonyl, cyano, nitro, nitroso or N–O group (cyanoguanidines as in cimetidine,
  nitroguanidines, acylguanidines, amidoximes).

The `basic_amine` column is true for either kind of basic centre. The two parts are also kept
separately as `aliphatic_amine` and `amidine_guanidine`.

## Caveats when reading the results

- **pIC50 has a floor of 4.** ChEMBL flags every IC50 above 100 µM as *Outside typical range*,
  and the cleaning step drops flagged records.
- **The weak end is under-represented.** Compounds reported only as `>` values are excluded by the
  exact-relation filter, so a genuinely inactive compound may be missing entirely.
- **Mixed assay formats.** Binding, functional and toxicity assays are pooled. Filter on
  `assay_type` if that matters for your question.
- **Some values are wrong.** A few approved drugs have implausibly potent values that are probably
  unit or transcription errors in the source papers. Check outliers against the original
  publication before trusting them.
- **Correlations depend on the cutoff.** With no potency cutoff, cLogP correlates with pIC50 at
  ρ = 0.27 and TPSA at ρ = −0.23. Restricting to IC50 < 5 µM cuts both to near zero, purely
  through range restriction.

## Notes

- **The ChEMBL API goes down sometimes.** Cells can fail with an HTTP 500 from the server. It's
  usually transient; wait and re-run. Alternatively you can use the .csv files in the folder
- **Data version.** Results depend on the ChEMBL release that the API is serving, so counts will
  drift as new data is deposited.
