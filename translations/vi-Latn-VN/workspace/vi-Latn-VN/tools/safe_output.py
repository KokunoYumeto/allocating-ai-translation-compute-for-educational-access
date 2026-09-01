"""Replace an owned generated output only after its complete new bytes are saved."""
import os
from pathlib import Path
import shutil
import tempfile


def write_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(path.parent).free < 2 * len(data) + 1024 * 1024:
        raise OSError("Insufficient free space; existing output was not touched")
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".partial", delete=False) as stream:
        partial = Path(stream.name)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    partial.replace(path)
