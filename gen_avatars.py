"""Generate Fork Quiz archetype avatars via nano-banana-flash (Gemini 2.5 Flash Image).

Reads archetype_prompts.json, generates one PNG per archetype code to
assets/avatars/{code}.png. Runs in parallel (default 4 workers).

Usage:
    python3 gen_avatars.py                       # generate all 32
    python3 gen_avatars.py BLASD BLOSE WMOTE     # generate only specified codes
    python3 gen_avatars.py --force               # re-generate even if file exists
"""
import os
import sys
import json
import io
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

ROOT = Path(__file__).parent
PROMPTS_PATH = ROOT / "archetype_prompts.json"
OUT_DIR = ROOT / "assets" / "avatars"
MODEL = "gemini-2.5-flash-image"
WORKERS = 4

load_dotenv("/Users/lts/Desktop/Second_Brain/.env")
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def filename_for(entry: dict) -> str:
    """Convert 'The X, Y, Z, W V' → 'X_Y_Z_W_V.png' (hyphens preserved)."""
    name = entry["name"]
    if name.startswith("The "):
        name = name[4:]
    return name.replace(", ", "_").replace(" ", "_") + ".png"


def generate_one(entry: dict) -> tuple[str, bool, str]:
    code = entry["code"]
    prompt = entry["prompt"]
    out = OUT_DIR / filename_for(entry)
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
    except Exception as e:
        return (code, False, f"API error: {e}")

    for cand in resp.candidates or []:
        content = getattr(cand, "content", None)
        parts = getattr(content, "parts", None) if content else None
        for part in parts or []:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                img = Image.open(io.BytesIO(inline.data))
                img.save(out)
                return (code, True, f"{img.size[0]}x{img.size[1]} → {out.name}")
        fr = getattr(cand, "finish_reason", None)
        if fr:
            return (code, False, f"no image (finish_reason={fr})")
    return (code, False, "no image in response")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv

    with open(PROMPTS_PATH) as f:
        all_entries = json.load(f)

    if args:
        wanted = set(args)
        entries = [e for e in all_entries if e["code"] in wanted]
        missing = wanted - {e["code"] for e in entries}
        if missing:
            print(f"WARN: codes not found in prompts: {sorted(missing)}", file=sys.stderr)
    else:
        entries = all_entries

    if not force:
        entries = [e for e in entries if not (OUT_DIR / filename_for(e)).exists()]

    if not entries:
        print("nothing to generate")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"generating {len(entries)} avatars via {MODEL} (workers={WORKERS})...")

    t0 = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(generate_one, e): e["code"] for e in entries}
        for fut in as_completed(futures):
            code, ok, info = fut.result()
            marker = "OK " if ok else "FAIL"
            print(f"  {marker} {code}: {info}")
            results.append((code, ok))

    dt = time.time() - t0
    ok_count = sum(1 for _, ok in results if ok)
    print(f"\ndone: {ok_count}/{len(results)} succeeded in {dt:.1f}s")
    if ok_count < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
