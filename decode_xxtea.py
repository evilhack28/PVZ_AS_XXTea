"""
Decode cocos2d-x XXTEA-encrypted text files.

Matches the C++ code in UtilityHelper::ReadTextFromBin / DBCFile_OpenFromMemory:
    setXXTEAKeyAndSign("7ec34b808tk94hf1", 0x10, "XXTEA", 5);
    xxtea_decrypt(data+5, len-5, "7ec34b808tk94hf1", 16, &out_len);

The cocos2d-x xxtea variant pads the ciphertext with zero bytes up to a
multiple of 4, runs standard XXTEA decrypt over the 32-bit little-endian
word array, and stores the plaintext length in the *last* word of the
output buffer (i.e. xxtea_to_byte_array(..., include_length=1)).
"""

import os
import struct
import sys

DELTA = 0x9E3779B9
KEY = b"7ec34b808tk94hf1"
SIGN = b"XXTEA"


def _to_longs(data: bytes, include_length: bool):
    n = len(data)
    if include_length:
        # number of 32-bit words to hold n bytes, plus 1 trailing length word
        nw = (n + 3) // 4
        out = [0] * (nw + 1)
        out[nw] = n
    else:
        nw = (n + 3) // 4
        out = [0] * nw
    for i, b in enumerate(data):
        out[i >> 2] |= b << ((i & 3) * 8)
    return out


def _from_longs(v, use_length_word: bool):
    n = len(v)
    if use_length_word:
        # last word is the plaintext length
        m = v[n - 1]
        n -= 1
        max_bytes = n * 4
        if m < 0 or m > max_bytes or (max_bytes - m) > 3:
            # length word looks bogus; fall back to raw bytes
            m = max_bytes
    else:
        m = n * 4
    out = bytearray(m)
    for i in range(m):
        out[i] = (v[i >> 2] >> ((i & 3) * 8)) & 0xFF
    return bytes(out)


def _u32(x):
    return x & 0xFFFFFFFF


def xxtea_decrypt(data: bytes, key: bytes) -> bytes:
    if len(data) == 0:
        return b""
    # key must be 16 bytes (4 words)
    k = list(struct.unpack("<4I", key.ljust(16, b"\0")[:16]))
    v = _to_longs(data, include_length=False)
    n = len(v)
    if n < 2:
        return _from_longs(v, use_length_word=True)
    rounds = 6 + 52 // n
    sum_ = _u32(rounds * DELTA)
    y = v[0]
    while sum_ != 0:
        e = (sum_ >> 2) & 3
        for p in range(n - 1, 0, -1):
            z = v[p - 1]
            mx = (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_ ^ y) + (k[(p & 3) ^ e] ^ z))
            v[p] = _u32(v[p] - mx)
            y = v[p]
        z = v[n - 1]
        mx = (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_ ^ y) + (k[(0 & 3) ^ e] ^ z))
        v[0] = _u32(v[0] - mx)
        y = v[0]
        sum_ = _u32(sum_ - DELTA)
    return _from_longs(v, use_length_word=True)


def decode_file(path: str) -> bytes:
    with open(path, "rb") as f:
        blob = f.read()
    if not blob.startswith(SIGN):
        # already plain
        return blob
    return xxtea_decrypt(blob[len(SIGN):], KEY)


def to_utf8(plain: bytes) -> bytes:
    # Source files are GBK (Simplified Chinese). Re-encode as UTF-8.
    # gb18030 is a superset of GBK/GB2312 and decodes everything cleanly.
    try:
        text = plain.decode("gb18030")
    except UnicodeDecodeError:
        # Already UTF-8 or pure ASCII — leave bytes alone.
        return plain
    return text.encode("utf-8")


def walk_and_decode(root: str, out_root: str, reencode_utf8: bool = True):
    count_ok = 0
    count_skip = 0
    for dirpath, _, files in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        out_dir = os.path.join(out_root, rel) if rel != "." else out_root
        os.makedirs(out_dir, exist_ok=True)
        for name in files:
            src = os.path.join(dirpath, name)
            dst = os.path.join(out_dir, name)
            try:
                plain = decode_file(src)
                if reencode_utf8:
                    plain = to_utf8(plain)
                with open(dst, "wb") as f:
                    f.write(plain)
                count_ok += 1
            except Exception as e:
                print(f"SKIP {src}: {e}", file=sys.stderr)
                count_skip += 1
    return count_ok, count_skip


if __name__ == "__main__":
    if len(sys.argv) == 2:
        # single-file dump to stdout (first 400 bytes)
        plain = decode_file(sys.argv[1])
        sys.stdout.buffer.write(plain[:400])
        sys.stdout.buffer.write(b"\n---\n")
        print(f"[decoded {len(plain)} bytes]")
    elif len(sys.argv) == 3:
        ok, skip = walk_and_decode(sys.argv[1], sys.argv[2])
        print(f"decoded {ok} files, skipped {skip}")
    else:
        print("usage: decode_xxtea.py <file>            # preview one", file=sys.stderr)
        print("       decode_xxtea.py <in_dir> <out_dir>  # batch", file=sys.stderr)
        sys.exit(2)
