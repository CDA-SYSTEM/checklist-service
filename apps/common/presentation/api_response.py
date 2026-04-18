from rest_framework.response import Response


def success_response(data=None, message='OK', status=200):
    payload = {
        'success': True,
        'message': message,
        'data': data,
    }
    return Response(payload, status=status)


def error_response(message='Error', *, status=400, code='error', details=None):
    payload = {
        'success': False,
        'error': {
            'code': code,
            'message': message,
            'details': details,
        },
    }
    return Response(payload, status=status)
