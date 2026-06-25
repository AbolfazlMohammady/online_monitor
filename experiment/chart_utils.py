"""Helpers for experiment results charts: layer filters and date parsing."""

from django.db.models import Q

from experiment.models import ExperimentSubType

EXPERIMENT_RESULT_LAYERS = [
    {
        'code': 'embankment',
        'label': 'خاکریزی',
        'layer_keywords': ['خاکریزی', 'خاک ریز'],
        'subtype_names': ['بستر', 'راکفیل', 'خاکریزی'],
    },
    {
        'code': 'subgrade',
        'label': 'سابگرید',
        'layer_keywords': ['سابگرید', 'سابگریت'],
        'subtype_names': ['سابگرید'],
    },
    {
        'code': 'subbase',
        'label': 'زیر اساس',
        'layer_keywords': ['زیر اساس', 'زیراساس'],
        'subtype_names': ['زیراساس', 'VSS'],
    },
    {
        'code': 'base',
        'label': 'اساس',
        'layer_keywords': ['اساس'],
        'subtype_names': ['اساس'],
        'exclude_layer_keywords': ['زیر'],
    },
    {
        'code': 'asphalt',
        'label': 'آسفالت',
        'layer_keywords': ['آسفالت'],
        'subtype_names': ['بیندر', 'توپکا', 'پریمکت', 'تک کت'],
    },
    {
        'code': 'concrete',
        'label': 'بتن ریزی',
        'layer_keywords': ['بتن'],
        'subtype_names': [
            'B_100', 'B_200', 'B_250', 'B_300', 'B_350', 'B_400',
            'C_8', 'C_16', 'C_20', 'C_24', 'C_28', 'C_32', 'ملات بنایی',
        ],
    },
]


def get_layer_filter_config(layer_code):
    if not layer_code:
        return None
    for item in EXPERIMENT_RESULT_LAYERS:
        if item['code'] == layer_code:
            return item
    return None


def get_subtypes_for_layer(layer_code):
    config = get_layer_filter_config(layer_code)
    if not config:
        return ExperimentSubType.objects.none()
    return ExperimentSubType.objects.filter(
        name__in=config['subtype_names']
    ).select_related('experiment_type').order_by('experiment_type__name', 'name')


def get_all_chart_subtypes():
    all_names = []
    for item in EXPERIMENT_RESULT_LAYERS:
        all_names.extend(item['subtype_names'])
    return ExperimentSubType.objects.filter(
        name__in=all_names
    ).select_related('experiment_type').order_by('experiment_type__name', 'name')


def filter_responses_to_chart_layers(queryset):
    """Keep only responses related to the six chart layer categories."""
    combined = Q()
    for item in EXPERIMENT_RESULT_LAYERS:
        layer_q = Q()
        for keyword in item['layer_keywords']:
            if keyword == 'اساس':
                layer_q |= Q(
                    experiment_request__layer__layer_type__name__icontains='اساس'
                ) & ~Q(experiment_request__layer__layer_type__name__icontains='زیر')
            else:
                layer_q |= Q(experiment_request__layer__layer_type__name__icontains=keyword)
        subtype_q = Q(experiment_request__experiment_subtype__name__in=item['subtype_names'])
        combined |= layer_q | subtype_q
    return queryset.filter(combined).distinct()


def filter_responses_by_layer(queryset, layer_code):
    config = get_layer_filter_config(layer_code)
    if not config:
        return queryset

    layer_q = Q()
    for keyword in config['layer_keywords']:
        if keyword == 'اساس':
            layer_q |= Q(
                experiment_request__layer__layer_type__name__icontains='اساس'
            ) & ~Q(experiment_request__layer__layer_type__name__icontains='زیر')
        else:
            layer_q |= Q(experiment_request__layer__layer_type__name__icontains=keyword)

    subtype_q = Q(experiment_request__experiment_subtype__name__in=config['subtype_names'])
    return queryset.filter(layer_q | subtype_q).distinct()


def build_empty_chart_data():
    return {
        'months': ['بدون داده'],
        'xbar_s': [None],
        'xbar_r': [None],
        'density': [0],
        'strength': [0],
    }
