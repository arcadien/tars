"""Print an HTML file to PDF with headless Firefox (WebDriver BiDi, standard library only).

usage: python3 -I tools/html2pdf.py page.html page.pdf [--portrait]

Starts a throw-away headless Firefox with its remote protocol on a free port, opens the page, prints it (A4,
landscape unless --portrait, backgrounds on, the page's @media print rules apply) and writes the PDF.
"""
import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time


class WS:
    """minimal client side WebSocket (text frames, masked, no extensions)"""

    def __init__(self, host, port, path):
        self.s = socket.create_connection((host, port), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f'GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                        f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        head = b''
        while b'\r\n\r\n' not in head:
            head += self.s.recv(1)
        if b' 101 ' not in head.split(b'\r\n')[0]:
            raise RuntimeError(head.decode(errors='replace'))
        self.n = 0

    def send(self, obj):
        data = json.dumps(obj).encode()
        hdr = bytes([0x81])
        ln = len(data)
        hdr += bytes([0x80 | ln]) if ln < 126 else bytes([0x80 | 126]) + struct.pack('>H', ln) if ln < 65536 else bytes([0x80 | 127]) + struct.pack('>Q', ln)
        mask = os.urandom(4)
        self.s.sendall(hdr + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def _exact(self, n):
        buf = b''
        while len(buf) < n:
            chunk = self.s.recv(n - len(buf))
            if not chunk:
                raise RuntimeError('connection closed')
            buf += chunk
        return buf

    def recv(self):
        msg = b''
        while True:
            b0, b1 = self._exact(2)
            ln = b1 & 0x7f
            if ln == 126:
                ln = struct.unpack('>H', self._exact(2))[0]
            elif ln == 127:
                ln = struct.unpack('>Q', self._exact(8))[0]
            payload = self._exact(ln)
            if b0 & 0x0f in (1, 0):
                msg += payload
                if b0 & 0x80:
                    return json.loads(msg)

    def call(self, method, params):
        self.n += 1
        self.send({'id': self.n, 'method': method, 'params': params})
        while True:
            r = self.recv()
            if r.get('id') == self.n:
                if r.get('type') == 'error':
                    raise RuntimeError(f'{method}: {r.get("error")}: {r.get("message")}')
                return r['result']


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    src, dst = os.path.abspath(args[0]), os.path.abspath(args[1])
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
    prof = tempfile.mkdtemp(prefix='html2pdf-')
    ff = subprocess.Popen(['firefox', '--headless', '--no-remote', '--profile', prof, f'--remote-debugging-port={port}'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(450):   # 90 s: the snap Firefox of CI runners starts slowly when cold
            try:
                ws = WS('127.0.0.1', port, '/session')
                break
            except (OSError, RuntimeError):
                time.sleep(0.2)
        else:
            raise RuntimeError('Firefox remote protocol did not start')
        ws.call('session.new', {'capabilities': {}})
        ctx = ws.call('browsingContext.getTree', {})['contexts'][0]['context']
        ws.call('browsingContext.navigate', {'context': ctx, 'url': 'file://' + src, 'wait': 'complete'})
        time.sleep(1.5)   # web fonts
        pdf = ws.call('browsingContext.print', {
            'context': ctx, 'background': True, 'shrinkToFit': True,
            'orientation': 'portrait' if '--portrait' in sys.argv else 'landscape',
            'page': {'width': 21.0, 'height': 29.7}, 'margin': {'top': 0.8, 'bottom': 0.8, 'left': 0.8, 'right': 0.8}})['data']
        with open(dst, 'wb') as fh:
            fh.write(base64.b64decode(pdf))
        try:
            ws.call('session.end', {})
        except Exception:
            pass
    finally:
        ff.terminate()
        try:
            ff.wait(10)
        except subprocess.TimeoutExpired:
            ff.kill()
        shutil.rmtree(prof, ignore_errors=True)
    print('wrote', os.path.relpath(dst))


if __name__ == '__main__':
    main()
