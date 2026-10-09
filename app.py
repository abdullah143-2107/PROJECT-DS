"""
PDF File Structure & Damage Simulator
Binary Manipulation, Header Integrity Analysis & Recovery Lab

100% Python web application (Streamlit). Works in any browser - desktop or phone.
Run locally:   pip install streamlit   then   streamlit run app.py
Theme: green & black with a Matrix-rain background.
"""
import random
from html import escape

import streamlit as st

st.set_page_config(page_title="PDF Damage & Recovery Simulator", page_icon="🛡", layout="wide")

SAMPLE_PDF = """%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 140] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 55 >>
stream
BT
/F1 18 Tf
20 80 Td
(PDF Integrity Test Sample) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000246 00000 n 
0000000350 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
423
%%EOF"""

# ------------------------------------------------------------------ theme + background
def matrix_rain_html(columns=46, rows=26):
    """Matrix-rain background generated in Python (pure CSS animation)."""
    chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ0123456789ABCDEF"
    rnd = random.Random(7)
    cols = []
    for i in range(columns):
        text = "<br>".join(rnd.choice(chars) for _ in range(rows))
        left = i * (100 / columns)
        dur = rnd.uniform(7, 16)
        delay = -rnd.uniform(0, 16)
        cols.append(f'<div class="rc" style="left:{left:.2f}%;animation-duration:{dur:.1f}s;'
                    f'animation-delay:{delay:.1f}s">{text}</div>')
    return '<div class="rain">' + "".join(cols) + "</div>"


CSS = """<style>
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:#030805 !important}
[data-testid="stToolbar"]{display:none}
.block-container{position:relative;z-index:1;max-width:1250px;padding-top:1rem !important}
.rain{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none;opacity:.38}
.rc{position:absolute;top:0;width:16px;line-height:16px;font:15px/16px monospace;color:#00ff66;text-align:center;
 text-shadow:0 0 6px #00ff66;animation:fall linear infinite;
 -webkit-mask-image:linear-gradient(to bottom,transparent,#000 85%);mask-image:linear-gradient(to bottom,transparent,#000 85%)}
@keyframes fall{from{transform:translateY(-100%)}to{transform:translateY(100vh)}}
.scan{position:fixed;inset:0;pointer-events:none;z-index:999;background:repeating-linear-gradient(0deg,rgba(0,0,0,.18) 0 1px,transparent 1px 3px)}
[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(6,33,15,.88);border:1px solid #0f4a28 !important;border-radius:12px}
.hdr{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;background:rgba(2,10,5,.92);
 border:1px solid #0f4a28;border-radius:12px;padding:14px 20px;margin-bottom:16px}
.hdr h1{margin:0;font-size:1.35rem;color:#00ff66;text-shadow:0 0 12px #00ff6666;padding:0}
.hdr p{margin:2px 0 0;color:#6fb98c;font-size:.78rem}
.pill{border:1px solid #0f4a28;background:#06210f;border-radius:20px;padding:5px 14px;font-size:.75rem;color:#d8ffe7}
.pill:before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:#00ff66;margin-right:8px;box-shadow:0 0 8px #00ff66}
.sec{color:#00ff66;font-weight:700;font-size:.82rem;letter-spacing:.08em;margin:0 0 6px}
.stat{background:rgba(6,33,15,.88);border:1px solid #0f4a28;border-radius:12px;padding:12px;text-align:center}
.stat small{display:block;color:#6fb98c;font-size:.65rem;letter-spacing:.1em}
.stat b{display:block;margin-top:4px;font-size:1rem}
.ok{color:#34d399}.bad{color:#fb7185}
.hexbox{background:#020a05;border:1px solid #0f4a28;border-radius:8px;padding:10px;font:12px/1.55 Consolas,monospace;
 white-space:pre;overflow:auto;max-height:380px;min-height:200px;color:#b6ffd2}
.hexrow{display:flex;justify-content:space-between;gap:16px}
.off{color:#4a8f65}.hd{color:#34d399;font-weight:700}.xx{color:#fb7185;font-weight:700}.asc{color:#6fb98c;border-left:1px solid #0f4a28;padding-left:12px}
.logbox{background:#020a05;border:1px solid #0f4a28;border-radius:8px;padding:8px 10px;font:12px/1.5 Consolas,monospace;height:110px;overflow:auto;color:#6fb98c}
.logbox p{margin:0}.l-success{color:#34d399}.l-warning{color:#fbbf24}.l-error{color:#fb7185}
.tag{background:#0f4a28;color:#86ffb4;font:11px Consolas,monospace;padding:2px 8px;border-radius:4px;float:right}
.stButton>button,.stDownloadButton>button{border-radius:8px;font-weight:700;border:1px solid #00a847;background:#06210f;color:#d8ffe7}
.stButton>button:hover:not(:disabled),.stDownloadButton>button:hover:not(:disabled){background:#00ff66;color:#000;border-color:#00ff66}
.stButton>button:disabled,.stDownloadButton>button:disabled{opacity:.4}
[data-testid="stFileUploaderDropzone"]{background:#020a05;border:2px dashed #0f4a28;border-radius:10px}
</style>"""

st.markdown(CSS + matrix_rain_html() + '<div class="scan"></div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ session state
S = st.session_state
S.setdefault("original", None)
S.setdefault("current", None)
S.setdefault("name", "sample_document.pdf")
S.setdefault("label", "Original State")
S.setdefault("logs", [("info", "System initialized. Ready for file input.")])


def log(msg, kind="info"):
    S.logs.append((kind, msg))


# ------------------------------------------------------------------ core logic (callbacks)
def on_upload():
    f = S.get("uploader")
    if f is None:
        return
    data = f.getvalue()
    S.original = data
    S.current = data
    S.name = f.name
    S.label = "Original File Loaded"
    log(f"Loaded file: {f.name} ({len(data)} bytes)", "success")


def on_sample():
    S.original = SAMPLE_PDF.encode("utf-8")
    S.current = S.original
    S.name = "sample_test_doc.pdf"
    S.label = "Sample PDF Loaded"
    log("Generated sample PDF minimal structure.", "info")


def on_corrupt():
    if S.original is None:
        return
    mode = S.mode
    data = bytearray(S.original)  # reset to original first

    if mode == "Corrupt Magic Header":
        data[0:4] = b"XXXX"
        log("Corrupted Header magic bytes (%PDF -> XXXX).", "error")
    elif mode == "Strip EOF / Trailer Marker":
        pos = bytes(data).rfind(b"%%EOF")
        if pos != -1:
            data = data[:pos]
            log("Truncated '%%EOF' trailer marker from file tail.", "error")
        else:
            log("Trailer '%%EOF' not found to remove.", "warning")
    else:  # Random Bit Flipping / Noise
        percent = int(S.noise)
        flips = max(1, len(data) * percent // 100)
        span = max(1, len(data) - 20)
        for _ in range(flips):
            idx = random.randrange(span) + 10
            if idx < len(data):
                data[idx] = random.randrange(256)
        log(f"Injected {flips} random corrupted bytes ({percent}% noise).", "error")

    S.current = bytes(data)
    S.label = "Damaged / Corrupted"


def on_repair():
    if S.current is None:
        return
    log("Executing recovery scanner...", "info")
    repaired = S.current

    if not repaired[:8].decode("utf-8", errors="replace").startswith("%PDF-"):
        log("Header anomaly detected. Injecting standard %PDF-1.4 header.", "warning")
        repaired = b"%PDF-1.4\n" + repaired

    if b"%%EOF" not in repaired[-20:]:
        log("Missing EOF trailer detected. Appending '%%EOF' marker.", "warning")
        repaired = repaired + b"\n%%EOF\n"

    S.current = repaired
    S.label = "Repaired State"
    log("Repair protocol completed.", "success")


# ------------------------------------------------------------------ rendering helpers
def hex_view(data):
    chunk = data[:512]
    rows = []
    for start in range(0, len(chunk), 16):
        part = chunk[start:start + 16]
        cells = []
        for j, b in enumerate(part):
            i = start + j
            cls = ""
            if i < 8 and chunk[0] == 0x25 and chunk[1] == 0x50:
                cls = "hd"
            elif b == 0x58:
                cls = "xx"
            cells.append(f'<span class="{cls}">{b:02X}</span>')
        pad = "   " * (16 - len(part))
        ascii_txt = "".join(chr(b) if 32 <= b <= 126 else "." for b in part)
        rows.append(f'<div class="hexrow"><div><span class="off">{start:06x}</span>  '
                    f'{" ".join(cells)}{pad}</div><div class="asc">{escape(ascii_txt)}</div></div>')
    if len(data) > 512:
        rows.append(f'<div style="text-align:center;color:#4a8f65;font-style:italic;padding:6px">'
                    f'... ({len(data) - 512} additional bytes omitted for preview) ...</div>')
    return '<div class="hexbox">' + "".join(rows) + "</div>"


# ------------------------------------------------------------------ header
st.markdown(
    '<div class="hdr"><div><h1>▣ PDF File Structure &amp; Damage Simulator</h1>'
    '<p>Binary Manipulation, Header Integrity Analysis &amp; Recovery Lab</p></div>'
    '<div class="pill">Academic Lab Mode</div></div>', unsafe_allow_html=True)

left, right = st.columns([5, 7], gap="medium")

# ------------------------------------------------------------------ left panel
with left:
    with st.container(border=True):
        st.markdown('<p class="sec">1. SELECT INPUT DOCUMENT</p>', unsafe_allow_html=True)
        st.file_uploader("Drop PDF here or click to browse", type=["pdf"], key="uploader",
                         on_change=on_upload, help="Files are processed entirely in memory.")
        st.markdown('<p style="text-align:center;color:#6fb98c;margin:0">— OR —</p>', unsafe_allow_html=True)
        st.button("📄 Generate Sample Minimal PDF", on_click=on_sample, use_container_width=True)

    with st.container(border=True):
        st.markdown('<p class="sec">2. CONFIGURE CORRUPTION STRATEGY</p>', unsafe_allow_html=True)
        st.radio("Corruption strategy", [
            "Corrupt Magic Header",
            "Strip EOF / Trailer Marker",
            "Random Bit Flipping / Noise"], key="mode", label_visibility="collapsed",
            captions=["Replaces %PDF-1.x signature with dummy characters (XXXX). Readers refuse the file.",
                      "Removes trailing %%EOF tag. Causes parser structure lookup errors.",
                      "Simulates network noise or disk degradation across internal streams."])
        st.slider("Noise level (%)", 1, 10, 2, key="noise",
                  disabled=S.get("mode") != "Random Bit Flipping / Noise")
        b1, b2 = st.columns(2)
        b1.button("⚡ Apply Damage", on_click=on_corrupt, disabled=S.current is None, use_container_width=True)
        b2.button("✚ Attempt Repair", on_click=on_repair, disabled=S.current is None, use_container_width=True)

    with st.container(border=True):
        st.markdown('<p class="sec">3. MODIFIED FILE OUTPUT</p>', unsafe_allow_html=True)
        status = f"{S.label} ({len(S.current)} bytes)" if S.current is not None else "No file loaded"
        st.caption(status)
        st.download_button("⬇ Save Output File", data=S.current or b"", file_name=f"corrupted_{S.name}",
                           mime="application/pdf", disabled=S.current is None, use_container_width=True)

# ------------------------------------------------------------------ right panel
with right:
    data = S.current
    if data is None:
        magic, magic_cls, eof, eof_cls, size = "--", "", "--", "", "0 Bytes"
    else:
        head = data[:8].decode("latin-1").replace("\r", "").replace("\n", "")
        tail = data[-12:].decode("latin-1").replace("\r", "").replace("\n", "")
        magic, magic_cls = escape(head[:8]), ("ok" if head.startswith("%PDF-") else "bad")
        has_eof = "%%EOF" in tail
        eof, eof_cls = ("Valid (%%EOF)" if has_eof else "Missing / Broken"), ("ok" if has_eof else "bad")
        size = f"{len(data)} B"

    c1, c2, c3 = st.columns(3)
    for col, title, val, cls in ((c1, "MAGIC HEADER", magic, magic_cls),
                                 (c2, "EOF MARKER", eof, eof_cls),
                                 (c3, "FILE SIZE", size, "")):
        col.markdown(f'<div class="stat"><small>{title}</small><b class="{cls}">{val}</b></div>',
                     unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<span class="tag">{escape(S.label)}</span><p class="sec">▸ BINARY HEX INSPECTOR</p>',
                    unsafe_allow_html=True)
        if data is None:
            st.markdown('<div class="hexbox" style="text-align:center;padding-top:80px;color:#4a8f65">'
                        'Load or generate a PDF file to inspect byte structures...</div>', unsafe_allow_html=True)
        else:
            st.markdown(hex_view(data), unsafe_allow_html=True)

        st.markdown('<p class="sec" style="margin-top:12px;color:#6fb98c;font-size:.7rem">DIAGNOSTIC LOG:</p>',
                    unsafe_allow_html=True)
        lines = "".join(f'<p class="l-{k}">&gt; {escape(m)}</p>' for k, m in reversed(S.logs[-30:]))
        st.markdown(f'<div class="logbox">{lines}</div>', unsafe_allow_html=True)
