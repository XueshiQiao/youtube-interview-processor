#!/usr/bin/env python3
"""
clean_and_merge_srt.py

A robust, general-purpose Python script to clean and merge YouTube auto-generated
rolling/scrolling subtitles into clean, semantic sentence-level SRT subtitles.

Features:
1. Automatically detects and discards <= 50ms player refresh / flash frames.
2. Robust dual-line sliding window deduplication for rolling subtitles as well as
   regular non-rolling multi-line subtitles.
3. Word-level character-length-weighted timestamp interpolation for high-precision
   sentence boundary timing.
4. Intelligent semantic sentence segmentation:
   - Splits on speaker markers (">>").
   - Splits on sentence-ending punctuation (., ?, !) while avoiding false positives
     from numbers (e.g. 1.2, 3.5) and common abbreviations (e.g. Mr., Dr., e.g., etc.).
   - Intelligently merges dependent clauses and conjunctions (e.g. "to help...", "because...").
   - Intelligently merges ultra-short confirmation/backchannel words (e.g. ">> Exactly. Right.", "Yeah.").
   - Enforces reasonable reading duration (> 1 second) for all subtitle blocks.
5. Canonical proper noun normalization (e.g., OpenAI, ChatGPT, YouTube, GitHub).
"""

import argparse
import os
import re
import sys
from typing import List, Optional, Tuple

# Common abbreviations that should NOT trigger a sentence split
ABBREVIATIONS = {
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "vs.", "v.",
    "e.g.", "i.e.", "etc.", "ex.", "inc.", "corp.", "co.", "ltd.",
    "u.s.", "u.k.", "u.n.", "e.u.", "a.m.", "p.m.", "am.", "pm.",
    "jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.", "sep.",
    "sept.", "oct.", "nov.", "dec.", "approx.", "al.", "st.", "ave.", "rd."
}

# Subordinating words / conjunctions that indicate dependent clauses
DEPENDENT_WORDS = {
    "to", "because", "and", "but", "or", "so", "which", "that", "where",
    "when", "while", "as", "though", "although", "since", "unless", "if"
}

# Short confirmation / backchannel words
CONFIRMATIONS = {
    "exactly.", "right.", "yeah.", "yes.", "yep.", "sure.", "cool.", "totally.",
    "okay.", "ok.", "indeed.", "absolutely.", "wow.", "multiple.", "all right.",
    "exactly", "right", "yeah", "yes", "yep", "sure", "cool", "totally",
    "okay", "ok", "indeed", "absolutely", "wow", "multiple", "all right"
}

# Canonical proper noun replacements
PROPER_NOUNS = [
    (re.compile(r"\bOpen\s*AI\b", re.I), "OpenAI"),
    (re.compile(r"\bChat\s*GPT\b", re.I), "ChatGPT"),
    (re.compile(r"\bYou\s*Tube\b", re.I), "YouTube"),
    (re.compile(r"\bGit\s*Hub\b", re.I), "GitHub"),
    (re.compile(r"\bDeep\s*Mind\b", re.I), "DeepMind"),
]


def parse_timestamp(ts: str) -> float:
    """Convert timestamp string (HH:MM:SS,mmm or HH:MM:SS.mmm) to seconds."""
    ts = ts.strip().replace(",", ".")
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return float(ts)


def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm."""
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    if s >= 60:
        m += 1
        s -= 60
    if m >= 60:
        h += 1
        m -= 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


class RawCue:
    def __init__(self, start: float, end: float, lines: List[str]):
        self.start = start
        self.end = end
        self.lines = lines


class Word:
    def __init__(self, text: str, start: float, end: float, speaker_change: bool = False):
        self.text = text
        self.start = start
        self.end = end
        self.speaker_change = speaker_change


class Segment:
    def __init__(self, has_speaker: bool, words: List[Word]):
        self.has_speaker = has_speaker
        self.words = list(words)
        self.start = self.words[0].start
        self.end = self.words[-1].end

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)

    @property
    def char_len(self) -> int:
        return len(self.text)


def parse_srt(file_path: str) -> List[RawCue]:
    """Parse SRT file using robust block matching, filtering out refresh/flash frames (<= 50ms)."""
    with open(file_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    pattern = re.compile(
        r"(?:^|\n)(\d+)\r?\n"
        r"(\d+:\d+:\d+[\.,]\d+\s*-->\s*(\d+:\d+:\d+[\.,]\d+))\r?\n"
        r"(.*?)(?=(?:\r?\n\d+\r?\n\d+:\d+:\d+[\.,]\d+\s*-->|\Z))",
        re.DOTALL
    )

    cues = []
    for m in pattern.finditer(content):
        time_str = m.group(2)
        s_str, e_str = [t.strip() for t in time_str.split("-->")]
        start = parse_timestamp(s_str)
        end = parse_timestamp(e_str)

        # Skip refresh frames (<= 50ms)
        if end - start <= 0.05:
            continue

        raw_text = m.group(4)
        text_lines = []
        for raw_line in raw_text.splitlines():
            clean_l = re.sub(r"<[^>]+>", "", raw_line).strip()
            if clean_l:
                text_lines.append(clean_l)

        if text_lines:
            cues.append(RawCue(start, end, text_lines))

    return cues


def deduplicate_sliding_window(cues: List[RawCue]) -> List[Tuple[float, float, str]]:
    """
    Extract a clean chronological sequence of unique spoken lines with timestamps.
    Handles YouTube 2-line sliding window rolling subtitles as well as regular multi-line subtitles.
    """
    extracted_lines: List[Tuple[float, float, str]] = []
    last_seen: Optional[str] = None

    for cue in cues:
        txts = cue.lines
        if len(txts) == 1:
            if txts[0] != last_seen:
                extracted_lines.append((cue.start, cue.end, txts[0]))
                last_seen = txts[0]
        elif len(txts) == 2:
            top, bottom = txts[0], txts[1]
            if top == last_seen:
                extracted_lines.append((cue.start, cue.end, bottom))
                last_seen = bottom
            elif bottom == last_seen:
                extracted_lines.append((cue.start, cue.end, top))
                last_seen = top
            else:
                # Both lines are new (standard multi-line subtitle or gap jump)
                dur = cue.end - cue.start
                w0 = max(1, len(top))
                w1 = max(1, len(bottom))
                mid = cue.start + dur * (w0 / (w0 + w1))
                extracted_lines.append((cue.start, mid, top))
                extracted_lines.append((mid, cue.end, bottom))
                last_seen = bottom
        else:
            # Multi-line (> 2 lines)
            new_lines = [l for l in txts if l != last_seen]
            if new_lines:
                dur = cue.end - cue.start
                tot = sum(max(1, len(l)) for l in new_lines)
                curr = cue.start
                for nl in new_lines:
                    chunk_dur = dur * (max(1, len(nl)) / tot)
                    extracted_lines.append((curr, curr + chunk_dur, nl))
                    curr += chunk_dur
                last_seen = new_lines[-1]

    return extracted_lines


def interpolate_words(extracted_lines: List[Tuple[float, float, str]]) -> List[Word]:
    """
    Apply word-level character-length-weighted timestamp interpolation and proper noun normalization.
    """
    all_words: List[Word] = []

    for s, e, raw_text in extracted_lines:
        text = raw_text
        for pattern, repl in PROPER_NOUNS:
            text = pattern.sub(repl, text)

        tokens = text.split()
        if not tokens:
            continue

        spk_change = False
        if tokens[0] == ">>":
            tokens = tokens[1:]
            spk_change = True
        elif tokens[0].startswith(">>"):
            tokens[0] = tokens[0][2:].strip()
            spk_change = True

        tokens = [t for t in tokens if t]
        if not tokens:
            continue

        dur = e - s
        tot_len = sum(max(1, len(t)) for t in tokens)
        curr = s
        for i, t in enumerate(tokens):
            w_dur = dur * (max(1, len(t)) / tot_len)
            w_start = curr
            w_end = s + dur if i == len(tokens) - 1 else curr + w_dur
            all_words.append(Word(t, w_start, w_end, speaker_change=(i == 0 and spk_change)))
            curr = w_end

    return all_words


def is_sentence_terminal(w: Word, next_w: Optional[Word]) -> bool:
    """
    Determine if a word is an actual sentence-ending terminal (. ? !),
    avoiding false positives from decimals and common abbreviations.
    """
    txt = w.text
    if not re.search(r"[\.\?!]$", txt):
        return False
    # Avoid decimal numbers like 1.2 or 3.5
    if re.match(r"^\$?\d+\.\d+$", txt):
        return False
    clean = re.sub(r"[^\w\.]", "", txt).lower()
    if clean in ABBREVIATIONS or re.match(r"^[a-z]\.$", clean):
        return False
    # If next word starts with lowercase AND is a dependent clause/conjunction word, suppress split
    if next_w:
        nxt_clean = re.sub(r"[^\w]", "", next_w.text).lower()
        if next_w.text[0].islower() and nxt_clean in DEPENDENT_WORDS:
            return False
    return True


def segment_into_raw_sentences(all_words: List[Word]) -> List[Segment]:
    """Segment words into candidate sentences based on speaker markers and sentence punctuation."""
    raw_sents: List[Segment] = []
    curr_words: List[Word] = []
    curr_has_speaker = False

    for i, w in enumerate(all_words):
        if w.speaker_change and curr_words:
            raw_sents.append(Segment(curr_has_speaker, curr_words))
            curr_words = []
            curr_has_speaker = True
        elif w.speaker_change:
            curr_has_speaker = True

        curr_words.append(w)
        next_w = all_words[i + 1] if i + 1 < len(all_words) else None

        if is_sentence_terminal(w, next_w):
            raw_sents.append(Segment(curr_has_speaker, curr_words))
            curr_words = []
            curr_has_speaker = False

    if curr_words:
        raw_sents.append(Segment(curr_has_speaker, curr_words))

    return raw_sents


def should_merge_segments(seg_a: Segment, seg_b: Segment, max_chars: int = 100, max_dur: float = 7.0) -> bool:
    """
    Determine whether candidate segment A and segment B should be merged.
    Never merges across speaker change (seg_b.has_speaker == True).
    """
    if seg_b.has_speaker:
        return False

    combined_len = seg_a.char_len + 1 + seg_b.char_len
    combined_dur = seg_b.end - seg_a.start

    # Rule 1: A ended without sentence terminal (e.g. comma or incomplete fragment)
    if not re.search(r"[\.\?!]$", seg_a.words[-1].text):
        return combined_len <= max_chars * 1.5 and combined_dur <= max_dur * 1.5

    # Rule 2: B starts with lowercase or dependent conjunction
    first_b = seg_b.words[0].text
    if first_b[0].islower() or first_b.lower() in DEPENDENT_WORDS:
        if combined_len <= max_chars and combined_dur <= max_dur:
            return True

    # Rule 3: Short confirmation/backchannel words
    clean_a = re.sub(r"[^\w\.]", "", seg_a.text).lower()
    is_conf_a = clean_a in CONFIRMATIONS or (len(seg_a.words) <= 2 and seg_a.duration < 1.0)
    clean_b = re.sub(r"[^\w\.]", "", seg_b.text).lower()
    is_conf_b = clean_b in CONFIRMATIONS

    # If both are short confirmations, always merge (e.g. ">> Exactly." + "Right." -> ">> Exactly. Right.")
    if is_conf_a and is_conf_b:
        return True
    if is_conf_a and combined_len <= max_chars and combined_dur <= max_dur:
        return True

    # Rule 4: Very short duration (< 1.0s or <= 3 words)
    if (seg_a.duration < 1.0 or len(seg_a.words) <= 3) and combined_len <= max_chars and combined_dur <= max_dur:
        return True
    if (seg_b.duration < 1.0 or len(seg_b.words) <= 2) and combined_len <= max_chars and combined_dur <= max_dur:
        return True

    return False


def merge_sentences(segments: List[Segment], max_chars: int = 100, max_dur: float = 7.0) -> List[Segment]:
    """Iteratively merge candidate sentences according to semantic and duration criteria."""
    merged: List[Segment] = []
    i = 0
    while i < len(segments):
        curr = segments[i]
        while i + 1 < len(segments) and should_merge_segments(curr, segments[i + 1], max_chars, max_dur):
            nxt = segments[i + 1]
            curr = Segment(curr.has_speaker, curr.words + nxt.words)
            i += 1
        merged.append(curr)
        i += 1
    return merged


def ensure_minimum_duration(segments: List[Segment], min_dur: float = 1.0, min_gap: float = 0.05) -> None:
    """
    Ensure every subtitle segment has a reasonable reading duration (> min_dur),
    by extending display end time if silent pause follows, without overlapping next subtitle.
    """
    for i in range(len(segments)):
        seg = segments[i]
        if seg.duration < min_dur:
            target_end = seg.start + min_dur
            if i + 1 < len(segments):
                max_allowed = segments[i + 1].start - min_gap
                if max_allowed > seg.start:
                    seg.end = min(target_end, max_allowed)
            else:
                seg.end = target_end


def format_srt_block(index: int, seg: Segment) -> str:
    """Format a single subtitle block for SRT output."""
    time_str = f"{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}"
    text = seg.text
    if seg.has_speaker:
        text = f">> {text}"
    return f"{index}\n{time_str}\n{text}\n"


def process_srt(input_path: str, output_path: str, min_duration: float = 1.0) -> Tuple[int, float, float]:
    """Main processing function for an SRT file."""
    # 1. Parse SRT and filter refresh frames
    raw_cues = parse_srt(input_path)
    if not raw_cues:
        raise ValueError(f"No valid subtitle cues found in {input_path}")

    # 2. Sliding window deduplication
    extracted_lines = deduplicate_sliding_window(raw_cues)

    # 3. Word interpolation & proper noun normalization
    all_words = interpolate_words(extracted_lines)
    if not all_words:
        raise ValueError("Failed to extract words from subtitle cues")

    # 4. Semantic sentence segmentation
    raw_sentences = segment_into_raw_sentences(all_words)

    # 5. Semantic merging
    merged_segments = merge_sentences(raw_sentences)

    # 6. Ensure minimum reading duration
    ensure_minimum_duration(merged_segments, min_dur=min_duration)

    # 7. Write output SRT
    with open(output_path, "w", encoding="utf-8") as out:
        for idx, seg in enumerate(merged_segments, 1):
            out.write(format_srt_block(idx, seg) + "\n")

    return len(merged_segments), merged_segments[0].start, merged_segments[-1].end


def main():
    parser = argparse.ArgumentParser(
        description="Clean and merge YouTube auto-scrolling subtitles into high-quality semantic SRT subtitles."
    )
    parser.add_argument("input_srt", help="Path to input SRT file")
    parser.add_argument("output_srt", nargs="?", default=None, help="Path to output SRT file (optional)")
    parser.add_argument(
        "--min-duration",
        type=float,
        default=1.0,
        help="Minimum display duration in seconds (default: 1.0)"
    )

    args = parser.parse_args()

    input_file = os.path.abspath(args.input_srt)
    if not os.path.isfile(input_file):
        print(f"Error: Input file does not exist: {input_file}", file=sys.stderr)
        sys.exit(1)

    if args.output_srt:
        output_file = os.path.abspath(args.output_srt)
    else:
        # Strip .en-orig.srt or .srt to produce <base>.merged.srt
        if input_file.endswith(".en-orig.srt"):
            output_file = input_file[:-len(".en-orig.srt")] + ".merged.srt"
        elif input_file.endswith(".srt"):
            output_file = input_file[:-len(".srt")] + ".merged.srt"
        else:
            output_file = input_file + ".merged.srt"

    print(f"Processing: {input_file}")
    print(f"Output:     {output_file}")

    total_segments, start_sec, end_sec = process_srt(input_file, output_file, min_duration=args.min_duration)

    print("\nProcessing completed successfully!")
    print(f"- Total segments: {total_segments}")
    print(f"- Start time:     {format_timestamp(start_sec)}")
    print(f"- End time:       {format_timestamp(end_sec)}")


if __name__ == "__main__":
    main()
