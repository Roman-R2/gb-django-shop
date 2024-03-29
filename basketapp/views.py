from inspect import getmembers

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from basketapp.models import Basket
from mainapp.models import Product


@login_required
def basket(request):
    context = {
        "basket_list": Basket.objects.filter(user=request.user)
    }
    return render(request, 'basketapp/basket.html', context=context)


@login_required
def basket_add(request, pk):  # pk - Product pk
    if 'login' in request.META.get('HTTP_REFERER'):
        slug = get_object_or_404(Product, pk=pk).slug
        return HttpResponseRedirect(reverse('mainapp:product', args=[slug]))

    product_item = get_object_or_404(Product, pk=pk)
    basket_item = Basket.objects.filter(user=request.user,
                                        product=product_item)
    if not basket_item:
        basket_item = Basket(
            user=request.user,
            product=product_item,
            quantity=1,
        )
        basket_item.save()
    else:
        basket_item.update(quantity=F("quantity") + 1)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def basket_remove(request, pk):  # pk - Basket pk
    basket_item = get_object_or_404(Basket, pk=pk)
    basket_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def basket_edit(request, pk, quantity):
    if request.is_ajax():
        quantity = int(quantity)
        basket_item = Basket.objects.get(pk=pk)
        if quantity > 0:
            basket_item.quantity = quantity
            basket_item.save()
        else:
            basket_item.delete()

        basket_list = Basket.objects.filter(user=request.user)
        result = render_to_string('basketapp/inc/_inc_basket_list.html', {
            'basket_list': basket_list
        })
        return JsonResponse({'result': result})
