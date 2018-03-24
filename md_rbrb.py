#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function


"""md_rbrb.py: multilanguage Rabi-Ribi"""
__version__   = "2017.02.19"
__author__    = "ed <a@ocv.me>"
__credits__   = ["stackoverflow.com"]
__license__   = "MIT"
__copyright__ = 2017


# Rabi-Ribi v1.75
ADR_BLOCK_ID = 0xd7d64
ADR_BLOCK_POS = 0xd7d50


from ctypes.wintypes import \
    WORD, DWORD, HMODULE, HANDLE, MAX_PATH
from ctypes import \
    POINTER, byref, cast, addressof, string_at, \
    create_unicode_buffer, sizeof, windll, \
    c_ubyte, c_ulong, c_void_p
import subprocess
import threading
import socket
import struct
import codecs
import base64
import json
import zlib
import time
import sys
import re
try:
    from builtins import chr
except:
    from __builtin__ import chr

##
## codepage stuff
##

# chcp 65001

enc_py26 = 'eJxdkttyhCAMht/F615wBp+l02GUusrqHkZ0ZtunLwvJmu0N//eHhIDxs+lSiLH5aPo4apBpTiFlDncmbVElVFXwmrGiFry1uqjTDFSAYtyA1nxnIM9wUMg3ElSBQr2BetNWtbAPfVtZ61tV91u4B2fMAAgArmBL6BdwBIEgERSCRjAIFsFlGPbgz3eEmLxgTB32wQSXYOc1w9gLyUWBuazcMfm80PSbl5hugglRTzyM5+9W/LO1JYnIdzs8NhIo91i6LV7xXOd0i4cWloQVYU3YELaEHeGWMGfU0A6ctuC0B382Od+mrs8636LzK8Ke4dIFH37WuCwxgB3XYZiBYxiW7voNrrxYgFlvl+4KvO3rHNOU3X3Lcy2jT1M8bc8BUsYP/QrgdPft5MufWMH3w8ELcnlLhSMh8yvBgjpUn+LYfP0Bd0QChw=='

enc_py27 = 'eJxdkt1ygyAQRt/F617wDz5Lp+MoNUo0MSM6k/bpi7AbN73xnA9wF8TPqo0+hOqj6sKgAeMUfUzuH0zaTCVUIWTNWKYVQBi3Vmc6zYACiOMGaIGu0MB6w4HwnpFABYQ6BuqYutDCPPSvZXm/VmW+hv1wxgyIAOEKpoR+CUcRKBJFoWgUg2JRjjP1u2+uD5QQG8GYOuOTCS4hTmuSoROSiyxTfnLH5LGh8Tc9QlwEE6JUPEPD36P4F0tLMiLfY//cyEDex9xu4Y51ndM1Fs0uiSvimrghbok74jVxzmignTltx2k/Thvyo+N1GdsucVqCa1aUPcmt9Y3/WcM8Bw9xWPt+Ag++n9v7N6R8fAFhXW7tHXzb1ynEMaXHli45/wdxDJftuE3q+NVfA3jV+3Zp8m9ZpOn602f0fJYi54LkrwUW6JBNDEP19Qcj/gml'

def zenc(lst):
    return base64.b64encode(zlib.compress(json.dumps(lst, separators=(',',':'))))

def zdec(b64):
    return json.loads(zlib.decompress(base64.b64decode(b64)).decode())

if sys.version_info.major == 2 and sys.version_info.minor == 6:
    tcodecs = zdec(enc_py26)
else:
    tcodecs = zdec(enc_py27)

# kinda fixes py2.7
def cp65001(name):
    if name.lower() == 'cp65001':
        return codecs.lookup('utf-8')
codecs.register(cp65001)

##
## process interaction declarations
##

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle
PROCESS_ALL_ACCESS = 0x1f0fff
PROCESS_QUERY_INFORMATION = 0x400
PROCESS_VM_READ = 0x10
LIST_MODULES_ALL = 0x3

##
## list processes and modules within
##

#def findproc(name):
#    cmd = 'wmic process get description,processid'
#    for line in run(cmd.split(' ')):
#        line = line.strip()
#        if line[-3:].lower() == 'exe':
#            ofs = line.find(' ')
#            pid = line[:ofs].strip()
#            line = line[ofs:].strip()
#        else:
#            ofs = line.rfind(' ')
#            pid = line[ofs+1:].strip()
#            line = line[:ofs].strip()
#        if line == name:
#            return pid
#    return None

def EnumProcesses():
    buf_count = 256
    while True:
        buf = (DWORD * buf_count)()
        buf_size = sizeof(buf)
        res_size = DWORD()
        if not windll.Psapi.EnumProcesses(byref(buf), buf_size, byref(res_size)):
            raise OSError('EnumProcesses failed')
        if res_size.value >= buf_size:
            buf_count *= 2
            continue
        count = res_size.value // (buf_size // buf_count)
        return buf[:count]

def EnumProcessModulesEx(hProcess):
    buf_count = 256
    while True:
        buf = (HMODULE * buf_count)()
        buf_size = sizeof(buf)
        needed = DWORD()
        if not windll.Psapi.EnumProcessModulesEx(
                hProcess, byref(buf), buf_size,
                byref(needed), LIST_MODULES_ALL):
            raise OSError('EnumProcessModulesEx failed')
        if buf_size < needed.value:
            buf_count = needed.value // (buf_size // buf_count)
            continue
        count = needed.value // (buf_size // buf_count)
        return map(HMODULE, buf[:count])

def GetModuleFileNameEx(hProcess, hModule):
    buf = create_unicode_buffer(MAX_PATH)
    nSize = DWORD()
    if not windll.Psapi.GetModuleFileNameExW(
            hProcess, hModule, byref(buf), byref(nSize)):
        raise OSError('GetModuleFileNameEx failed')
    return buf.value

def get_process_modules(pid):
    hProcess = windll.Kernel32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
            False, pid)
    if not hProcess:
        raise OSError('Could not open PID %s' % pid)
    try:
        return [
            [ hModule.value, GetModuleFileNameEx(hProcess, hModule) ]
            for hModule in EnumProcessModulesEx(hProcess)]
    finally:
        windll.Kernel32.CloseHandle(hProcess)

def getmodule(procname, modname):
    procname = '\\' + procname
    modname = '\\' + modname
    for pid in EnumProcesses():
        try:
            dll_list = get_process_modules(pid)
            if dll_list[0][1].endswith(procname):
                for pair in dll_list:
                    if pair[1].endswith(modname):
                        return [pid, pair[0]]
        except OSError as ose:
            #print(str(ose))
            pass

##
## figure out what character encoding is used for japanese
##

def chardet(input, expect):
    for src in tcodecs:
        try:
            tmp3 = input.decode(src)
        except:
            continue
        for via in tcodecs:
            try:
                tmp = tmp3.encode(via)
            except:
                continue
            for enc in tcodecs:
                try:
                    tmp2 = tmp.decode(enc).encode('utf-8')
                    if tmp2.startswith(expect):
                        print(src, via, enc)
                except:
                    continue

def mecab(txt):
    cmd = [ 'c:\\Program Files (x86)\\MeCab\\bin\\mecab.exe' ]
    proc = subprocess.Popen(cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=False)
    txt = txt.encode('utf-8')
    stdout = proc.communicate(input=txt)[0]
    kana = ''
    html = ''
    for line in iter(stdout.decode('utf-8').splitlines()):
        if line == 'EOS':
            kana += '\n'
            html += '\n'
            continue
        conv = line.split(',')[-2]
        orig = line.split('\t')[0]
        if conv == '*':
            conv = orig
        yomi = ''
        for ch in conv:
            co = ord(ch)
            # hiragana >= 0x3041 and <= 0x3096
            # katakana >= 0x30a1 and <= 0x30f6
            if co >= 0x30a1 and co <= 0x30f6:
                yomi += chr(co - (0x30a1 - 0x3041))
            else:
                yomi += ch
        if yomi == orig:
            kana += orig
            html += orig
        else:
            kana += yomi
            html += (
                '<table><tr><td class="sup">{0}</td></tr>' +
                '<tr><td>{1}</td></tr></table>').format(
                    yomi, orig)
    return [ kana, html ]

##
## change terminal color
##

def color(c):
    # w: black blue green cyan red magenta yellow grey
    # u: black red green yellow blue magenta cyan grey
    cmap = [ 0, 4, 2, 6, 1, 5, 3, 7 ]
    
    # normal=0 bright_fg=8 bright_bg=128
    # fg + bg * 16 + (style | light)
    attrs = cmap[c % 8] + int(c / 8) * 8
    attrs = int(attrs)
    
    # stdout=-11 stderr=-12
    handle = -11
    
    mc = windll.kernel32.GetStdHandle
    mc.argtypes = [ DWORD ]
    handle = mc(handle)
    
    mc = windll.kernel32.SetConsoleTextAttribute
    mc.argtypes = [ HANDLE, WORD ]
    mc(handle, attrs)

def printc(c, *args, **kwargs):
    color(c)
    print(*args, flush=True, **kwargs)
    color(7)

##
## httpd
##

current_text = None
class Httpd(object):
    def __init__(self):
        self.text = ''
        thr = threading.Thread(target=self.run, args=())
        thr.daemon = True
        thr.start()
    
    def set(self, text):
        self.text = text
    
    def run(self):
        old_text = self.text
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', 8086))
        s.listen(1)
        while True:
            try:
                conn, addr = s.accept()
                data = conn.recv(4096)
                if not data:
                    conn.close()
                    continue
                data = data.decode('utf-8')
                if not data.startswith('GET /the.html HTTP/1.1'):
                    msg = 'HTTP/1.1 404 Not Found\r\nContent-Length: 4\r\nConnection: close\r\n\r\nnope'
                    conn.sendall(msg.encode('utf-8'))
                    time.sleep(0.1)
                    conn.close()
                    continue
                response = """HTTP/1.1 200 OK\r
Content-Type: text/html\r
Connection: close\r
\r
<!DOCTYPE html><html lang="en"><head>
    <meta charset="utf-8">
    <title>rabi-ribi</title>
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=0.6">
    <style>
html,body,#t,#t>tr,#t>tr>td {
    width: 100%;
    height: 100%;
    overflow: hidden;
    font-family: sans-serif;
    background: #fff;
    color: #000;
}
#t2 {
    font-size: 2em;
    text-align: center;
    line-height: 1.3em;
}
td table {
    display: inline-block;
    border-bottom: 1px solid #aaa;
    border-radius: .3em;
}
td table,
td table * {
    margin: 0;
    padding: 0;
    border-collapse: collapse;
    line-height: 1.1em;
    margin-bottom: -.15em;
}
.sup {
    font-size: .7em;
}
#hidden {
    display: none;
}
#ja {
    line-height: 2em;
}

</style></head><body>
    <table id="t"><tr><td id="t2">
""" + self.text.replace('\n', '<br />\r\n') + """
    </td></tr></table>
    <div id="hidden">
"""
                conn.sendall(response.encode('utf-8'))
                while self.text == old_text:
                    conn.sendall('.'.encode('utf-8'))
                    for n in range(10):
                        if self.text != old_text:
                            break
                        time.sleep(0.1)
                old_text = self.text
                response = """
</div><script>
    window.location.reload(true);
</script></body></html>"""
                conn.sendall(response.encode('utf-8'))
                time.sleep(0.1)
                conn.close()
            except:
                pass

httpd = Httpd()

##
## parse game files
##

def parse_rbrb(path, enc):
    rbrb = []
    scene_id = None
    scene_lines = None
    with open(path, 'rb') as f:
        f.readline()
        for n, line in enumerate(f):
            line = line.decode(enc).strip()
            if line.startswith('//'):
                continue
            if not line:
                if scene_id is not None:
                    rbrb.append([
                        scene_id,
                        scene_lines
                    ])
                scene_id = None
                scene_lines = None
                continue
            if scene_id is None:
                try:
                    scene_id = int(line)
                    scene_lines = []
                except:
                    printc(8+1, 'fuck {0} line {1}'.format(path, n+2))
                continue
            scene_lines.append(line)
    return rbrb

path = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Rabi-Ribi\\localize\\event\\'
rb_en = parse_rbrb(path + 'story_en.rbrb', 'utf-8')
rb_ja = parse_rbrb(path + 'story_jp.rbrb', 'cp932')
printc(8+3, 'rb_en entries:', len(rb_en))
printc(8+3, 'rb_ja entries:', len(rb_ja))

##
## it begins
##

pid, mod = getmodule('rabiribi.exe', 'rabiribi.exe')
proc = OpenProcess(PROCESS_ALL_ACCESS, False, pid)

buflen = 512
numread = c_ulong(0)
buf = (c_ubyte * buflen)()
#ptr = cast(addressof(buf), POINTER(c_ubyte))

def read_mem(adr, len):
    global proc, buf, numread
    if not ReadProcessMemory(proc, adr, buf, len, byref(numread)):
        print('read err')
        exit(1)

def read_int(adr):
    global buf
    #print('reading int32 @ {0:x}'.format(adr))
    read_mem(adr, 4)
    return struct.unpack('<L', string_at(addressof(buf), 4))[0]

last_block_id = None
last_block_pos = None
while True:
    block_id = read_int(read_int(mod + ADR_BLOCK_ID))
    block_pos = read_int(read_int(mod + ADR_BLOCK_POS))
    if block_id == last_block_id and block_pos == last_block_pos:
        time.sleep(0.5)
        continue
    last_block_id = block_id
    last_block_pos = block_pos
    printc(8+3, 'scene {0} line {1}'.format(
        block_id, block_pos))
    print()
    
    html_text = ''
    if block_id > 0:
        new_text = ''
        en = next(x for x in rb_en if x[0] == block_id)[1][block_pos].strip()
        ja = next(x for x in rb_ja if x[0] == block_id)[1][block_pos].strip()
        
        printc(8+3, 'ka: ', end='')
        lines = ja.replace('@', '\n    ')
        print(lines.strip(), '\n')
        
        printc(8+3, 'hi: ', end='')
        lines = ja.replace('@', '\n')
        kana, html = mecab(lines)
        html_text += '<div id="ja">{0}</div>\n'.format(html.strip())
        print(kana.strip().replace('\n', '\n    '), '\n')
        
        printc(8+3, 'en: ', end='')
        lines = en.replace('@', '\n    ')
        html_text += lines.strip()
        print(lines.strip(), '\n')
    
    current_text = new_text
    httpd.set(html_text)

CloseHandle(proc)
