from importlib.resources import files

from pynwb import get_class, load_namespaces

# Wheels contain the remapped spec; editable installs use the checkout's root spec.
_package_path = files(__name__)
_spec_path = _package_path / "spec" / "ndx-tank-metadata.namespace.yaml"
if not _spec_path.exists():
    _spec_path = _package_path.parent.parent.parent / "spec" / "ndx-tank-metadata.namespace.yaml"
load_namespaces(str(_spec_path))

# Register the custom table only after its namespace has been loaded.
from .maze_extension import MazeExtension

LabMetaDataExtension = get_class("LabMetaDataExtension", "ndx-tank-metadata")
RigExtension = get_class("RigExtension", "ndx-tank-metadata")

del files, get_class, load_namespaces, _package_path, _spec_path
