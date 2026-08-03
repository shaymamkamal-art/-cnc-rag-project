import os
import re
import json
import argparse
from typing import Dict, Any, List, Tuple

try:
    from CadQuery import importers
    import cadquery as cq
    CADQUERY_AVAILABLE = True
except ImportError:
    CADQUERY_AVAILABLE = False


class STEPGroundTruthExtractor:
    """
    Class to extract precise Ground Truth metadata, topology, and geometry
    from STEP (ISO-10303-21) CAD files.
    """

    def __init__(self, step_file_path: str):
        self.step_file_path = step_file_path
        if not os.path.exists(step_file_path):
            raise FileNotFoundError(f"File not found: {step_file_path}")

    def parse_raw_entities(self) -> Dict[str, Any]:
        """
        Parses raw entity types and calculates point-cloud bounding box 
        directly from the STEP ASCII structure.
        """
        entity_counts: Dict[str, int] = {}
        points: List[Tuple[float, float, float]] = []

        with open(self.step_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Extract entity types
        entities = re.findall(r'#\d+\s*=\s*([A-Z0-9_]+)\b', content)
        for entity in entities:
            entity_counts[entity] = entity_counts.get(entity, 0) + 1

        # Extract CARTESIAN_POINT coordinates
        pt_matches = re.findall(
            r'CARTESIAN_POINT\s*\(\s*\'[^\']*\'\s*,\s*\(\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*,\s*([-\d.E+]+)\s*\)\s*\)',
            content
        )

        for x, y, z in pt_matches:
            try:
                points.append((float(x), float(y), float(z)))
            except ValueError:
                continue

        bbox = {}
        if points:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            zs = [p[2] for p in points]
            bbox = {
                "x_min": min(xs), "x_max": max(xs),
                "y_min": min(ys), "y_max": max(ys),
                "z_min": min(zs), "z_max": max(zs),
                "dx": max(xs) - min(xs),
                "dy": max(ys) - min(ys),
                "dz": max(zs) - min(zs)
            }

        return {
            "entity_counts": entity_counts,
            "raw_cartesian_points_count": len(points),
            "point_cloud_bbox": bbox
        }

    def extract_analytical_geometry(self) -> Dict[str, Any]:
        """
        Extracts exact CAD solid properties (Volume, Surface Area, Bounding Box, Center of Mass)
        using CadQuery / OpenCASCADE kernel if installed.
        """
        if not CADQUERY_AVAILABLE:
            return {
                "warning": "CadQuery/OpenCASCADE is not installed. Skipping exact B-Rep calculations."
            }

        model = importers.importStep(self.step_file_path)
        val = model.val()

        bbox = val.BoundingBox()
        center = val.Center()

        return {
            "volume": val.Volume(),
            "surface_area": val.Area(),
            "center_of_mass": [center.x, center.y, center.z],
            "exact_bbox": {
                "x_min": bbox.xmin, "x_max": bbox.xmax,
                "y_min": bbox.ymin, "y_max": bbox.ymax,
                "z_min": bbox.zmin, "z_max": bbox.zmax,
                "dx": bbox.xlen, "dy": bbox.ylen, "dz": bbox.zlen
            },
            "topology_counts": {
                "faces": len(model.faces().vals()),
                "edges": len(model.edges().vals()),
                "vertices": len(model.vertices().vals()),
                "solids": len(model.solids().vals())
            }
        }

    def generate_ground_truth(self) -> Dict[str, Any]:
        """
        Generates full Ground Truth report.
        """
        raw_info = self.parse_raw_entities()
        analytical_info = self.extract_analytical_geometry()

        ground_truth = {
            "file_name": os.path.basename(self.step_file_path),
            "raw_parser_metadata": raw_info,
            "cad_kernel_geometry": analytical_info
        }
        return ground_truth


def main():
    parser = argparse.ArgumentParser(description="Extract Ground Truth from STEP CAD files.")
    parser.add_argument("--input", "-i", required=True, help="Path to input .step/.stp file")
    parser.add_argument("--output", "-o", default="ground_truth.json", help="Path to save JSON output")

    args = parser.parse_args()

    extractor = STEPGroundTruthExtractor(args.input)
    gt_data = extractor.generate_ground_truth()

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(gt_data, f, indent=4, ensure_ascii=False)

    print(f"Ground Truth extracted successfully -> {args.output}")


if __name__ == "__main__":
    main()