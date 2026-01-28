import json

from .models import EditableElement


def editable_elements(request):
    """Expose saved editable HTML snippets to all templates as JSON.

    The front-end visual editor uses this to hydrate elements that have been
    edited previously.
    """

    mapping = {el.key: el.content for el in EditableElement.objects.all()}
    return {"editable_elements_json": json.dumps(mapping)}