from functools import lru_cache

from aurion_claim_workflow.workflow import build_workflow


@lru_cache(maxsize=1)
def get_workflow():
    return build_workflow()
