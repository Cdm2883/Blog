import re
from mkdocs.plugins import event_priority

@event_priority(100)
def on_env(env, config, files, **kwargs):
    def add_spaces_to_str(pangu_str):
        if not isinstance(pangu_str, str):
            return pangu_str

        pangu_str = re.sub(r'(\d+)([\u4e00-\u9fa5])', r'\1 \2', pangu_str)
        pangu_str = re.sub(r'([\u4e00-\u9fa5])(\d+)', r'\1 \2', pangu_str)
        return pangu_str

    env.filters['str_pangu'] = add_spaces_to_str
    return env
