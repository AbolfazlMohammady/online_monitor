"""Helpers for experiment results charts: layer filters and chart aggregation."""

from django.db.models import Q

EXPERIMENT_RESULT_LAYERS = [
    {
        'code': 'embankment',
        'label': 'خاکریزی',
        'layer_keywords': ['خاکریزی', 'خاک ریز', 'خاکریز'],
    },
    {
        'code': 'subgrade',
        'label': 'سابگرید',
        'layer_keywords': ['سابگرید', 'سابگریت'],
    },
    {
        'code': 'subbase',
        'label': 'زیر اساس',
        'layer_keywords': ['زیر اساس', 'زیراساس'],
    },
    {
        'code': 'base',
        'label': 'اساس',
        'layer_keywords': ['اساس'],
        'exclude_layer_keywords': ['زیر'],
    },
    {
        'code': 'asphalt',
        'label': 'آسفالت',
        'layer_keywords': ['آسفالت'],
    },
    {
        'code': 'concrete',
        'label': 'بتن ریزی',
        'layer_keywords': ['بتن', 'مگر'],
    },
]


def get_layer_filter_config(layer_code):
    if not layer_code:
        return None
    for item in EXPERIMENT_RESULT_LAYERS:
        if item['code'] == layer_code:
            return item
    return None


def _layer_type_q_for_config(config):
    """Match experiment requests by project layer type (all tests on that layer)."""
    layer_q = Q()
    for keyword in config['layer_keywords']:
        if keyword == 'اساس':
            layer_q |= Q(
                experiment_request__layer__layer_type__name__icontains='اساس'
            ) & ~Q(experiment_request__layer__layer_type__name__icontains='زیر')
        else:
            layer_q |= Q(experiment_request__layer__layer_type__name__icontains=keyword)

    if config.get('code') == 'concrete':
        layer_q |= Q(experiment_request__experiment_type__name__icontains='مقاومت فشاری بتن')
        layer_q |= Q(experiment_request__experiment_type__name__icontains='بتن')

    return layer_q


def filter_responses_to_chart_layers(queryset):
    """Keep only responses for the six chart layer categories (by request layer)."""
    combined = Q()
    for item in EXPERIMENT_RESULT_LAYERS:
        combined |= _layer_type_q_for_config(item)
    return queryset.filter(combined).distinct()


def filter_responses_by_layer(queryset, layer_code):
    """Filter responses for one layer — includes every test registered on that layer."""
    config = get_layer_filter_config(layer_code)
    if not config:
        return queryset
    return queryset.filter(_layer_type_q_for_config(config)).distinct()


def get_response_month_key(resp):
    """Month key for charts; falls back when response_date is empty."""
    date_val = resp.response_date
    if not date_val:
        date_val = getattr(resp.experiment_request, 'request_date', None)
    if not date_val and resp.created_at:
        date_val = resp.created_at

    if not date_val:
        return None

    text = str(date_val).strip().replace('/', '-')
    if ' ' in text:
        text = text.split(' ')[0]
    if 'T' in text:
        text = text.split('T')[0]
    return text[:7] if len(text) >= 7 else text


def extract_density_value(resp):
    if resp.density_result is not None:
        return float(resp.density_result)
    return None


def extract_strength_values(resp):
    values = []
    if resp.strength_average is not None:
        values.append(float(resp.strength_average))
    else:
        for field in ('strength_result1', 'strength_result2', 'strength_result3'):
            val = getattr(resp, field, None)
            if val is not None:
                values.append(float(val))
    return values


def build_empty_chart_data():
    return {
        'months': ['بدون داده'],
        'xbar_s': [None],
        'xbar_r': [None],
        'density': [None],
        'strength': [None],
    }


def build_chart_data_from_responses(responses):
    """Aggregate monthly series for line/bar charts."""
    from collections import defaultdict

    monthly_data = defaultdict(lambda: {'density': [], 'strength': []})

    for resp in responses:
        month_key = get_response_month_key(resp)
        if not month_key:
            continue

        density = extract_density_value(resp)
        if density is not None:
            monthly_data[month_key]['density'].append(density)

        strength_values = extract_strength_values(resp)
        if strength_values:
            monthly_data[month_key]['strength'].extend(strength_values)

    chart_data = {
        'months': [],
        'xbar_s': [],
        'xbar_r': [],
        'density': [],
        'strength': [],
    }

    for month in sorted(monthly_data.keys()):
        data = monthly_data[month]
        chart_data['months'].append(month)

        if data['density']:
            avg_density = sum(data['density']) / len(data['density'])
            chart_data['xbar_s'].append(round(avg_density, 3))
            chart_data['density'].append(round(avg_density, 3))
        else:
            chart_data['xbar_s'].append(None)
            chart_data['density'].append(None)

        if data['strength']:
            avg_strength = sum(data['strength']) / len(data['strength'])
            chart_data['xbar_r'].append(round(avg_strength, 3))
            chart_data['strength'].append(round(avg_strength, 3))
        else:
            chart_data['xbar_r'].append(None)
            chart_data['strength'].append(None)

    if not chart_data['months']:
        return build_empty_chart_data()

    return chart_data


def build_scatter_points(responses):
    points = []
    for resp in responses:
        density = extract_density_value(resp)
        strength_values = extract_strength_values(resp)
        strength = strength_values[0] if strength_values else None
        if density is None or strength is None:
            continue
        try:
            points.append({
                'project': resp.experiment_request.project.name,
                'date': str(resp.response_date or resp.experiment_request.request_date or ''),
                'density': density,
                'strength': strength,
            })
        except (TypeError, ValueError, AttributeError):
            continue
    return points
