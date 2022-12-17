from django.urls import reverse
from django.utils.http import urlencode


def reverse_query(view, urlconf=None, args=None, kwargs=None,
                  current_app=None, query_kwargs=None):
    base_url = reverse(view, urlconf=urlconf, args=args,
                       kwargs=kwargs, current_app=current_app)
    return (
        f'{base_url}?{urlencode(query_kwargs)}' if query_kwargs
        else base_url
    )
