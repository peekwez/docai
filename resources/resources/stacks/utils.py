def get_stage(**kwargs):
    return "prod" if kwargs.get("prod") else "dev"
