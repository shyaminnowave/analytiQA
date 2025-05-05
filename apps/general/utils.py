from apps.general.models import StatusGroup


def get_status_group(status):
    """
    Get the Status Group From the Staus
    """
    group = StatusGroup.objects.filter(status__name__in=[status]).first()
    return group if group else None