import concurrent.futures
import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r'C:\Users\PK800\Documents\ChatGPT\AD5M Build\reference\Voron_Trident')
ROOT.mkdir(parents=True, exist_ok=True)
ARCHIVES = ROOT / 'source_archives'
ARCHIVES.mkdir(exist_ok=True)
HEADERS = {'User-Agent': 'AD5M-Voron-reference-archive'}

def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as r:
        return json.load(r)

def snapshot(name):
    repo = 'VoronDesign/' + name
    meta = get_json('https://api.github.com/repos/' + repo)
    commit = get_json('https://api.github.com/repos/' + repo + '/commits/' + meta['default_branch'])
    sha = commit['sha']
    url = 'https://codeload.github.com/' + repo + '/zip/' + sha
    target = ARCHIVES / (name + '-' + sha[:12] + '.zip')
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as r, target.open('wb') as f:
        shutil.copyfileobj(r, f)
    digest = hashlib.file_digest(target.open('rb'), 'sha256').hexdigest()
    folder = ROOT / name
    folder.mkdir(exist_ok=True)
    count = 0
    total = 0
    with zipfile.ZipFile(target) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError('ZIP CRC failure: ' + bad)
        for entry in z.infolist():
            parts = Path(entry.filename).parts[1:]
            if not parts or entry.is_dir():
                continue
            dest = folder.joinpath(*parts).resolve()
            if not dest.is_relative_to(folder.resolve()):
                raise RuntimeError('Unsafe archive path')
            dest.parent.mkdir(parents=True, exist_ok=True)
            with z.open(entry) as src, dest.open('wb') as out:
                shutil.copyfileobj(src, out)
            count += 1
            total += dest.stat().st_size
    result = {'repository': repo, 'source_url': meta['html_url'], 'branch': meta['default_branch'], 'commit': sha,
              'commit_date': commit['commit']['committer']['date'], 'download_url': url,
              'archive': str(target.relative_to(ROOT)), 'archive_sha256': digest,
              'archive_bytes': target.stat().st_size, 'extracted_files': count, 'extracted_bytes': total,
              'zip_crc_verified': True}
    (ROOT / (name + '_source.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)
    return result

if __name__ == '__main__':
    repos = ['Voron-Trident', 'Voron-Stealthburner', 'Voron-Documentation']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(snapshot, repos))
    (ROOT / 'SOURCES.json').write_text(json.dumps({'retrieved_utc': datetime.now(timezone.utc).isoformat(),
        'project_date': '2026-11-03', 'repositories': results}, indent=2), encoding='utf-8')
