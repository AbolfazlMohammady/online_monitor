"""Helpers for experiment results charts: layer filters and chart aggregation."""

from collections import defaultdict

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

METRIC_FIELDS = (
    ('density', 'تراکم', 'density_result'),
    ('strength', 'مقاومت فشاری', None),
    ('thickness', 'ضخامت', 'thickness_result'),
)


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


def _metric_value(resp, metric_key):
    if metric_key == 'density':
        return extract_density_value(resp)
    if metric_key == 'thickness':
        return extract_thickness_value(resp)
    if metric_key == 'strength':
        values = extract_strength_values(resp)
        return values[0] if values else None
    return None


def _metric_values_list(resp, metric_key):
    if metric_key == 'strength':
        return extract_strength_values(resp)
    value = _metric_value(resp, metric_key)
    return [value] if value is not None else []


def _sorted_values(responses, metric_key):
    """Collect numeric values for a metric from responses, sorted chronologically."""
    pairs = []
    for resp in responses:
        for value in _metric_values_list(resp, metric_key):
            pairs.append((get_response_sort_key(resp), value))
    pairs.sort(key=lambda item: item[0])
    return [value for _, value in pairs]


def _metric_label(metric_key):
    for key, label, _field in METRIC_FIELDS:
        if key == metric_key:
            return label
    return 'مقدار'


def resolve_layer_metrics(responses):
    """
    Pick primary/secondary metrics from whatever test results exist
    in the filtered responses (not hardcoded per layer type).
    """
    counts = {}
    for key, _label, _field in METRIC_FIELDS:
        total = 0
        for resp in responses:
            total += len(_metric_values_list(resp, key))
        counts[key] = total

    available = [(key, count) for key, count in counts.items() if count > 0]
    if not available:
        return None, None

    available.sort(key=lambda item: (-item[1], item[0]))
    primary_key = available[0][0]
    secondary_key = available[1][0] if len(available) > 1 else None
    return primary_key, secondary_key


def build_empty_statistical_charts():
    return {
        'has_data': False,
        'primary_label': 'مقدار',
        'secondary_label': 'مقدار',
        'xbar_s': None,
        'xbar_r': None,
        'histogram': None,
        'scatter': [],
        'scatter_x_label': 'محور X',
        'scatter_y_label': 'محور Y',
    }


def build_monthly_bar_chart(responses, primary_key, secondary_key=None):
    """Monthly averages for bar/histogram-style chart."""
    monthly = defaultdict(lambda: defaultdict(list))

    for resp in responses:
        month_key = get_response_month_key(resp)
        if not month_key:
            continue
        for value in _metric_values_list(resp, primary_key):
            monthly[month_key][primary_key].append(value)
        if secondary_key:
            for value in _metric_values_list(resp, secondary_key):
                monthly[month_key][secondary_key].append(value)

    if not monthly:
        return None

    months = sorted(monthly.keys())
    primary_series = []
    secondary_series = []

    for month in months:
        bucket = monthly[month]
        p_vals = bucket.get(primary_key, [])
        primary_series.append(
            round(sum(p_vals) / len(p_vals), 3) if p_vals else None
        )
        if secondary_key:
            s_vals = bucket.get(secondary_key, [])
            secondary_series.append(
                round(sum(s_vals) / len(s_vals), 3) if s_vals else None
            )

    result = {
        'months': months,
        'primary': primary_series,
        'primary_label': _metric_label(primary_key),
    }
    if secondary_key:
        result['secondary'] = secondary_series
        result['secondary_label'] = _metric_label(secondary_key)
    return result


def build_scatter_points(responses, primary_key, secondary_key):
    """Scatter using two available metrics from the same filtered responses."""
    if not primary_key or not secondary_key:
        return [], _metric_label(primary_key or 'density'), _metric_label(secondary_key or 'strength')

    points = []
    for resp in responses:
        x_vals = _metric_values_list(resp, primary_key)
        y_vals = _metric_values_list(resp, secondary_key)
        if not x_vals or not y_vals:
            continue
        try:
            project_name = resp.experiment_request.project.name
        except (AttributeError, TypeError):
            project_name = 'نامشخص'

        x_val = x_vals[0]
        y_val = y_vals[0]
        points.append({
            'project': project_name,
            'date': str(resp.response_date or resp.experiment_request.request_date or ''),
            'x': x_val,
            'y': y_val,
        })

    return points, _metric_label(primary_key), _metric_label(secondary_key)


def build_statistical_charts_from_responses(responses):
    """
    Build all four charts from filtered layer responses.
    Primary metric drives Xbar-S, Xbar-R, and histogram;
    scatter uses primary vs secondary metric available in data.
    """
    from core.chart_stats import build_xbar_s_chart, build_xbar_r_chart

    primary_key, secondary_key = resolve_layer_metrics(responses)
    if not primary_key:
        return build_empty_statistical_charts()

    primary_label = _metric_label(primary_key)
    secondary_label = _metric_label(secondary_key) if secondary_key else primary_label
    primary_values = _sorted_values(responses, primary_key)

    scatter_points, scatter_x_label, scatter_y_label = build_scatter_points(
        responses, primary_key, secondary_key
    )

    return {
        'has_data': bool(primary_values),
        'primary_label': primary_label,
        'secondary_label': secondary_label,
        'xbar_s': build_xbar_s_chart(primary_values),
        'xbar_r': build_xbar_r_chart(primary_values),
        'histogram': build_monthly_bar_chart(responses, primary_key, secondary_key),
        'scatter': scatter_points,
        'scatter_x_label': scatter_x_label,
        'scatter_y_label': scatter_y_label,
    }
