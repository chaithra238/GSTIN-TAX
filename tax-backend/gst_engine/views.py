from django.http import JsonResponse
from .scrapper import run_scraper

def search(request):

    gstin = request.GET.get("query")

    if not gstin:

        return JsonResponse({

            "status":"failed",

            "message":"GST Number Required"

        })

    result = run_scraper(gstin)

    return JsonResponse(result)