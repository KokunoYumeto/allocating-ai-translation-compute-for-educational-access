"""Local-only dependency adapter for the recovered finite opening renderer."""
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE
MANIFEST = BASE / "source-excerpts/manifest-b40-opening.json"
TRANSLATION = BASE / "translations/b40-opening.json"
WITNESS = BASE / "source-excerpts/b40-opening.json"
NOTICES = BASE / "provenance/b40-opening-component-notices.json"
ASSETS = []

def require(test, message):
    if not test:
        raise ValueError(message)

def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load():
    expected = {
        MANIFEST: "a3430810fd1f3259587b5581980280ac78ff2520148c227d677798b5e3eb1239",
        TRANSLATION: "45352c7245ff69768f97dbb12ca0e8926fa25ded46bed2169c62779984daf173",
        WITNESS: "560a16023aa2e93d5f47236320ef5740090b2d786d9f506b6f68d05ac01315f5",
        NOTICES: "d66924e0634f6a4ac0cffb4f1a69feed666dcf450309739b1fd3a8d5ee7e11bf",
    }
    for path, digest in expected.items():
        require(file_hash(path) == digest, "Changed recovered source input: " + path.name)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = json.loads(TRANSLATION.read_text(encoding="utf-8"))
    for item in manifest["source_files"]["canonical"]:
        require(file_hash(BASE / "source/canonical" / item["repository_path"]) == item["sha256"], "Source body differs")
    return manifest, target, BASE / "source/canonical"
