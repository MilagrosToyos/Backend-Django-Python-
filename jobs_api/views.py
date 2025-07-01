from django.shortcuts import render

import os, json, requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt #To POST without Django form
from dotenv import load_dotenv

#Loads environment variables if not done in settings.py
load_dotenv()

APYFY_API_TOKEN = os.getenv('APYFY_API_TOKEN')
APYFY_ACTOR_ID = 'apify/linkedin-jobs-scraper'

@csrf_exempt

def get_linkedin_jobs(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            li_at_token = data.get('li_at')
            if not li_at_token:
                return JsonResponse({'error': 'Missing li_at token in request body'}, status=400)
            if not APYFY_API_TOKEN:
                return JsonResponse({'error': 'Apify API token not configures. Please check .env file.'}, status=500)
            #config. headers to request Apify:
            headers = {
                'Authorization': f'Bearer {APYFY_API_TOKEN}',
                'Content-Type': 'application/json',
            }
            apify_payload = {
                "actorId": APYFY_ACTOR_ID,
                "input":  {
                    "linkedinSessionCookie": li_at_token,
                    "maxItems": 10,
                    "resultsPerPage": 10,
                    "proxy": {
                        "useApifyProxy": True,
                        "apifyProxyGroups": ["RESIDENTIAL"],
                        "apifyProxyCountry": "US"
                    }
                }
            }
            apify_run_url = f'https://api.apify.com/v2/acts/{APYFY_ACTOR_ID}/run-sync-get-dataset-items'
            print(f"Calling Apify API for actor: {APYFY_ACTOR_ID}")
            print(f"With li_at token (first 10 chars): {li_at_token[:10]}...")
            
            response = requests.post(apify_run_url, headers=headers, json=apify_payload, timeout=120)
            response.raise_for_status()

            jobs_data = response.json()

            if not jobs_data:
                return JsonResponse({'message': 'No job offers found or Apify returned empty data.'}, status=200)
            return JsonResponse(jobs_data, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except requests.exceptions.RequestException as e: # <--- Simplificamos a un solo RequestException
            # Aquí capturamos Timeout, ConnectionError, HTTPError, etc. de requests
            error_message = f'Error communicating with Apify: {str(e)}'
            if isinstance(e, requests.exceptions.HTTPError):
                error_message += f' - Status: {e.response.status_code}, Detail: {e.response.text}'
            print(f"API request failed: {error_message}")
            return JsonResponse({'error': error_message}, status=500)
        except Exception as e:
            print(f"An unexpected internal error occurred: {e}")
            return JsonResponse({'error': f'An unexpected internal server error occurred: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are supported'}, status=405)
