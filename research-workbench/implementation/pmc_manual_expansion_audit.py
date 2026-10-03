"""Recompute the frozen 40-article one-reviewer PMC screen."""

import json
import math
import random
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).parent


def jsonl(name):
    return [json.loads(line) for line in (ROOT / name).read_text().splitlines() if line]


def wilson(successes, total):
    z = 1.96
    p = successes / total
    d = 1 + z * z / total
    center = (p + z * z / (2 * total)) / d
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d
    return [center - radius, center + radius]


def main():
    plan = json.loads((ROOT / "pmc_manual_expansion_plan_2026-09-29.json").read_text())
    old = jsonl("pmc_xml_manual_review_2026-09-28.jsonl")
    new = jsonl("pmc_manual_expansion_labels_2026-09-29.jsonl")
    checks = {row["pmcid"]: row for row in jsonl("pmc_xml_checks_2026-09-28.jsonl")
              if row["group"] == "random"}
    assert len(checks) == 80 and len(old) == len(new) == 20
    old_ids = {row["pmcid"] for row in old}
    pool = sorted(set(checks) - old_ids)
    assert len(pool) == 60
    assert plan["selected_pmcids"] == sorted(random.Random(plan["seed"]).sample(pool, 20))
    assert sorted(row["pmcid"] for row in new) == plan["selected_pmcids"]
    assert not (old_ids & {row["pmcid"] for row in new})
    labels = old + new
    assert all(row["pmcid"] in checks for row in labels)
    confusion = Counter()
    for row in labels:
        check = checks[row["pmcid"]]
        queued = check["well_formed"] and check["jats_article"] and \
            check["article_type"] == "research-article" and check["body_words"] >= 1000
        confusion[(queued, row["strict_original_research_candidate"])] += 1
    central = sum(row["cardiovascular_relevance"] == "central" for row in labels)
    original = sum(row["strict_original_research_candidate"] for row in labels)
    summary = {"random_xml_pool": 80, "reviewed_total": 40,
               "original_random_review": 20, "new_random_review": 20,
               "central": central, "central_wilson_95": wilson(central, 40),
               "original_candidate": original,
               "original_candidate_wilson_95": wilson(original, 40),
               "structural_queue_confusion": {
                   "queued_original": confusion[(True, True)],
                   "queued_not_original": confusion[(True, False)],
                   "not_queued_original": confusion[(False, True)],
                   "not_queued_not_original": confusion[(False, False)]},
               "interpretation": "One agent qualitative screen; development estimate, not expert adjudication or training eligibility."}
    assert sum(confusion.values()) == 40
    print(json.dumps(summary, indent=2))
    (ROOT / "pmc_manual_expansion_summary_2026-09-29.json").write_text(
        json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
