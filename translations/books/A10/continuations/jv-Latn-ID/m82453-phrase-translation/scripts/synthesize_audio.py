"""Create and verify the two explicitly labelled Javanese AX-2 audio tracks.

Generation uses a genuine jv-ID voice discovered from the Edge speech voice
catalog.  It never substitutes an Indonesian or English voice.  The network
synthesis result is normalized twice from the same captured stream; byte
identity of the two normalizations is required before an artifact is admitted.
Ordinary packet rebuilds do not contact the service and preserve the admitted
audio bytes.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
TRACKS = {
    "jv-academic": {"voice": "jv-ID-DimasNeural", "rate": "-8%"},
    "jv-conversation": {"voice": "jv-ID-SitiNeural", "rate": "-3%"},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ffprobe(path: Path) -> dict:
    command = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate,channels,bit_rate:format=duration",
        "-of", "json", str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    data = json.loads(result.stdout)
    stream = data["streams"][0]
    return {
        "codec": stream["codec_name"],
        "sample_rate_hz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "bit_rate_bps": int(stream.get("bit_rate") or 0),
        "duration_seconds": round(float(data["format"]["duration"]), 3),
    }


def narration_text(track: str) -> tuple[str, str]:
    path = ROOT / "narration" / f"{track}.ssml"
    root = E.parse(str(path)).getroot()
    language = root.get("{http://www.w3.org/XML/1998/namespace}lang")
    if language != "jv-Latn-ID":
        raise ValueError(f"{track} SSML is not Javanese: {language!r}")
    paragraphs = [" ".join((node.text or "").split()) for node in root.findall("p")]
    if len(paragraphs) != 23 or any(not paragraph for paragraph in paragraphs):
        raise ValueError(f"{track} must have 23 nonempty source-positioned paragraphs")
    return "\n\n".join(paragraphs), sha256(path)


def normalize(raw: Path, destination: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(raw), "-map_metadata", "-1", "-vn", "-ac", "1",
            "-ar", "24000", "-c:a", "libmp3lame", "-b:a", "64k",
            "-write_xing", "0", "-fflags", "+bitexact", "-flags:a", "+bitexact",
            str(destination),
        ],
        check=True,
    )


async def generate() -> None:
    import edge_tts

    catalog = await edge_tts.list_voices()
    by_name = {item["ShortName"]: item for item in catalog}
    for settings in TRACKS.values():
        voice = settings["voice"]
        if voice not in by_name or by_name[voice].get("Locale") != "jv-ID":
            raise RuntimeError(f"Required genuine Javanese voice unavailable: {voice}")

    audio_dir = ROOT / "audio"
    temp_dir = ROOT / "tmp" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    records: dict[str, dict] = {}
    try:
        for track, settings in TRACKS.items():
            text, ssml_hash = narration_text(track)
            raw = temp_dir / f"{track}.service.mp3"
            normalized_a = temp_dir / f"{track}.normalized-a.mp3"
            normalized_b = temp_dir / f"{track}.normalized-b.mp3"
            communicate = edge_tts.Communicate(
                text,
                settings["voice"],
                rate=settings["rate"],
                volume="+0%",
                pitch="+0Hz",
            )
            await communicate.save(str(raw))
            normalize(raw, normalized_a)
            normalize(raw, normalized_b)
            if normalized_a.read_bytes() != normalized_b.read_bytes():
                raise RuntimeError(f"Non-deterministic normalization for {track}")
            destination = audio_dir / f"{track}.mp3"
            normalized_a.replace(destination)
            probe = ffprobe(destination)
            if probe["codec"] != "mp3" or probe["channels"] != 1 or probe["sample_rate_hz"] != 24000:
                raise RuntimeError(f"Unexpected normalized audio format for {track}: {probe}")
            if probe["duration_seconds"] < 60:
                raise RuntimeError(f"Implausibly short complete-section audio for {track}: {probe}")
            voice_info = by_name[settings["voice"]]
            records[track] = {
                "file": destination.relative_to(ROOT).as_posix(),
                "sha256": sha256(destination),
                "bytes": destination.stat().st_size,
                **probe,
                "voice": settings["voice"],
                "voice_locale": voice_info["Locale"],
                "voice_gender": voice_info.get("Gender"),
                "rate": settings["rate"],
                "volume": "+0%",
                "pitch": "+0Hz",
                "narration_ssml_sha256": ssml_hash,
                "spoken_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "normalization_replay": "two independent ffmpeg normalizations of the captured service stream were byte-identical",
            }
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    version = importlib.metadata.version("edge-tts")
    ffmpeg_line = subprocess.run(
        ["ffmpeg", "-version"], check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout.splitlines()[0]
    metadata = {
        "schema": "a10.synthetic-audio.v1",
        "locale": "jv-Latn-ID",
        "scope": "m82453/fs-id1170654942537",
        "generated_date": "2026-09-04",
        "status": "actual synthetic Javanese audio supplied for both Javanese tracks",
        "human_recording": False,
        "human_pronunciation_certification": False,
        "disclaimer": "These files are synthetic Javanese speech, not human recordings. Pronunciation and dialect suitability remain provisional; neither Indonesian nor English audio was used as a fallback.",
        "synthesis": {
            "client": f"edge-tts {version}",
            "catalog_check": "live catalog returned both requested voices with Locale jv-ID",
            "service_regeneration_byte_stability": "not claimed; admitted normalized bytes are pinned by SHA-256",
            "normalizer": ffmpeg_line,
            "output_profile": "MP3, mono, 24000 Hz, nominal 64 kbit/s, metadata stripped",
        },
        "tracks": records,
    }
    (audio_dir / "AUDIO.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Synthetic Javanese audio",
        "",
        "These are actual synthetic Javanese speech files, not human recordings. No Indonesian or English voice was substituted. Pronunciation and dialect suitability remain provisional and have not been human-certified.",
        "",
        "| Track | Voice | Duration | Bytes | SHA-256 |",
        "|---|---|---:|---:|---|",
    ]
    for track, record in records.items():
        lines.append(
            f"| `{track}` | `{record['voice']}` (`{record['voice_locale']}`) | {record['duration_seconds']:.3f} s | {record['bytes']} | `{record['sha256']}` |"
        )
    lines += [
        "",
        "`AUDIO.json` binds each MP3 to its source-positioned SSML and spoken-text hashes and records the deterministic normalization replay. Routine offline rebuilds preserve these admitted bytes and do not contact the synthesis service.",
        "",
    ]
    (audio_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def verify() -> None:
    path = ROOT / "audio" / "AUDIO.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    if metadata.get("locale") != "jv-Latn-ID" or metadata.get("human_recording") is not False:
        raise RuntimeError("Audio labeling is missing or false")
    for track, expected in TRACKS.items():
        record = metadata["tracks"][track]
        if record["voice"] != expected["voice"] or record["voice_locale"] != "jv-ID":
            raise RuntimeError(f"Non-Javanese or unexpected voice recorded for {track}")
        artifact = ROOT / record["file"]
        if sha256(artifact) != record["sha256"] or artifact.stat().st_size != record["bytes"]:
            raise RuntimeError(f"Audio hash/size mismatch for {track}")
        actual_probe = ffprobe(artifact)
        for key in ["codec", "sample_rate_hz", "channels", "duration_seconds"]:
            if actual_probe[key] != record[key]:
                raise RuntimeError(f"Audio probe mismatch for {track}: {key}")
        _, ssml_hash = narration_text(track)
        if ssml_hash != record["narration_ssml_sha256"]:
            raise RuntimeError(f"Narration SSML changed after synthesis for {track}")
    print("Verified two genuine jv-ID synthetic tracks, hashes, formats, durations, and SSML bindings.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", help="contact Edge speech service and replace admitted audio")
    parser.add_argument("--verify", action="store_true", help="verify existing admitted audio without network access")
    args = parser.parse_args()
    if args.generate == args.verify:
        parser.error("choose exactly one of --generate or --verify")
    if args.generate:
        asyncio.run(generate())
    else:
        verify()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    sys.dont_write_bytecode = True
    main()
