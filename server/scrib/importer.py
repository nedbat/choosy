import yaml

from scrib.models import Page
from desk.models import Exercise

# A map from slug field names to models
slug_map = {
    'page': Page,
    'exercise': Exercise,
}

def import_yaml(yaml_file, user):
    """Import a multi-model YAML file."""
    data = yaml.safe_load_all(yaml_file)
    for d in data:
        for slug_name in slug_map:
            if slug_name in d:
                class_ = slug_map[slug_name]
                d['slug'] = d[slug_name]
                new_thing = class_.from_dict(d, user)
                break
        else:
            # Didn't find a slug name we recognized
            raise Exception("Didn't find a slug, keys are: %s" % ", ".join(d))
