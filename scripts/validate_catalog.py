"""Validate the signed list format consumed by Gravewright's module host."""
import base64,json,re
from pathlib import Path
from urllib.parse import urlsplit
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
root=Path(__file__).resolve().parents[1]
keys=json.loads((root/'trusted-keys.json').read_text())
records=json.loads((root/'gravewright.marketplace.json').read_text())
assert isinstance(records,list),'Catalog must be a JSON list'
seen=set()
for record in records:
 assert {'id','version','sdk','download','sha256','keyId','signature'} <= record.keys()
 pair=(record['id'],record['version']);assert pair not in seen;seen.add(pair)
 assert re.fullmatch('[0-9a-f]{64}',record['sha256'])
 url=urlsplit(record['download']);assert url.scheme=='https' and url.netloc and not url.username and not url.fragment
 public=Ed25519PublicKey.from_public_bytes(base64.b64decode(keys[record['keyId']],validate=True))
 canonical=json.dumps({k:v for k,v in record.items() if k!='signature'},sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
 public.verify(base64.b64decode(record['signature'],validate=True),canonical)
print(f'{len(records)} signed release records validated.')
