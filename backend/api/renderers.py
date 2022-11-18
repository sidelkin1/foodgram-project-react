from rest_framework_csv import renderers


class IngredientCSVRenderer(renderers.CSVRenderer):
    header = ('Ингредиент', 'Ед. изм.', 'Количество')
    writer_opts = {'delimiter': ';'}
