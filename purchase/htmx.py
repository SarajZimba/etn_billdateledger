from django.shortcuts import render
from product.models import Product

def search_product(request):
    search_text = request.POST.get('search')

    results = Product.objects.filter(title__icontails=search_text)
    return render(request, 'purchase/purchase_create.html', {'results':results})
