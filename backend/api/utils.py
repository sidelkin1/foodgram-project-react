from django.db.models import Exists, OuterRef


def get_exists_subquery(model, user, field, outer_ref):
    return {field: Exists(model.objects.filter(
        user_id=user.id,
        **{outer_ref: OuterRef('pk')},
    ))}
