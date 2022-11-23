import json
import numpy as np
from django.http import JsonResponse



def getLaplaceNoise(request):
    post_data = json.loads(request.body)
    mu, b = post_data['mu'], post_data['b']
    laplace_noise = np.random.laplace(mu, b, 1000)
    return JsonResponse({'noise': list(laplace_noise)})