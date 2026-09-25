"""Sync the selected C stylesheet into the standalone landing page (Python stdlib)."""
from pathlib import Path
import re
root = Path(__file__).resolve().parent.parent
path = root / 'index.html'
text = path.read_text(encoding='utf-8')
css = (root / '样式源码/C_雪白深栏.css').read_text(encoding='utf-8')
text, count = re.subn(r'(<style id="theme-c">).*?(</style>)', lambda m:m.group(1)+css+m.group(2), text, count=1, flags=re.S)
if count != 1:
    raise ValueError('Cannot find the selected C style block; file not changed.')
path.write_text(text,encoding='utf-8')
print('C配色已同步到首页。')
