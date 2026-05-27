import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads((ROOT / path).read_text())


def test_metadata_source_uses_preserved_mcca_id_for_sample_matching():
    spec = read_json("web/specs/spec.json")
    metadata = read_json("web/specs/metadata.json")

    identity = spec["vconcat"][1]["samples"]["identity"]
    backend = metadata["backend"]

    assert identity["idField"] == "MCCA-ID"
    assert identity["data"]["url"] == "../data/processed/samples.parquet"
    assert identity["data"]["format"]["type"] == "parquet"
    assert backend["sampleIdField"] == "MCCA-ID"
    assert backend["data"]["url"] == "../data/processed/samples.parquet"
    assert backend["data"]["format"]["type"] == "parquet"
    assert "parse" not in backend["data"]["format"]


def test_model_allele_metadata_source_uses_parquet_and_mcca_id():
    spec = read_json("web/specs/spec.json")
    model_alleles = read_json("web/specs/model-alleles.json")

    sources = spec["vconcat"][1]["metadata"]["sources"]
    source = next(source for source in sources if source["id"] == "model-alleles")
    backend = model_alleles["backend"]

    assert source["import"]["url"] == "model-alleles.json"
    assert backend["sampleIdField"] == "MCCA-ID"
    assert backend["data"]["url"] == "../data/processed/model-alleles.parquet"
    assert backend["data"]["format"]["type"] == "parquet"
    assert model_alleles["attributes"][""] == {
        "visible": False,
        "type": "nominal",
    }


def test_transcriptome_source_uses_symbol_primary_and_ensembl_lookup():
    transcriptome = read_json("web/specs/transcriptome.json")

    identifiers = transcriptome["backend"]["identifiers"]

    assert "Ensembl mouse gene IDs retained as lookup identifiers" in transcriptome["description"]
    assert identifiers == [
        {
            "name": "symbol",
            "path": "var/symbol",
            "primary": True,
            "caseInsensitive": True,
        },
        {
            "name": "ensembl",
            "path": "var/ensembl_id",
            "stripVersionSuffix": True,
        },
    ]


def test_mcca_derived_track_data_uses_parquet():
    copy_ratios = read_json("web/specs/copy-ratios.json")
    mutations = read_json("web/specs/mutations.json")

    assert copy_ratios["data"]["url"] == "../data/processed/copy-ratios.parquet"
    assert copy_ratios["data"]["format"] == {"type": "parquet"}
    assert mutations["data"]["url"] == "../data/processed/mutations.parquet"
    assert mutations["data"]["format"] == {"type": "parquet"}


def test_gene_annotation_track_uses_gencode_output():
    spec = read_json("web/specs/spec.json")
    genes = read_json("web/specs/gencode-genes.json")

    assert spec["vconcat"][2]["import"]["url"] == "gencode-genes.json"
    assert genes["data"]["url"] == "../data/external-data/gencodeGenes-mm10.tsv"
    assert "GENCODE mouse M25" in genes["description"]
    assert genes["layer"][1]["layer"][0]["mark"]["tooltip"] == {
        "handler": "refseqgene",
        "params": {
            "Organism": "Mus musculus",
        },
    }
