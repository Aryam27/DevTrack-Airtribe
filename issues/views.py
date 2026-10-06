import json
import os
from .models import Reporter, Issue, CriticalIssue, LowPriorityIssue
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse

from .models import Reporter

REPORTERS_FILE = os.path.join(settings.BASE_DIR, 'reporters.json')


def read_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def write_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2) 

def find_by_id(records, raw_id, label):
    try:
        wanted = int(raw_id) 
    except ValueError:
        return JsonResponse({'error': 'id must be a number'}, status=400)
    for record in records:
        if record['id'] == wanted:
            return JsonResponse(record, status=200)
    return JsonResponse({'error': f'{label} not found'}, status=404)

@csrf_exempt
def reporters(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        reporter = Reporter(data.get('id'), data.get('name'),
                            data.get('email'), data.get('team'))
        try:
            reporter.validate()
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)

        all_reporters = read_json(REPORTERS_FILE)
        all_reporters.append(reporter.to_dict())
        write_json(REPORTERS_FILE, all_reporters)
        return JsonResponse(reporter.to_dict(), status=201)
    if request.method == 'GET':
        all_reporters = read_json(REPORTERS_FILE)
        raw_id = request.GET.get('id')
        if raw_id is not None:
            return find_by_id(all_reporters, raw_id, 'Reporter')
        return JsonResponse(all_reporters, safe=False, status=200)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

ISSUES_FILE = os.path.join(settings.BASE_DIR, 'issues.json')

@csrf_exempt
def issues(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        args = (data.get('id'), data.get('title'), data.get('description'),
                data.get('status'), data.get('priority'), data.get('reporter_id'))

        if data.get('priority') == 'critical':
            issue = CriticalIssue(*args)
        elif data.get('priority') == 'low':
            issue = LowPriorityIssue(*args)
        else:
            issue = Issue(*args)

        try:
            issue.validate()
            pass
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        
        reporter_ids = [r['id'] for r in read_json(REPORTERS_FILE)]
        if issue.reporter_id not in reporter_ids:
            return JsonResponse({'error': 'Reporter not found'}, status=400)
        all_issues = read_json(ISSUES_FILE)
        if any(i['id'] == issue.id for i in all_issues):
            return JsonResponse({'error': 'Issue id already exists'}, status=400)
        all_issues.append(issue.to_dict())
        write_json(ISSUES_FILE, all_issues)

        response_data = issue.to_dict()
        response_data['message'] = issue.describe()
        return JsonResponse(response_data, status=201)
    if request.method == 'GET':
        all_issues = read_json(ISSUES_FILE)
        raw_id = request.GET.get('id')
        status = request.GET.get('status')

        if raw_id is not None:
            return find_by_id(all_issues, raw_id, 'Issue')
        if status is not None:
            filtered = [i for i in all_issues if i['status'] == status]
            return JsonResponse(filtered, safe=False, status=200)
        return JsonResponse(all_issues, safe=False, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)