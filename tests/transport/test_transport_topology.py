import hashlib
import importlib.util
import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
PYTHON_BINDINGS_ROOT = ROOT / 'py/packages/aegis_contracts_py/generated/proto'
RUST_BINDINGS_ROOT = ROOT / 'rs/crates/aegis_contracts_rs/src/generated/proto'


def load_generated_python_module(module_path: Path):
    original_sys_path = list(sys.path)
    sys.path.insert(0, str(PYTHON_BINDINGS_ROOT))
    try:
        spec = importlib.util.spec_from_file_location(f'aegis_generated_{module_path.stem}', module_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = original_sys_path


def test_transport_subject_messages_have_proto_messages():
    topology = yaml.safe_load((ROOT / 'schema/transport-topology.yaml').read_text())
    proto_text = "\n".join(p.read_text() for p in (ROOT / 'schema/proto').rglob('*.proto'))
    message_names = set(re.findall(r'(?m)^message\s+(\w+)\s*\{', proto_text))
    for subject in topology['subjects']:
        assert subject['message'] in message_names


def test_cancel_consumers_cover_dispatch_worker_kinds():
    topology = yaml.safe_load((ROOT / 'schema/transport-topology.yaml').read_text())
    dispatch = {c['filter_subject'].split('.')[-1] for c in topology['consumers'] if '.command.dispatch.' in c['filter_subject']}
    cancel = {c['filter_subject'].split('.')[-1] for c in topology['consumers'] if '.command.cancel.' in c['filter_subject']}
    assert dispatch == cancel


def test_cancelled_subject_is_part_of_worker_event_contracts():
    topology = yaml.safe_load((ROOT / 'schema/transport-topology.yaml').read_text())
    subjects = {subject['name']: subject['message'] for subject in topology['subjects']}
    assert subjects['cancelled'] == 'ActionCancelled'
    assert 'aegis.v1.event.cancelled.*' in next(stream['subjects'] for stream in topology['streams'] if stream['name'] == 'WORKER_EVENTS')


def test_transport_topology_lists_required_headers():
    topology = yaml.safe_load((ROOT / 'schema/transport-topology.yaml').read_text())
    headers = set(topology['headers'])
    assert headers == {
        'x-aegis-trace-id',
        'x-aegis-tenant-id',
        'x-aegis-workspace-id',
        'x-aegis-session-id',
        'x-aegis-lease-epoch',
        'x-aegis-contract-version',
        'x-aegis-isolation-tier',
    }


def test_runtime_control_plane_consumers_cover_worker_event_and_registry_subjects():
    topology = yaml.safe_load((ROOT / 'schema/transport-topology.yaml').read_text())
    consumers = {consumer['name']: consumer['filter_subject'] for consumer in topology['consumers']}
    assert consumers['runtime-worker-events'] == 'aegis.v1.event.>'
    assert consumers['runtime-worker-registry'] == 'aegis.v1.registry.>'


def test_generated_contract_manifests_share_current_source_digest():
    digest = hashlib.sha256()
    paths = [
        ROOT / 'buf.yaml',
        ROOT / 'buf.gen.yaml',
        ROOT / 'schema/transport-topology.yaml',
        *sorted((ROOT / 'schema/proto').rglob('*.proto')),
    ]

    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')

    expected = digest.hexdigest()

    assert f'@source_digest "{expected}"' in (ROOT / 'apps/aegis_execution_bridge/lib/aegis/execution_bridge/generated/contracts.ex').read_text()
    assert f"SOURCE_DIGEST = '{expected}'" in (ROOT / 'py/packages/aegis_contracts_py/generated/manifest.py').read_text()
    assert f'pub const SOURCE_DIGEST: &str = "{expected}";' in (ROOT / 'rs/crates/aegis_contracts_rs/src/generated/mod.rs').read_text()
    assert (PYTHON_BINDINGS_ROOT / '.source_digest').read_text().strip() == expected


def test_transport_subject_messages_exist_in_generated_python_bindings():
    topology = yaml.safe_load((ROOT / 'schema/transport-topology.yaml').read_text())
    worker_bindings = load_generated_python_module(PYTHON_BINDINGS_ROOT / 'aegis/runtime/v1/worker_pb2.py')
    for subject in topology['subjects']:
        descriptor = getattr(getattr(worker_bindings, subject['message'], None), 'DESCRIPTOR', None)
        assert descriptor is not None
        assert descriptor.full_name == f"aegis.runtime.v1.{subject['message']}"


def test_transport_subject_messages_exist_in_generated_rust_bindings():
    topology = yaml.safe_load((ROOT / 'schema/transport-topology.yaml').read_text())
    generated_sources = sorted(RUST_BINDINGS_ROOT.rglob('*.rs'))
    if not generated_sources:
        pytest.skip('Rust Buf bindings were not regenerated in this environment.')
    rust_text = "\n".join(path.read_text() for path in generated_sources)
    for message_name in {subject['message'] for subject in topology['subjects']}:
        assert f'pub struct {message_name}' in rust_text
