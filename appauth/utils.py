from rest_framework.exceptions import ValidationError
from .models import Funnel, FunnelTemplate, Page

categories = (
    'Business',
    'Ecommerce',
    'Blogs/news',
    'Portfolio',
    'Service provider',
    'Landing page',
    'Wiki/database',
    'Forum',
    'Event',
    'Others'
)

def get_category(cat: str):
    if cat in categories:
        return cat
    
    else:
        return 'Others'

def get_funnel_manager(funnel_type: str):
    model = None
    if funnel_type == 'public':
        model = Funnel

    elif funnel_type == 'template':
        model = FunnelTemplate

    if model:
        return model.objects

    else:
        raise ValidationError('Invalid funnel type')


def get_index_page(funnel_id, funnel_type):
    index = Page.objects.filter(funnel_id=funnel_id, funnel_type=funnel_type, is_index=True)
    slug = None

    if not index.exists():
        index = Page.objects.filter(funnel_id=funnel_id)

    if index.exists():
        return index.first()

    else:
        return None

def funnel_label(funnel_type: str) -> str:
    return "public" if funnel_type == "funnel" else funnel_type