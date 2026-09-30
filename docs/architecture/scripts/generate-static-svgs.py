#!/usr/bin/env python3
"""Generate dependency-free SVG renderings for the architecture diagrams.

The authoritative diagrams are the Mermaid blocks in diagrams/*.md. This script
keeps checked-in SVG previews available in environments where Mermaid CLI cannot
be installed from npm.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = ROOT / "diagrams"


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int
    style: str
    lines: tuple[str, ...]


def svg_header(width: int, height: int, title: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">Static SVG preview generated from the repository architecture diagram definitions.</desc>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#394150" />
    </marker>
    <style>
      .title {{ font: 700 22px Arial, sans-serif; fill: #172033; }}
      .box {{ rx: 12; ry: 12; stroke-width: 1.7; }}
      .protocol {{ fill: #e8f1ff; stroke: #2f6fed; }}
      .runtime {{ fill: #edf8f0; stroke: #2c8a4a; }}
      .archive {{ fill: #fff7e6; stroke: #d99000; }}
      .external {{ fill: #fff0f0; stroke: #d64545; }}
      .label {{ font: 700 15px Arial, sans-serif; fill: #172033; }}
      .small {{ font: 12px Arial, sans-serif; fill: #394150; }}
      .edge {{ stroke: #394150; stroke-width: 1.6; fill: none; marker-end: url(#arrow); }}
      .dash {{ stroke-dasharray: 6 5; }}
    </style>
  </defs>
'''


def text_block(x: float, y: float, lines: tuple[str, ...], anchor: str = "middle") -> str:
    output: list[str] = []
    for index, line in enumerate(lines):
        css_class = "label" if index == 0 else "small"
        output.append(
            f'  <text x="{x}" y="{y + index * 18}" text-anchor="{anchor}" class="{css_class}">{escape(line)}</text>'
        )
    return "\n".join(output) + "\n"


def box(item: Box) -> str:
    center_x = item.x + item.width / 2
    return (
        f'  <rect x="{item.x}" y="{item.y}" width="{item.width}" height="{item.height}" class="box {item.style}" />\n'
        + text_block(center_x, item.y + 28, item.lines)
    )


def arrow(x1: float, y1: float, x2: float, y2: float, label: str | None = None, dashed: bool = False) -> str:
    css_class = "edge dash" if dashed else "edge"
    output = f'  <path d="M {x1} {y1} L {x2} {y2}" class="{css_class}" />\n'
    if label:
        label_x = x1 + 14 if x1 == x2 else (x1 + x2) / 2
        anchor = "start" if x1 == x2 else "middle"
        output += f'  <text x="{label_x}" y="{(y1 + y2) / 2 - 8}" text-anchor="{anchor}" class="small">{escape(label)}</text>\n'
    return output


def write_svg(name: str, content: str) -> None:
    (DIAGRAM_DIR / name).write_text(content + "</svg>\n", encoding="utf-8")


# Positions are layout only. All labels and relationships come from Mermaid.
LAYOUTS = {
    "protocol-stack": {"App": (1, 0), "Local": (0, 1), "HTTP": (2, 1), "Event": (1, 2), "Verifier": (1, 3)},
    "execution-path": {"Request": (1, 0), "Policy": (1, 1), "Tool": (0, 2), "Record": (1, 3), "Archive": (1, 4), "Replay": (1, 5)},
    "delegation-lineage": {"Parent": (1, 0), "D": (1, 1), "Policy": (0, 2), "Tool": (0, 3), "Evidence": (1, 4)},
    "replay-verification": {"Archive": (1, 0), "Core": (0, 1), "Result": (0, 2), "Extra": (2, 1), "Report": (1, 3)},
    "trust-boundary": {"Caller": (1, 0), "App": (1, 1), "Signer": (0, 2), "Tool": (2, 2), "Archive": (1, 3), "Verifier": (1, 4)},
}


def generate(name, positions):
    import re
    import textwrap
    source = (DIAGRAM_DIR / f"{name}.md").read_text()
    nodes = dict(re.findall(r'^    (\w+)\["([^"\n]+)"\]$', source, re.M))
    edges = re.findall(r'^    (\w+) -->\|([^|]+)\| (\w+)$', source, re.M)
    assert nodes.keys() == positions.keys(), "Every Mermaid node needs a layout position"
    title = source.splitlines()[0].removeprefix("# ")
    width, height = 1040, 210 + 155 * max(row for _, row in positions.values())
    content = svg_header(width, height, title)
    content += f'<rect width="{width}" height="{height}" fill="white" />\n'
    content += f'<text x="520" y="35" text-anchor="middle" class="title">{escape(title)}</text>\n'
    boxes = {key: Box(45 + col * 340, 75 + row * 155, 270, 78, "protocol",
                     tuple(textwrap.wrap(label, width=28))) for key, label in nodes.items()
             for col, row in [positions[key]]}
    for a, label, b in edges:
        first, second = boxes[a], boxes[b]
        # Same-column long links route around intervening nodes.
        x1, y1 = first.x + first.width / 2, first.y + first.height
        x2, y2 = second.x + second.width / 2, second.y
        if positions[b][1] - positions[a][1] > 1:
            left = positions[a][0] < positions[b][0]
            route_x = first.x - 25 if left else first.x + first.width + 32
            start_x = first.x if left else first.x + first.width
            end_x = second.x if left else second.x + second.width
            content += f'<path d="M {start_x} {first.y + 39} L {route_x} {first.y + 39} L {route_x} {second.y + 39} L {end_x} {second.y + 39}" class="edge" />\n'
            label_x = (route_x + end_x) / 2
            anchor = "middle"
            label_y = second.y + 29
            if abs(route_x - end_x) < 120:
                label_x = route_x + 8
                anchor = "start"
                label_y = (first.y + second.y) / 2 + 39
            content += f'<text x="{label_x}" y="{label_y}" text-anchor="{anchor}" class="small">{escape(label)}</text>\n'
        else:
            content += arrow(x1, y1, x2, y2, label)
    for item in boxes.values():
        content += box(item)
    content += f'<text x="520" y="{height - 16}" text-anchor="middle" class="small">Explanatory architecture; verification claims depend on implemented scope and trusted evidence.</text>\n'
    write_svg(f"{name}.svg", content)


def main():
    for name, positions in LAYOUTS.items():
        generate(name, positions)


if __name__ == "__main__":
    main()
