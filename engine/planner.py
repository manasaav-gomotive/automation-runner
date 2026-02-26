def plan_execution(suite, config):
    """
    Future:
    - sharding
    - parallel distribution
    - retry grouping
    """
    return {
        "suite": suite,
        "parallelism": config.get("parallelism", 1)
    }