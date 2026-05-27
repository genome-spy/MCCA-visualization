# MCCA GenomeSpy Visualization

This repository builds a local GenomeSpy visualization for the Mouse Cancer
Cell Line Atlas (MCCA). It contains the visualization specs, a small static web
launcher, and Python scripts that download and wrangle the public source data
into files that GenomeSpy can load efficiently.

The original data resource is described in:

> Mueller, S. et al. A disease model resource reveals core principles of
> tissue-specific cancer evolution. Nature 653, 265 (2026).
> https://doi.org/10.1038/s41586-026-10187-2

Generated data are not committed. The scripts create source files under
`tmp/raw/` and web-ready data under `web/data/`; both directories are ignored by
git.

## Visualization

The main view combines sample metadata with genomic tracks for canonical mouse
chromosomes (`chr1`-`chr19`, `chrX`, and `chrY`):

- MCCA cell line annotations
- engineered model alleles parsed from `MouseModelDetailed`
- segmented copy-ratio data from the source `LOG2FC` field
- somatic mutation calls sized by tumor allele fraction
- UCSC mm10 cytobands
- GENCODE M25 mm10 gene annotations with citation-count label scoring
- lazy transcriptome metadata from a Zarr expression matrix

The spec files live under `web/specs/`. The root spec is
`web/specs/spec.json`, and the static entry point is `web/index.html`.

## Data Wrangling

The scripts are written in Python and managed with `uv`.

`mcca-download` downloads:

- MCCA mutation, copy-number, and cell line annotation workbooks
- MCCA transcriptome archive
- GENCODE mouse M25 annotation
- NCBI gene mapping tables used for gene label scoring
- UCSC mm10 cytobands

`mcca-wrangle` converts the MCCA-derived tabular data into GenomeSpy-ready
files:

- `web/data/processed/samples.parquet`
- `web/data/processed/model-alleles.parquet`
- `web/data/processed/copy-ratios.parquet`
- `web/data/processed/mutations.parquet`
- `web/data/expression.zarr`

The tabular outputs use Parquet. TSV would also work for many GenomeSpy data
sources, but Parquet is faster to load and preserves column types and missing
values explicitly, avoiding separate parse hints in the visualization specs.

The transcriptome source contains VST batch-corrected expression values with
Ensembl mouse gene IDs as rows and MCCA samples as columns. The wrangler maps
the Ensembl IDs to GENCODE M25 mouse gene symbols, keeps the original
`ENSMUSG...` identifiers as secondary lookup keys, z-scores each gene across
samples, and writes a Zarr v3 matrix for lazy metadata loading.

`mcca-gencode-genes` builds the gene annotation track from GENCODE mouse M25.
It adapts the citation-count label scoring idea from the HiGlass gene
annotation preparation guide:
<https://docs.higlass.io/data_preparation.html#gene-annotation-tracks>.
The generated file is `web/data/external-data/gencodeGenes-mm10.tsv`, with a
matching provenance sidecar.

## Quick Start

Install dependencies:

```bash
uv sync
```

Download source data:

```bash
uv run mcca-download
```

Wrangle the MCCA-derived data:

```bash
uv run mcca-wrangle
```

Generate the GENCODE gene annotation track:

```bash
uv run mcca-gencode-genes
```

Serve the static visualization:

```bash
uv run python -m http.server 8008 --directory web
```

Open <http://localhost:8008>.

## Repository Layout

- `src/mcca_genomespy/download.py`: download source workbooks and external
  annotation inputs.
- `src/mcca_genomespy/wrangle.py`: normalize MCCA workbooks, filter genomic
  data to canonical mm10 chromosomes, and write Parquet/Zarr outputs.
- `src/mcca_genomespy/expression.py`: build the lazy transcriptome Zarr source.
- `src/mcca_genomespy/gene_annotations.py`: build the scored GENCODE gene
  annotation track.
- `web/specs/`: GenomeSpy visualization and metadata source specs.
- `web/index.html`: static GenomeSpy App launcher.
- `web/data/`: generated data used by the visualization.

To deploy the demo on a static web server, run the wrangling commands above and
publish the contents of `web/`.

## License

The contents of this repository are released under CC0 1.0 Universal.

## Acknowledgement

OpenAI Codex with GPT-5.5 was used to help prepare the data-wrangling scripts.
