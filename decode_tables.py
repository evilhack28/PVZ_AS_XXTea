import os
import struct
import sys
from concurrent.futures import ProcessPoolExecutor

DELTA = 0x9E3779B9
XXTEA_KEY = b"7ec34b808tk94hf1"
XXTEA_SIGN = b"XXTEA"
DES_KEY = b"1234567\x00"
DBC_MAGIC = 0xDDBBCC00


class DecodeError(Exception):
    pass


def _to_longs(data: bytes, include_length: bool):
    n = len(data)
    nw = (n + 3) // 4
    padded = data.ljust(nw * 4, b"\0")
    v = list(struct.unpack(f"<{nw}I", padded)) if nw else []
    if include_length:
        v.append(n)
    return v


def _from_longs(v, use_length_word: bool):
    n = len(v)
    if use_length_word:
        m = v[n - 1]  # trailing word is the real plaintext length
        n -= 1
        max_bytes = n * 4
        if m < 0 or m > max_bytes or (max_bytes - m) > 3:
            m = max_bytes  # bogus length word, fall back to raw bytes
        words = v[:n]
    else:
        m = n * 4
        words = v
    packed = struct.pack(f"<{len(words)}I", *words) if words else b""
    return packed[:m]


def xxtea_decrypt(data: bytes, key: bytes) -> bytes:
    if len(data) == 0:
        return b""
    k = list(struct.unpack("<4I", key.ljust(16, b"\0")[:16]))
    v = _to_longs(data, include_length=False)
    n = len(v)
    if n < 2:
        return _from_longs(v, use_length_word=True)
    rounds = 6 + 52 // n
    sum_ = (rounds * DELTA) & 0xFFFFFFFF
    y = v[0]
    while sum_ != 0:
        e = (sum_ >> 2) & 3
        for p in range(n - 1, 0, -1):
            z = v[p - 1]
            mx = (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_ ^ y) + (k[(p & 3) ^ e] ^ z))
            y = (v[p] - mx) & 0xFFFFFFFF
            v[p] = y
        z = v[n - 1]
        mx = (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4))) ^ ((sum_ ^ y) + (k[e] ^ z))
        y = (v[0] - mx) & 0xFFFFFFFF
        v[0] = y
        sum_ = (sum_ - DELTA) & 0xFFFFFFFF
    return _from_longs(v, use_length_word=True)


def _looks_like_text(data: bytes) -> bool:
    if not data:
        return True
    for enc in ("gb18030", "utf-8"):
        try:
            data.decode(enc)
            return True
        except UnicodeDecodeError:
            pass
    return False


def des_decrypt(data: bytes, key: bytes = DES_KEY) -> bytes:
    if len(data) == 0:
        return b""
    if len(data) % 8 != 0:
        raise DecodeError(f"DES ciphertext length {len(data)} is not a multiple of 8")
    try:
        from Crypto.Cipher import DES
    except ImportError as e:
        raise DecodeError("des format requires pycryptodome (`pip install pycryptodome`)") from e
    return DES.new(key, DES.MODE_ECB).decrypt(data)


def _dbc_rows(field_types, field_count, record_count, records_raw, string_block):
    rows = []
    for r in range(record_count):
        row = []
        for c in range(field_count):
            raw = records_raw[(r * field_count + c) * 4:(r * field_count + c) * 4 + 4]
            t = field_types[c]
            if t == 0:
                row.append(struct.unpack("<i", raw)[0])
            elif t == 1:
                row.append(struct.unpack("<f", raw)[0])
            elif t == 2:
                (soff,) = struct.unpack("<I", raw)
                end = string_block.find(b"\0", soff)
                row.append(string_block[soff:end] if end != -1 else string_block[soff:])
            else:
                raise DecodeError(f"unknown DBC field type {t} in column {c}")
        rows.append(row)
    return rows


def parse_dbc_binary(data: bytes):
    """Parse a DES-decrypted DBC::DBCFile OpenFromMemoryImpl_Binary blob into (field_types, rows)."""
    if len(data) < 16:
        raise DecodeError("DBC blob shorter than the 16-byte header")
    magic, field_count, record_count, str_block_size = struct.unpack_from("<4I", data, 0)
    if magic != DBC_MAGIC:
        raise DecodeError(f"DBC magic mismatch: got {magic:#010x}, expected {DBC_MAGIC:#010x}")
    types_end = 16 + field_count * 4
    header_size = types_end + field_count * record_count * 4
    if header_size + str_block_size > len(data):
        raise DecodeError(f"DBC blob too short: need {header_size + str_block_size} bytes, have {len(data)}")
    field_types = struct.unpack_from(f"<{field_count}I", data, 16)
    records_raw = data[types_end:types_end + field_count * record_count * 4]
    string_block = data[types_end + field_count * record_count * 4: header_size + str_block_size]
    rows = _dbc_rows(field_types, field_count, record_count, records_raw, string_block)
    return field_types, rows


def parse_dbc_plain(data: bytes):
    """Parse an unencrypted (pre-DES-era) DBC blob: same field_types/records/string_block
    layout as parse_dbc_binary, but with two extra NUL-terminated header text lines (a
    display-name row and a field-name row) between the 24-byte numeric header and the
    field_types array. No encryption at all — the magic is visible in the raw file.
    Returns (field_types, rows, header_lines) where header_lines is (display_line,
    fieldname_line) decoded as text, or None if they can't be decoded."""
    if len(data) < 24:
        raise DecodeError("DBC blob shorter than the 24-byte header")
    magic, field_count, record_count, _len2, _len1, str_block_size = struct.unpack_from("<6I", data, 0)
    if magic != DBC_MAGIC:
        raise DecodeError(f"DBC magic mismatch: got {magic:#010x}, expected {DBC_MAGIC:#010x}")
    end1 = data.index(b"\0", 24)
    end2 = data.index(b"\0", end1 + 1)
    display_line = data[24:end1]
    fieldname_line = data[end1 + 1:end2]
    types_start = end2 + 1
    types_end = types_start + field_count * 4
    header_size = types_end + field_count * record_count * 4
    if header_size + str_block_size > len(data):
        raise DecodeError(f"DBC blob too short: need {header_size + str_block_size} bytes, have {len(data)}")
    field_types = struct.unpack_from(f"<{field_count}I", data, types_start)
    records_raw = data[types_end:types_end + field_count * record_count * 4]
    string_block = data[types_end + field_count * record_count * 4: header_size + str_block_size]
    rows = _dbc_rows(field_types, field_count, record_count, records_raw, string_block)

    def decode_line(b):
        try:
            return b.decode("gb18030")
        except UnicodeDecodeError:
            return b.decode("utf-8", errors="replace")

    header_lines = (decode_line(display_line), decode_line(fieldname_line))
    return field_types, rows, header_lines


_DBC_TYPE_NAMES = {0: "INT", 1: "FLOAT", 2: "STRING"}


def dbc_to_table_text(field_types, rows, header_lines=None) -> bytes:
    lines = []
    if header_lines:
        lines.append(header_lines[0])
        lines.append("\t".join(_DBC_TYPE_NAMES[t] for t in field_types))
        lines.append(header_lines[1])
    else:
        lines.append("\t".join(_DBC_TYPE_NAMES[t] for t in field_types))
    for row in rows:
        cells = []
        for v in row:
            if isinstance(v, bytes):
                try:
                    cells.append(v.decode("gb18030"))
                except UnicodeDecodeError:
                    cells.append(v.decode("utf-8", errors="replace"))
            elif isinstance(v, float):
                cells.append(repr(v))
            else:
                cells.append(str(v))
        lines.append("\t".join(cells))
    return ("\n".join(lines) + "\n").encode("utf-8")


def to_utf8(plain: bytes) -> bytes:
    """Re-encode GBK table text as UTF-8 (no-op if it's already UTF-8/ASCII)."""
    try:
        return plain.decode("gb18030").encode("utf-8")
    except UnicodeDecodeError:
        return plain


def write_xlsx(text_bytes: bytes, path: str) -> str:
    """Write tab-separated table text out as a real .xlsx workbook. Returns the actual path written (.xls is corrected to .xlsx, since the file content is always modern OOXML, not legacy .xls)."""
    from openpyxl import Workbook

    if not path.lower().endswith(".xlsx"):
        path = os.path.splitext(path)[0] + ".xlsx"
    wb = Workbook()
    ws = wb.active
    for line in text_bytes.decode("utf-8").splitlines():
        ws.append(line.split("\t"))
    wb.save(path)
    return path


_DBC_MAGIC_BYTES = struct.pack("<I", DBC_MAGIC)


def decode_file(path: str):
    """Decode one file, auto-detecting its format. Returns (plain_bytes, format_used).

    Formats seen across game versions, in detection order:
      0. Genuine legacy .xls (real OLE2 file)   -> not ours, passed through as-is
      1. XXTEA-signed text (1.0.105+)           -> sign "XXTEA" present
      2. Already-plain GBK/UTF-8 text            -> no sign, decodes as text
      3. Plain (unencrypted) DBC binary (early)  -> no sign, DBC magic visible raw
      4. DES-encrypted DBC binary (1.0.4)        -> no sign, none of the above
    """
    with open(path, "rb") as f:
        blob = f.read()

    if blob.startswith(b"\xd0\xcf\x11\xe0"):
        return blob, "xls_passthrough"  # real pre-existing Excel file, nothing to decode

    if blob.startswith(XXTEA_SIGN):
        plain = xxtea_decrypt(blob[len(XXTEA_SIGN):], XXTEA_KEY)
        if not _looks_like_text(plain):
            raise DecodeError(f"{path}: decrypted but result is not valid text — wrong key or corrupt file")
        return plain, "xxtea"

    if blob.startswith(_DBC_MAGIC_BYTES):
        return dbc_to_table_text(*parse_dbc_plain(blob)), "dbc"

    if _looks_like_text(blob):
        return blob, "xxtea"  # already-plain text, no sign needed

    plain = des_decrypt(blob)
    try:
        return dbc_to_table_text(*parse_dbc_binary(plain)), "des"
    except DecodeError:
        return dbc_to_table_text(*parse_dbc_plain(plain)), "des"  # DES + header-lines variant


def _decode_one(src: str, dst: str, as_text: bool):
    try:
        plain, used = decode_file(src)
        if used == "xls_passthrough":
            dst = os.path.splitext(dst)[0] + ".xls"
            with open(dst, "wb") as f:
                f.write(plain)
            return True, src, None
        if used == "xxtea":
            plain = to_utf8(plain)  # dbc/des output is already UTF-8 text
        if as_text:
            with open(dst, "wb") as f:
                f.write(plain)
        else:
            write_xlsx(plain, dst)
        return True, src, None
    except Exception as e:
        return False, src, str(e)


def walk_and_decode(root: str, out_root: str, as_text: bool = False):
    """Batch-decode every file under root into out_root, mirroring the folder structure.
    as_text=False (default) writes one .xlsx per file; as_text=True writes plain .txt,
    which is easier to diff (git diff, text compare tools) across game versions."""
    out_ext = ".txt" if as_text else ".xlsx"
    jobs = []
    for dirpath, _, files in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        out_dir = os.path.join(out_root, rel) if rel != "." else out_root
        os.makedirs(out_dir, exist_ok=True)
        for name in files:
            dst = os.path.join(out_dir, os.path.splitext(name)[0] + out_ext)
            jobs.append((os.path.join(dirpath, name), dst, as_text))

    count_ok = count_skip = 0
    with ProcessPoolExecutor() as pool:
        for ok, src, err in pool.map(_decode_one, *zip(*jobs)) if jobs else []:
            if ok:
                count_ok += 1
            else:
                print(f"SKIP {src}: {err}", file=sys.stderr)
                count_skip += 1
    return count_ok, count_skip


if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            plain, used = decode_file(sys.argv[1])
        except DecodeError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"[format: {used}]")
        if used == "xls_passthrough":
            print(f"[{len(plain)} bytes, already a real .xls — nothing to decode]")
        else:
            preview = to_utf8(plain) if used == "xxtea" else plain
            sys.stdout.buffer.write(preview.decode("utf-8", errors="replace")[:400].encode("utf-8"))
            sys.stdout.buffer.write(b"\n---\n")
            print(f"[decoded {len(plain)} bytes]")
    elif len(sys.argv) == 3 and os.path.isfile(sys.argv[1]):
        try:
            plain, used = decode_file(sys.argv[1])
        except DecodeError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        if used == "xxtea":
            plain = to_utf8(plain)
        if sys.argv[2].lower().endswith(".xlsx"):
            saved_path = write_xlsx(plain, sys.argv[2])
        else:
            saved_path = sys.argv[2]
            with open(saved_path, "wb") as f:
                f.write(plain)
        print(f"saved {saved_path}")
    elif len(sys.argv) == 4 and sys.argv[3] == "--txt":
        ok, skip = walk_and_decode(sys.argv[1], sys.argv[2], as_text=True)
        print(f"decoded {ok} files, skipped {skip}")
    elif len(sys.argv) == 3:
        ok, skip = walk_and_decode(sys.argv[1], sys.argv[2])
        print(f"decoded {ok} files, skipped {skip}")
    else:
        print("usage: decode_tables.py <file>                  # preview one", file=sys.stderr)
        print("       decode_tables.py <file> <out.xlsx|out.txt> # decode one file", file=sys.stderr)
        print("       decode_tables.py <in_dir> <out_dir>         # batch, one .xlsx per file", file=sys.stderr)
        print("       decode_tables.py <in_dir> <out_dir> --txt   # batch, one .txt per file", file=sys.stderr)
        sys.exit(2)
