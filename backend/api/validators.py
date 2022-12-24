from rest_framework.exceptions import ValidationError
from rest_framework.fields import get_attribute


class DuplicateValidator:
    message = 'Недопустимый повтор значений: {duplicates}!'
    code = 'duplicate_values_not_allowed'

    def __init__(self, source, message=None):
        source_attrs = source.split('.')
        self.field, self.sources = source_attrs[0], source_attrs[1:]
        self.message = message or self.message

    def __call__(self, attrs):
        seen = set()
        duplicates = []
        for instance in attrs[self.field]:
            value = get_attribute(instance, self.sources)
            if value in seen:
                duplicates.append(value)
            else:
                seen.add(value)
        if duplicates:
            raise ValidationError({
                self.field: self.message.format(duplicates=duplicates)
            }, code=self.code)
