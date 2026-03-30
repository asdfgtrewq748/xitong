#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import re
from pathlib import Path
import xml.etree.ElementTree as ET


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

NS = {"svg": SVG_NS}
URL_REF_RE = re.compile(r"^url\(#([^)]+)\)$")
CLASS_RULE_RE = re.compile(r"\.([A-Za-z0-9_-]+)\s*\{([^}]*)\}", re.S)


def svg_tag(local: str) -> str:
    return f"{{{SVG_NS}}}{local}"


def parse_style_declarations(style_text: str) -> dict[str, str]:
    declarations: dict[str, str] = {}
    for chunk in style_text.split(";"):
        if ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key and value:
            declarations[key] = value
    return declarations


def extract_class_rules(root: ET.Element) -> dict[str, dict[str, str]]:
    rules: dict[str, dict[str, str]] = {}
    for style in root.findall(".//svg:style", NS):
        text = style.text or ""
        for class_name, body in CLASS_RULE_RE.findall(text):
            rules[class_name] = parse_style_declarations(body)
    return rules


def inline_class_styles(root: ET.Element) -> int:
    class_rules = extract_class_rules(root)
    changed = 0
    if not class_rules:
        return changed

    for elem in root.iter():
        class_attr = elem.attrib.get("class")
        if not class_attr:
            continue

        merged: dict[str, str] = {}
        for class_name in class_attr.split():
            merged.update(class_rules.get(class_name, {}))

        for attr_name, attr_value in merged.items():
            if attr_name not in elem.attrib:
                elem.set(attr_name, attr_value)
                changed += 1
        del elem.attrib["class"]
        changed += 1

    for parent in root.iter():
        for child in list(parent):
            if child.tag == svg_tag("style"):
                parent.remove(child)
                changed += 1

    return changed


def first_simple_color(node: ET.Element) -> str | None:
    preferred = []
    fallback = []
    for elem in node.iter():
        fill = elem.attrib.get("fill")
        if fill and fill != "none" and not fill.startswith("url(#"):
            preferred.append(fill)
        stroke = elem.attrib.get("stroke")
        if stroke and stroke != "none" and not stroke.startswith("url(#"):
            fallback.append(stroke)
    if preferred:
        return preferred[0]
    if fallback:
        return fallback[0]
    return None


def collect_defs(root: ET.Element, flatten_gradients: bool) -> tuple[dict[str, str], set[str], set[str], set[str]]:
    pattern_colors: dict[str, str] = {}
    filter_ids: set[str] = set()
    marker_ids: set[str] = set()
    gradient_ids: set[str] = set()

    for defs in root.findall(".//svg:defs", NS):
        for child in list(defs):
            elem_id = child.attrib.get("id")
            if child.tag == svg_tag("pattern") and elem_id:
                color = first_simple_color(child)
                if color:
                    pattern_colors[elem_id] = color
            elif child.tag == svg_tag("filter") and elem_id:
                filter_ids.add(elem_id)
            elif child.tag == svg_tag("marker") and elem_id:
                marker_ids.add(elem_id)
            elif flatten_gradients and child.tag in {svg_tag("linearGradient"), svg_tag("radialGradient")} and elem_id:
                color = None
                stops = child.findall(".//svg:stop", NS)
                if stops:
                    middle = stops[len(stops) // 2]
                    color = middle.attrib.get("stop-color")
                if color:
                    pattern_colors[elem_id] = color
                    gradient_ids.add(elem_id)

    return pattern_colors, filter_ids, marker_ids, gradient_ids


def simplify_references(
    root: ET.Element,
    pattern_colors: dict[str, str],
    filter_ids: set[str],
    flatten_gradients: bool,
) -> int:
    changed = 0
    ref_attrs = ("fill", "stroke")

    for elem in root.iter():
        if "filter" in elem.attrib:
            match = URL_REF_RE.match(elem.attrib["filter"].strip())
            if not match or match.group(1) in filter_ids:
                del elem.attrib["filter"]
                changed += 1

        for marker_attr in ("marker-start", "marker-mid", "marker-end"):
            if marker_attr in elem.attrib:
                del elem.attrib[marker_attr]
                changed += 1

        for attr in ref_attrs:
            ref = elem.attrib.get(attr)
            if not ref:
                continue
            match = URL_REF_RE.match(ref.strip())
            if not match:
                continue
            ref_id = match.group(1)
            if ref_id in pattern_colors:
                elem.set(attr, pattern_colors[ref_id])
                changed += 1

        if flatten_gradients:
            style_attr = elem.attrib.get("style")
            if style_attr and "url(#" in style_attr:
                pieces = []
                style_changed = False
                for part in style_attr.split(";"):
                    if ":" not in part:
                        if part.strip():
                            pieces.append(part.strip())
                        continue
                    key, value = part.split(":", 1)
                    value = value.strip()
                    match = URL_REF_RE.match(value)
                    if match and match.group(1) in pattern_colors:
                        value = pattern_colors[match.group(1)]
                        style_changed = True
                    pieces.append(f"{key.strip()}:{value}")
                if style_changed:
                    elem.set("style", "; ".join(pieces))
                    changed += 1

    return changed


def strip_defs(root: ET.Element, flatten_gradients: bool) -> int:
    changed = 0
    removable = {svg_tag("filter"), svg_tag("marker"), svg_tag("pattern")}
    if flatten_gradients:
        removable.update({svg_tag("linearGradient"), svg_tag("radialGradient")})

    for defs in root.findall(".//svg:defs", NS):
        for child in list(defs):
            if child.tag in removable:
                defs.remove(child)
                changed += 1
    return changed


def sanitize_svg_text(text: str, flatten_gradients: bool) -> tuple[str, dict[str, int]]:
    root = ET.fromstring(text)
    stats = {
        "inlined_styles": 0,
        "simplified_refs": 0,
        "stripped_defs": 0,
    }

    stats["inlined_styles"] = inline_class_styles(root)
    pattern_colors, filter_ids, _marker_ids, gradient_ids = collect_defs(root, flatten_gradients)
    if gradient_ids:
        # Gradients share the same replacement map as patterns when flattening.
        pattern_colors = dict(pattern_colors)
    stats["simplified_refs"] = simplify_references(root, pattern_colors, filter_ids, flatten_gradients)
    stats["stripped_defs"] = strip_defs(root, flatten_gradients)

    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return xml_bytes.decode("utf-8"), stats


def process_file(src: Path, dst: Path, flatten_gradients: bool) -> dict[str, int]:
    text = src.read_text(encoding="utf-8")
    sanitized, stats = sanitize_svg_text(text, flatten_gradients=flatten_gradients)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(sanitized, encoding="utf-8", newline="\n")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate PowerPoint-friendly SVG copies.")
    parser.add_argument("inputs", nargs="+", help="SVG files or directories")
    parser.add_argument("--output-dir", required=True, help="Directory for sanitized SVG copies")
    parser.add_argument(
        "--flatten-gradients",
        action="store_true",
        help="Replace gradient references with a midpoint solid color for maximum compatibility.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    inputs: list[Path] = []
    for raw in args.inputs:
        path = Path(raw)
        if path.is_dir():
            inputs.extend(sorted(path.glob("*.svg")))
        else:
            inputs.append(path)

    if not inputs:
        raise SystemExit("No SVG inputs found.")

    for src in inputs:
        dst = output_dir / src.name.replace(".svg", "_ppt_safe.svg")
        stats = process_file(src, dst, flatten_gradients=args.flatten_gradients)
        print(
            f"{src.name} -> {dst.name} | "
            f"inlined={stats['inlined_styles']} simplified={stats['simplified_refs']} stripped={stats['stripped_defs']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
