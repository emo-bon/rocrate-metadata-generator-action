import json
import os  
from pathlib import Path
from rocrate.rocrate import ROCrate
from rocrate.model.contextentity import ContextEntity

GITHUB_WORKSPACE = Path(os.getenv("GITHUB_WORKSPACE", "/github/workspace"))
ROCRATE_PROFILE_URI = os.getenv("PROFILE")
REPO = os.getenv("REPO").split("/")[-1]

crate = ROCrate()

# profile
profile = crate.add(
    ContextEntity(
        crate,
        ROCRATE_PROFILE_URI,
        properties={
            "@type": "CreativeWork",
            "name": "<name>", # TODO
            "version": "<version>" # TODO
        }
    )
)

# context
crate.metadata.extra_terms.update({"accessURL": "https://www.w3.org/ns/dcat#accessURL"}) # TODO http vs https

# graph
crate.root_dataset["conformsTo"] = profile

crate.update_jsonld({
    "@id": "./",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "title": REPO,
    "publisher": "https://www.embrc.eu/emo-bon", # TODO data.emobon.embrc.eu?
    "contactPoint": {
        "@type": "ContactPoint", # TODO changed this to type
        "email": "emobon@embrc.eu"
    },
    "description": f"This RO-Crate/GitHub repository contains the EMO BON sampling event logsheets from the observatory {REPO.split('-')[1].upper()}",
    "keywords": [
        "https://www.w3.org/TR/vocab-ssn/#SOSASampling",
        "https://rs.tdwg.org/terms/Event",
        "https://schema.org/Dataset",
        "EMO BON",
    ],
    "version": "<version>", # TODO
    "accessURL": f"https://raw.githubusercontent.com/emo-bon/{REPO}/main/ro-crate-metadata.json", # TODO point to github?
})

crate.update_jsonld({
    "@id": "ro-crate-metadata.json",
    "version": "<version>", # TODO
})

files = {
    "./.gitignore": {
        "encodingFormat": "text/plain", # TODO changed fileFormat to encodingFormat
    },
    "./README.md": {
        "encodingFormat": "text/markdown",
    },
    "./.github/workflows/workflow.yml": {
        "encodingFormat": "application/x-yaml",
    },
    "./config/workflow_properties.yml": {
        "encodingFormat": "application/x-yaml",
    },
    "./data-quality-control/dqc.csv": {
        "encodingFormat": "text/csv",
    },
    "./data-quality-control/logfile": {
        "encodingFormat": "text/plain",
    },
    "./data-quality-control/report.csv": {
        "encodingFormat": "text/csv",
    },
}

for dest_path, properties in files.items():
    properties.update({"@label": dest_path})
    crate.add_file(
        dest_path=dest_path,
        properties=properties
    )

directories = [
    "./.github/",
    "./config/",
    "./data-quality-control/",
]

for directory in directories:
    crate.add_directory(
        dest_path=directory,
        properties={
            "@label": directory,
        }
    )

for ls in ("logsheets", "logsheets-filtered", "logsheets-transformed"):
    dest_path = f"./{ls}/"
    crate.add_directory(
        dest_path=dest_path,
        properties={
            "@label": dest_path,
        }
    )
    for habitat in ("sediment", "water"):
        for sheet in ("measured", "observatory", "sampling"):
            dest_path = f"{ls}/{habitat}_{sheet}.csv"
            desc_pt1 = {
                "logsheets": "Raw",
                "logsheets-filtered": "Filtered",
                "logsheets-transformed": "Transformed",
            }
            desc_pt2 = {
                "measured": "environmental measurements",
                "observatory": "observatory metadata",
                "sampling": "sample and event metadata",
            }
            description = f"{desc_pt1[ls]} logsheet of the {desc_pt2[sheet]} from the {habitat} sampling events"
            envo_term = "ENVO_03000033" if habitat == "sediment" else "ENVO_06105011"
            keywords = {
                "measured": [
                    "metadata",
                    "http://ecoinformatics.org/oboe/oboe.1.0/oboe-core.owl#Measurement",
                    f"http://purl.obolibrary.org/obo/{envo_term}"
                ],
                "observatory": [
                    "metadata",
                    "https://purl.org/dc/terms/Location",
                    "https://schema.org/ContactPoint",
                    f"http://purl.obolibrary.org/obo/{envo_term}"
                ],
                "sampling": [
                    "metadata",
                    "https://rs.tdwg.org/terms/Event",
                    f"http://purl.obolibrary.org/obo/{envo_term}"
                ],
            }[sheet]
            crate.add_file(
                dest_path=dest_path,
                properties={
                    "@label": f"./{dest_path}",
                    "encodingFormat": "text/csv",
                    "downloadUrl": f"https://raw.githubusercontent.com/emo-bon/{REPO}/main/{dest_path}", # TODO point to github?
                    "description": description,
                    "keywords": keywords,
                }
            )

for dirpath, dirnames, filenames in os.walk(GITHUB_WORKSPACE / "rdf"):
    dirpath = dirpath.replace(str(GITHUB_WORKSPACE), ".")
    for d in dirnames:
        dest_path = f"{dirpath}/{d}/"
        crate.add_directory(
            dest_path=dest_path,
            properties={
                "@label": dest_path,
            }
        )
    for f in filenames:
        dest_path = f"{dirpath}/{f}"
        crate.add_file(
            dest_path=dest_path,
            properties={
                "@label": dest_path,
                "encodingFormat": "text/turtle",
            }
        )

# write
with open(GITHUB_WORKSPACE / "ro-crate-metadata.json", "w") as f:
    json.dump(crate.metadata.generate(), f, indent=4)
