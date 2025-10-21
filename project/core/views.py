from django.apps import apps
from django.http import JsonResponse


def get_relationship_type(field):
    """
    Returns the type of relationship a field has.
    - OneToOne
    - OneToMany
    - ManyToMany
    """
    relationship_type = None
    if getattr(field, "one_to_one", False):
        relationship_type = "one_to_one"
    elif getattr(field, "one_to_many", False):
        relationship_type = "one_to_many"
    elif getattr(field, "many_to_many", False):
        relationship_type = "many_to_many"
    return relationship_type


def get_models_info():
    """
    Returns detailed metadata about all models in the 'core' app:
    - Table names
    - Field names and types
    - Relationship details (OneToOne, OneToMany, ManyToMany)
    - For ForeignKey: local column, referenced column, and related table
    - For ManyToMany: through table and join fields
    """
    models_info = {}

    for model in apps.get_models():
        if model._meta.app_label in ["core"]:
            model_name = model.__name__
            model_info = {
                "table": model._meta.db_table,
                "fields": []
            }

            for field in model._meta.get_fields():
                field_info = {
                    "name": field.name,
                    "type": field.get_internal_type(),
                    "is_relation": field.is_relation,
                    "related_model": None,
                    "related_type": get_relationship_type(field),
                }

                if field.is_relation and field.related_model:
                    field_info["related_model"] = field.related_model.__name__

                # --- Handle ForeignKey and OneToOne relationships ---
                if getattr(field, "is_relation", False) and hasattr(field, "column"):
                    # Only consider forward (non-reverse) relationships
                    if not field.auto_created:
                        field_info["local_column"] = field.column
                        if hasattr(field, "target_field") and field.target_field:
                            field_info["target_column"] = field.target_field.column
                            field_info["related_table"] = field.related_model._meta.db_table

                # --- Handle ManyToMany relationships ---
                if getattr(field, "many_to_many", False) and getattr(field, "remote_field", None):
                    remote_field = field.remote_field
                    if hasattr(remote_field, "through") and remote_field.through:
                        through_model = remote_field.through
                        field_info["through_table"] = through_model._meta.db_table

                        # Extract the join fields in the through table
                        through_fields = []
                        for through_field in through_model._meta.get_fields():
                            if (
                                through_field.is_relation
                                and through_field.related_model in [model, field.related_model]
                            ):
                                through_fields.append({
                                    "field_name": through_field.name,
                                    "column_name": getattr(through_field, "column", None),
                                    "related_model": through_field.related_model.__name__,
                                    "related_table": through_field.related_model._meta.db_table,
                                })
                        field_info["through_fields"] = through_fields

                model_info["fields"].append(field_info)

            models_info[model_name] = model_info

    return models_info


def index(request):
    return JsonResponse(get_models_info())
