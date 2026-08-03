import json
import math
import os
import argparse
from typing import Dict, Any


class CADEvaluator:
    """
    Evaluates predicted CAD/STEP metadata against Ground Truth.
    Calculates Absolute Error, Relative Error (%), Euclidean Distance for Position,
    and Overall Accuracy Score.
    """

    def __init__(self, gt_path: str, pred_path: str):
        self.gt_data = self._load_json(gt_path)
        self.pred_data = self._load_json(pred_path)

    def _load_json(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def calculate_relative_error(gt_val: float, pred_val: float) -> float:
        """Calculates Relative Error percentage."""
        if gt_val == 0:
            return 0.0 if pred_val == 0 else 100.0
        return abs((pred_val - gt_val) / gt_val) * 100.0

    @staticmethod
    def calculate_euclidean_distance(pt1: list, pt2: list) -> float:
        """Calculates Euclidean distance between two 3D points."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(pt1, pt2)))

    def evaluate_geometry(() -> Dict[str, Any]:
        """Evaluates Volume, Surface Area, Bounding Box, and Center of Mass."""
        gt_cad = self.gt_data.get("cad_kernel_geometry", {})
        pred_cad = self.pred_data.get("cad_kernel_geometry", {})

        metrics = {}

        # 1. Volume Evaluation
        gt_vol = gt_cad.get("volume", 0.0)
        pred_vol = pred_cad.get("volume", 0.0)
        vol_err = self.calculate_relative_error(gt_vol, pred_vol)
        metrics["volume"] = {
            "ground_truth": gt_vol,
            "predicted": pred_vol,
            "abs_error": abs(pred_vol - gt_vol),
            "relative_error_pct": round(vol_err, 4),
            "accuracy_pct": round(max(0.0, 100.0 - vol_err), 4)
        }

        # 2. Surface Area Evaluation
        gt_area = gt_cad.get("surface_area", 0.0)
        pred_area = pred_cad.get("surface_area", 0.0)
        area_err = self.calculate_relative_error(gt_area, pred_area)
        metrics["surface_area"] = {
            "ground_truth": gt_area,
            "predicted": pred_area,
            "abs_error": abs(pred_area - gt_area),
            "relative_error_pct": round(area_err, 4),
            "accuracy_pct": round(max(0.0, 100.0 - area_err), 4)
        }

        # 3. Center of Mass Evaluation
        gt_com = gt_cad.get("center_of_mass", [0.0, 0.0, 0.0])
        pred_com = pred_cad.get("center_of_mass", [0.0, 0.0, 0.0])
        com_dist = self.calculate_euclidean_distance(gt_com, pred_com)
        metrics["center_of_mass"] = {
            "ground_truth": gt_com,
            "predicted": pred_com,
            "euclidean_distance_error": round(com_dist, 6)
        }

        # 4. Bounding Box Dimensions Evaluation (dx, dy, dz)
        gt_bbox = gt_cad.get("exact_bbox", {})
        pred_bbox = pred_cad.get("exact_bbox", {})
        bbox_metrics = {}
        bbox_accs = []

        for dim in ["dx", "dy", "dz"]:
            g_d = gt_bbox.get(dim, 0.0)
            p_d = pred_bbox.get(dim, 0.0)
            d_err = self.calculate_relative_error(g_d, p_d)
            acc = max(0.0, 100.0 - d_err)
            bbox_accs.append(acc)
            bbox_metrics[dim] = {
                "ground_truth": g_d,
                "predicted": p_d,
                "relative_error_pct": round(d_err, 4)
            }
        
        metrics["bounding_box"] = bbox_metrics
        metrics["bounding_box_avg_accuracy_pct"] = round(sum(bbox_accs) / len(bbox_accs), 4) if bbox_accs else 0.0

        return metrics

    def evaluate_topology(self) -> Dict[str, Any]:
        """Evaluates Topology counts (Faces, Edges, Vertices)."""
        gt_topo = self.gt_data.get("cad_kernel_geometry", {}).get("topology_counts", {})
        pred_topo = self.pred_data.get("cad_kernel_geometry", {}).get("topology_counts", {})

        topo_metrics = {}
        accuracies = []

        for key in ["faces", "edges", "vertices", "solids"]:
            g_val = gt_topo.get(key, 0)
            p_val = pred_topo.get(key, 0)
            err = self.calculate_relative_error(g_val, p_val)
            acc = max(0.0, 100.0 - err)
            accuracies.append(acc)

            topo_metrics[key] = {
                "ground_truth": g_val,
                "predicted": p_val,
                "exact_match": g_val == p_val,
                "accuracy_pct": round(acc, 4)
            }

        topo_metrics["avg_topology_accuracy_pct"] = round(sum(accuracies) / len(accuracies), 4) if accuracies else 0.0
        return topo_metrics

    def run_evaluation(self) -> Dict[str, Any]:
        """Runs full evaluation and calculates overall score."""
        geom_results = self.evaluate_geometry()
        topo_results = self.evaluate_topology()

        # Overall composite score (Weighted average)
        vol_acc = geom_results["volume"]["accuracy_pct"]
        area_acc = geom_results["surface_area"]["accuracy_pct"]
        bbox_acc = geom_results["bounding_box_avg_accuracy_pct"]
        topo_acc = topo_results["avg_topology_accuracy_pct"]

        overall_score = (vol_acc * 0.3) + (area_acc * 0.3) + (bbox_acc * 0.2) + (topo_acc * 0.2)

        report = {
            "overall_similarity_score_pct": round(overall_score, 2),
            "geometry_evaluation": geom_results,
            "topology_evaluation": topo_results
        }
        return report


def main():
    parser = argparse.ArgumentParser(description="Evaluate CAD Predictions against Ground Truth.")
    parser.add_argument("--gt", "-g", required=True, help="Path to ground_truth.json")
    parser.add_argument("--pred", "-p", required=True, help="Path to predictions.json")
    parser.add_argument("--output", "-o", default="evaluation_report.json", help="Path to save evaluation report")

    args = parser.parse_args()

    evaluator = CADEvaluator(args.gt, args.pred)
    report = evaluator.run_evaluation()

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\n" + "="*50)
    print(f" EVALUATION REPORT COMPLETED")
    print("="*50)
    print(f" Overall Similarity Score: {report['overall_similarity_score_pct']}%")
    print(f" Volume Accuracy:           {report['geometry_evaluation']['volume']['accuracy_pct']}%")
    print(f" Surface Area Accuracy:     {report['geometry_evaluation']['surface_area']['accuracy_pct']}%")
    print(f" Bounding Box Avg Accuracy: {report['geometry_evaluation']['bounding_box_avg_accuracy_pct']}%")
    print(f" Topology Avg Accuracy:     {report['topology_evaluation']['avg_topology_accuracy_pct']}%")
    print("="*50)
    print(f" Detailed report saved to: {args.output}\n")


if __name__ == "__main__":
    main()