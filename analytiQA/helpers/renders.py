from rest_framework.renderers import JSONRenderer


class ResponseInfo:

    def __init__(self, user=None, **args) -> None:
        self.response = {
            "status": args.get('status', True),
            "status_code": args.get('status_code', ''),
            "data": args.get('data', {}),
            "message": args.get('message', '')
        }


class CustomRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        response = {
            "status": "sucesss",
            "status_code": status_code,
            "error": None,
            "data": data,
            "message": None
        }
        if not str(status_code).startswith('2'):
            response['status'] = "error"
            response['data'] = None
            try:
                response['message'] = data['detail']
            except KeyError:
                response['data'] = data
        return super().render(response, accepted_media_type, renderer_context)
