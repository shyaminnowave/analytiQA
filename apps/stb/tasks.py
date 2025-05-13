import logging
import requests
from celery import shared_task
from django.http import Http404
from django.shortcuts import get_object_or_404
from apps.stb.models import STBNode, STBNodeConfig

logger = logging.getLogger(__name__)

@shared_task
def get_stb_node_info():
    print('Inside get_stb_node_info')
    try:
        response = requests.get(
            url="https://innowave.stb-tester.com/api/_private/workgroup?ref=HEAD",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "cookie": "stbt4=ghu_XRK5qZG1J3f3zcxT7ySqTocnH1Y04t2q1Tzf:shyaminnowave:cP8lgU5w6YX8k4N7lbK35Gv5EH0;"
            }
        )
        _data = response.json()
        for key in _data:
            get_instance = get_object_or_404(STBNode, node_id=key['id'])
            print(get_instance if get_instance else None)
            if get_instance:
                try:
                    get_node_config = get_object_or_404(STBNodeConfig, stb_node=get_instance)
                    if get_node_config and get_node_config.natco != key['friendly_name']:
                        get_node_config.is_active = False
                        get_node_config.save()
                        STBNodeConfig.objects.create(stb_node=get_instance, natco=key['friendly_name'])
                except Http404:
                    STBNodeConfig.objects.create(
                        stb_node=get_instance,
                        natco=key['friendly_name'],
                    )
            logger.error('No Node Present')
        return True
    except Exception as e:
        logger.error(e)
        return False



