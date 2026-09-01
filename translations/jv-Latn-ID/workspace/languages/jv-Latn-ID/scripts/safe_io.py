"""Replace generated artifacts only after a complete, flushed temporary write.

This protects the previous file if storage runs out during generation. It is
per-file atomicity, not an all-files transaction or a guarantee about power loss.
Temporary files are created in the target directory for same-volume replacement.
"""
import os
from pathlib import Path
import tempfile


def write_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix='.' + path.name + '.', suffix='.tmp', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        # This exact path was allocated above, never a caller-supplied glob.
        temporary.unlink(missing_ok=True)


def write_text(path, text):
    write_bytes(path, text.encode('utf-8'))
