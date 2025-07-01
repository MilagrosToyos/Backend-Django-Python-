from django.shortcuts import render

import json, requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt #To POST without Django form
from requests.exceptions import RequestException, Timeout
from django.conf import settings

@csrf_exempt

def get_linkedin_jobs(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            li_at_token = data.get('li_at')
            if not li_at_token:
                return JsonResponse({'error': 'Missing li_at token in request body'}, status=400)
            
            apify_api_token = settings.APYFY_API_TOKEN
            apify_actor_id = settings.APYFY_ACTOR_ID

            if not apify_api_token:
                return JsonResponse({'error': 'Apify API token not configures. Please check .env file.'}, status=500)
            
            #config. headers to request Apify:
            headers = {
                'Authorization': f'Bearer {apify_api_token}',
                'Content-Type': 'application/json',
            }
            actor_input_playload = {
                    "linkedinSessionCookie": li_at_token,
                    "search": "Developer",
                    "location": "Argentina",
                    "maxItems": 10,
                    "proxy": {
                        "useApifyProxy": True,
                        "apifyProxyGroups": ["RESIDENTIAL"],
                        "apifyProxyCountry": "US"
                    }
            }
            # start by executing the Actor
            apify_run_url = f'https://api.apify.com/v2/acts/{apify_actor_id}/run-sync-get-dataset-items'

            print(f"Calling Apify API to start actor run (async): {apify_actor_id}")
            run_response = requests.post(apify_run_url, headers=headers, json=actor_input_playload, timeout=300)
            run_response.raise_for_status()
            
            jobs_data = run_response.json()

            if not jobs_data:
                return JsonResponse({'message': 'No job offers found or Apify returned empty data.'}, status=200)
            return JsonResponse(jobs_data, safe=False)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except requests.exceptions.RequestException as e:
            error_message = f'Error communicating with Apify: {str(e)}'
            if isinstance(e, requests.exceptions.HTTPError):
                error_message += f' - Status: {e.response.status_code}, Detail: {e.response.text}'
            print(f"API request failed: {error_message}")
            return JsonResponse({'error': error_message}, status=500)
        except KeyError as e:
            print(f"Error parsing Apify response (missing key): {e}. Full response: {run_start_response.text if 'run_start_response' in locals() else 'N/A'}")
            return JsonResponse({'error': f'Error processing Apify response: missing expected data ({e})'}, status=500)
        except Exception as e:
            print(f"An unexpected internal error occurred: {e}")
            return JsonResponse({'error': f'An unexpected internal server error occurred: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are supported'}, status=405)
    

def show_works_html(request):
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/linkedin-jobs/',
            json={"li_at": "your_li_at_token_LinkedIn"},
            timeout=300
        )
        response.raise_for_status()
        jobs = response.json()
    except:
        jobs = []
    return render(request, 'jobs_api/templates.html', {'jobs': jobs})