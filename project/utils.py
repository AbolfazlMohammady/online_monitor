from project.models import Project


def get_user_accessible_projects(user):
    """All projects the user may access (main and sub-projects)."""
    if not user or not user.is_authenticated:
        return Project.objects.none()

    if user.is_superuser:
        return Project.objects.all()

    project_ids = set()
    project_ids.update(user.managed_projects.values_list('id', flat=True))
    project_ids.update(user.technical_projects.values_list('id', flat=True))
    project_ids.update(user.qc_projects.values_list('id', flat=True))
    project_ids.update(user.project_experts.values_list('id', flat=True))
    project_ids.update(user.accessible_projects.values_list('id', flat=True))
    return Project.objects.filter(id__in=project_ids)


def get_filter_projects(user):
    """
    Ordered list for project filter dropdowns:
    main projects first, then their sub-projects indented underneath.
    """
    accessible = get_user_accessible_projects(user)
    accessible_ids = set(accessible.values_list('id', flat=True))

    result = []
    included_ids = set()

    for main in accessible.filter(parent_project__isnull=True).order_by('name'):
        result.append(main)
        included_ids.add(main.id)
        for sub in accessible.filter(parent_project=main).order_by('name'):
            result.append(sub)
            included_ids.add(sub.id)

    for orphan in accessible.filter(parent_project__isnull=False).exclude(id__in=included_ids).order_by('name'):
        result.append(orphan)

    return result


def project_filter_display_name(project):
    if project.parent_project_id:
        return f"— {project.name}"
    return project.name


def get_project_filter_ids(project_id, user=None):
    """
    Resolve selected project to IDs used in queryset filters.
    Selecting a main project includes all accessible sub-projects.
    """
    if not project_id:
        return None

    try:
        project_id = int(project_id)
    except (ValueError, TypeError):
        return None

    accessible = get_user_accessible_projects(user) if user else Project.objects.all()
    project = accessible.filter(pk=project_id).first()
    if not project:
        return None

    ids = [project_id]
    if project.parent_project_id is None:
        sub_ids = list(
            accessible.filter(parent_project_id=project_id).values_list('id', flat=True)
        )
        ids.extend(sub_ids)
    return ids


def filter_queryset_by_project(queryset, project_id, user, project_field='project'):
    """Apply project filter on a queryset, expanding main projects to sub-projects."""
    ids = get_project_filter_ids(project_id, user)
    if ids is None:
        return queryset
    return queryset.filter(**{f'{project_field}__in': ids})


def filter_queryset_by_nested_project(queryset, project_id, user, project_field='experiment_request__project'):
    """Apply project filter when project is nested (e.g. experiment responses)."""
    ids = get_project_filter_ids(project_id, user)
    if ids is None:
        return queryset
    return queryset.filter(**{f'{project_field}__in': ids})


def parse_jalali_date_string(date_str):
    """Convert YYYY/MM/DD or YYYY-MM-DD jalali string to gregorian date."""
    if not date_str:
        return None
    import jdatetime

    normalized = date_str.strip().replace('-', '/')
    parts = normalized.split('/')
    if len(parts) != 3:
        return None
    try:
        jy, jm, jd = int(parts[0]), int(parts[1]), int(parts[2])
        return jdatetime.date(jy, jm, jd).togregorian()
    except (ValueError, TypeError):
        return None
