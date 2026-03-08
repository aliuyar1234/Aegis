import importlib.util
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROTO_ROOT = ROOT / 'schema/proto'
PYTHON_VENDOR_ROOT = ROOT / 'py/vendor'
PYTHON_BINDINGS_ROOT = ROOT / 'py/packages/aegis_contracts_py/generated/proto'
MESSAGE_PATTERN = re.compile(r'(?m)^message\s+(\w+)\s*\{')
ENUM_PATTERN = re.compile(r'(?m)^enum\s+(\w+)\s*\{')
PACKAGE_PATTERN = re.compile(r'(?m)^package\s+([^;]+);')


def load_generated_python_module(module_path: Path):
    original_sys_path = list(sys.path)
    sys.path.insert(0, str(PYTHON_VENDOR_ROOT))
    sys.path.insert(1, str(PYTHON_BINDINGS_ROOT))
    try:
        spec = importlib.util.spec_from_file_location(f'aegis_generated_{module_path.stem}', module_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = original_sys_path


def test_every_event_has_schema_ref():
    data = yaml.safe_load((ROOT / 'schema/event-catalog/events.yaml').read_text())
    for event in data['events']:
        assert (ROOT / event['schema_ref']).exists()


def test_generated_python_contract_manifest_is_importable():
    manifest_path = ROOT / 'py/packages/aegis_contracts_py/generated/manifest.py'
    spec = importlib.util.spec_from_file_location('aegis_contract_manifest', manifest_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert 'ActionDispatch' in module.MESSAGE_NAMES
    assert 'cancelled' in {subject['name'] for subject in module.TRANSPORT_TOPOLOGY['subjects']}
    assert (PYTHON_BINDINGS_ROOT / '.source_digest').read_text().strip() == module.SOURCE_DIGEST


def test_generated_python_bindings_cover_proto_definitions():
    expected_modules = set()
    for proto_file in sorted(PROTO_ROOT.rglob('*.proto')):
        text = proto_file.read_text(encoding='utf-8')
        package_match = PACKAGE_PATTERN.search(text)
        assert package_match is not None
        package = package_match.group(1)

        relative = proto_file.relative_to(PROTO_ROOT)
        module_path = PYTHON_BINDINGS_ROOT / relative.with_name(f'{relative.stem}_pb2.py')
        expected_modules.add(module_path)
        assert module_path.exists()

        module = load_generated_python_module(module_path)
        for message_name in MESSAGE_PATTERN.findall(text):
            descriptor = getattr(getattr(module, message_name, None), 'DESCRIPTOR', None)
            assert descriptor is not None
            assert descriptor.full_name == f'{package}.{message_name}'
        for enum_name in ENUM_PATTERN.findall(text):
            descriptor = getattr(getattr(module, enum_name, None), 'DESCRIPTOR', None)
            assert descriptor is not None
            assert descriptor.full_name == f'{package}.{enum_name}'

    assert set(PYTHON_BINDINGS_ROOT.rglob('*_pb2.py')) == expected_modules
