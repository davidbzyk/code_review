"""Install agy 1.2.14 from Google's release bucket, checked against the digest GE pins."""

import hashlib
import io
import tarfile
import urllib.request

URL = (
    "https://storage.googleapis.com/antigravity-public/antigravity-cli/"
    "1.2.14-4571742832820224/linux-x64/cli_linux_x64.tar.gz"
)
SHA512 = (
    "fd771dfc74ddd07b61c8b0a6fd7a238f53a3a098a51052583a01d97ab84ee60d"
    "b741ce5f041e87a9da3c1a9aabe95b053113374437df1e231773552781edaf09"
)

data = urllib.request.urlopen(URL, timeout=300).read()
if hashlib.sha512(data).hexdigest() != SHA512:
    raise SystemExit("agy download does not match its pinned digest")
member = tarfile.open(fileobj=io.BytesIO(data)).extractfile("antigravity")
with open("/usr/local/bin/agy", "wb") as out:
    out.write(member.read())
