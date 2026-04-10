from __future__ import annotations

from collections import defaultdict
from typing import Any

from .scorer import score_expected, weighted_score
from .test_cases import TEST_CASES


def run_benchmark(systems: dict[str, Any], chat_fn) -> dict[str, Any]:
    report = {"systems": []}
    for system_name in systems:
        systems[system_name].clear()
        dimension_scores: dict[str, list[float]] = defaultdict(list)
        case_results = []
        for index, case in enumerate(TEST_CASES):
            session_id = f"benchmark-{system_name}-{index}"
            systems[system_name].clear(session_id)
            last_reply = ""
            for turn in case["turns"]:
                response = chat_fn(system_name, session_id, turn)
                last_reply = response["reply"]
            result = score_expected(last_reply, case["expect"])
            dimension_scores[case["dimension"]].append(result["ratio"])
            case_results.append(
                {
                    "name": case["name"],
                    "dimension": case["dimension"],
                    "reply": last_reply,
                    **result,
                }
            )
        averaged = {key: round(sum(values) / len(values), 4) for key, values in dimension_scores.items()}
        report["systems"].append(
            {
                "system": system_name,
                "dimensions": averaged,
                "weighted_score": weighted_score(averaged),
                "cases": case_results,
            }
        )
    return report
