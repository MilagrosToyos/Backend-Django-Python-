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
                    "proxy": {
                        "useApifyProxy": True,
                        "apifyProxyGroups": ["RESIDENTIAL"],
                        "apifyProxyCountry": "US"
                    }
            }
            # start by executing the Actor
            apify_run_url = f'https://api.apify.com/v2/acts/{apify_actor_id}/runs'

            print(f"Calling Apify API to start actor run (async): {apify_actor_id}")
            run_response = requests.request("POST", apify_run_url, headers=headers, json=actor_input_playload, timeout=60)
            
            run_response.raise_for_status()
            
            run_data = run_response.json()

            run_id = run_data['data']['id']
            dataset_id = run_data['data']['defaultDatasetId']
            print(f"Actor run stated, run ID: {run_id},defaultDatasetId: {dataset_id}")

            apify_get_dataset_items_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items'
            print(f"Fetching dataset items from: {dataset_id}")

            dataset_items_response = requests.get(apify_get_dataset_items_url, headers=headers, timeout=120)
            dataset_items_response.raise_for_status()
            jobs_data = dataset_items_response.json()

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