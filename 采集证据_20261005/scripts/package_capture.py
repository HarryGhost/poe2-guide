#!/usr/bin/env python3
"""Audit and package this capture once. Standard library; no network access."""
import hashlib
import json
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    output = ROOT.parent / 'outputs' / (ROOT.name + '.zip')
    if output.exists():
        raise FileExistsError('Refusing to overwrite existing ZIP: ' + str(output))
    mandatory = ['README.md', 'builds.json', 'atlas.json', '装备与珠宝核对.md', '缺失与冲突.md', 'validation.json']
    for name in mandatory:
        assert (ROOT / name).is_file(), name
    assert (ROOT / 'evidence').is_dir() and (ROOT / 'scripts').is_dir()
    sensitive_patterns = {
        'credential_header': r'(?im)(?:authorization|cookie|set-cookie)\s*["\x27]?\s*[:=]\s*["\x27]?(?:bearer\s+|eyJ|[A-Za-z0-9_]+=)',
        'token_value': r'(?i)["\x27](?:access_token|refresh_token|id_token|auth_token|sessionid|password|private_key)["\x27]\s*:\s*["\x27][^"\x27]+["\x27]',
        'email_in_url': r'(?i)[?&#]email=[^&"\s<>]+',
        'private_key_block': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    }
    findings = []
    json_count = 0
    local_link_count = 0
    image_count = 0
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:
            continue
        if p.suffix in ['.json', '.md', '.js', '.py']:
            content = p.read_text(encoding='utf-8')
            for pattern_name, pattern in sensitive_patterns.items():
                if re.search(pattern, content):
                    findings.append({'file': str(p.relative_to(ROOT)), 'pattern': pattern_name})
            if p.suffix == '.json':
                assert '[MaxDepth]' not in content, str(p)
                json.loads(content)
                json_count += 1
            if p.suffix == '.md':
                for href in re.findall(r'\]\(([^)]+)\)', content):
                    if '://' in href or href.startswith('#'):
                        continue
                    local = unquote(href).split('#', 1)[0]
                    assert (p.parent / local).is_file(), (p.name, local)
                    local_link_count += 1
        if p.suffix in ['.jpg', '.png']:
            data = p.read_bytes()
            assert data.startswith(b'\xff\xd8\xff') or data.startswith(b'\x89PNG\r\n\x1a\n'), str(p)
            image_count += 1
    assert not findings, findings
    validation = json.loads((ROOT / 'validation.json').read_text())
    assert all(c['passed'] for c in validation['checks'])
    preflight = {'checked_at': datetime.now(timezone.utc).isoformat(),
                 'mandatory_files_present': True, 'json_files_parsed': json_count,
                 'local_markdown_links_resolved': local_link_count,
                 'native_image_files_recognized': image_count,
                 'sensitive_value_patterns_found': findings,
                 'public_document_depth_truncation_found': False,
                 'zip_crc_status': 'performed_after_packaging_and_printed_by_this_script',
                 'limits': 'Pattern scan is not a general security proof. Only target page excerpts and screenshots were saved; no cookies/Authorization were requested or exported.'}
    write_json(ROOT / 'package-preflight.json', preflight)
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'manifest.json')
    entries = [{'path': str(p.relative_to(ROOT)), 'size': p.stat().st_size,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    manifest = {'generated_at': datetime.now(timezone.utc).isoformat(), 'hash': 'SHA-256',
                'scope': 'All delivery files except manifest.json itself; work/ scratch is outside capture root.', 'files': entries}
    write_json(ROOT / 'manifest.json', manifest)
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for p in files + [ROOT / 'manifest.json']:
            archive.write(p, ROOT.name + '/' + str(p.relative_to(ROOT)))
    with zipfile.ZipFile(output) as archive:
        corrupt = archive.testzip()
        assert corrupt is None, corrupt
        prefix = ROOT.name + '/'
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert all(name.startswith(prefix) and '..' not in Path(name).parts for name in names)
        packed_manifest = json.loads(archive.read(prefix + 'manifest.json'))
        assert packed_manifest == manifest
        for entry in packed_manifest['files']:
            data = archive.read(prefix + entry['path'])
            assert len(data) == entry['size']
            assert hashlib.sha256(data).hexdigest() == entry['sha256'], entry['path']
        assert len(names) == len(entries) + 1
    result = {'verified_at': datetime.now(timezone.utc).isoformat(), 'zip_path': str(output),
              'zip_size_bytes': output.stat().st_size, 'zip_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'zip_crc_test': 'passed', 'all_manifest_hashes': 'passed', 'file_count': len(entries) + 1,
              'preflight': preflight}
    scratch = ROOT.parent / 'work'
    scratch.mkdir(exist_ok=True)
    write_json(scratch / 'zip-verification.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
