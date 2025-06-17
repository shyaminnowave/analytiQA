import logging
import requests
from celery import shared_task
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from apps.stb.models import STBNode, STBNodeConfig, StbResult
from apps.core.models import TestCaseScript
from apps.stb.stbtester import STBClient

logger = logging.getLogger(__name__)

@shared_task
def get_stb_node_info():
    try:
        response = STBClient(
            baseurl="https://innowave.stb-tester.com/api/_private/workgroup?ref=HEAD",
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "cookie": "stbt4=ghu_oNaUl88nh1pesOzp7woPZr224B1SUB0FJeqG:shyaminnowave:uDbIKZOqqSdCehbLRLQmtqSgIyE"
            }
        )
        _data = response.get_stb_node_info()
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


@shared_task()
def get_testcase_result():
    stb_client = STBClient(baseurl='https://innowave.stb-tester.com/api/v2/', headers={
        "Authorization": "token zvqu7pcsalb-1uMs-oYnO1rmzTU2fz0-",
    })
    testscripts = TestCaseScript.objects.values('script_name').distinct()
    _cached_result = {} 
    _results = []

    try:
        for script_dict in testscripts:
            script_name = script_dict['script_name']

            if script_name not in _cached_result:
                # Get the actual TestCaseScript instance for this script_name
                script_instance = TestCaseScript.objects.filter(script_name=script_name).first()
                if script_instance:
                    _cached_result[script_name] = script_instance

            # Make sure we have the script instance
            if script_name not in _cached_result:
                logger.warning(f"No TestCaseScript instance found for {script_name}")
                continue

            script_instance = _cached_result[script_name]

            _result_instance = StbResult.objects.filter(script=script_instance).last()

            if _result_instance:
                response = stb_client.get_results(script_name, _result_instance.get_start_date())
            else:
                response = stb_client.get_results(script_name)

            if response is not None:
                # Clear the results list for each script to avoid mixing results
                _results = []
                for j in response:
                    _data = {
                        "result_id": j['result_id'],
                        "result_url": j['result_url'],
                        "triage_url": j['triage_url'],
                        "job_uid": j['job_uid'],
                        "start_time": j['start_time'],
                        "end_time": j['end_time'],
                        "script": script_instance,  # Use the instance from cache
                        "result": j['result'],
                        "failure_reason": j['failure_reason']
                    }
                    _results.append(StbResult(**_data))

                # Create the results within the script loop
                if _results:
                    with transaction.atomic():
                        StbResult.objects.bulk_create(_results, ignore_conflicts=True)

    except Exception as e:
        logger.error(f"Error in get_testcase_result: {e}")
        # Re-raise to properly handle the task failure in Celery
        raise