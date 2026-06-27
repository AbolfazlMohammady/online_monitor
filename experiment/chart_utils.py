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


def extract_thickness_value(resp):
    if resp.thickness_result is not None:
        return float(resp.thickness_result)
    return None


def get_response_sort_key(resp):
    date_val = resp.response_date
    if not date_val:
        date_val = getattr(resp.experiment_request, 'request_date', None)
    if not date_val and resp.created_at:
        date_val = resp.created_at
    return str(date_val or '')


def _sorted_values(responses, extractor):
    """Collect numeric values from responses, sorted chronologically."""
    pairs = []
    for resp in responses:
        if extractor is extract_strength_values:
            for value in extract_strength_values(resp):
                pairs.append((get_response_sort_key(resp), value))
        else:
            value = extractor(resp)
            if value is not None:
                pairs.append((get_response_sort_key(resp), value))
    pairs.sort(key=lambda item: item[0])
    return [value for _, value in pairs]


def build_empty_statistical_charts():
    return {
        'xbar_s': None,
        'xbar_r': None,
        'histogram': None,
        'scatter': [],
        'scatter_y_label': 'مقاومت',
    }


def build_statistical_charts_from_responses(responses):
    """Build SPC control charts, histogram, and scatter from filtered responses."""
    from core.chart_stats import build_xbar_s_chart, build_xbar_r_chart, histogram_from_values

    density_values = _sorted_values(responses, extract_density_value)
    strength_values = _sorted_values(responses, extract_strength_values)

    scatter_points, scatter_y_label = build_scatter_points(responses)

    return {
        'xbar_s': build_xbar_s_chart(density_values),
        'xbar_r': build_xbar_r_chart(strength_values),
        'histogram': histogram_from_values(density_values) if density_values else None,
        'scatter': scatter_points,
        'scatter_y_label': scatter_y_label,
    }


def build_scatter_points(responses):
    """Return scatter points and the Y-axis label (strength or thickness)."""
    points = []
    y_label = 'مقاومت'
    use_thickness = False

    for resp in responses:
        density = extract_density_value(resp)
        if density is None:
            continue

        strength_values = extract_strength_values(resp)
        y_val = strength_values[0] if strength_values else None

        if y_val is None:
            y_val = extract_thickness_value(resp)
            if y_val is not None:
                use_thickness = True

        if y_val is None:
            continue

        try:
            points.append({
                'project': resp.experiment_request.project.name,
                'date': str(resp.response_date or resp.experiment_request.request_date or ''),
                'density': density,
                'y': y_val,
            })
        except (TypeError, ValueError, AttributeError):
            continue

    if use_thickness and not any(extract_strength_values(r) for r in responses):
        y_label = 'ضخامت'

    return points, y_label
