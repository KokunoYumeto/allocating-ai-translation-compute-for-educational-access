from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "PAPER.md"


def main() -> None:
    text = PAPER.read_text(encoding="utf-8")
    before = {"en_dash": text.count("\u2013"), "em_dash": text.count("\u2014")}
    text = text.replace("\u2013", "-").replace("\u2014", " - ")
    PAPER.write_text(text, encoding="utf-8", newline="\n")
    after = {"en_dash": text.count("\u2013"), "em_dash": text.count("\u2014")}
    print({"before": before, "after": after, "path": str(PAPER)})


if __name__ == "__main__":
    main()
