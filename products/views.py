from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required

from .models import Product, Category, ProductReview
from .forms import ProductForm


def all_products(request):
    """
    A view to show all products,
    including sorting and search
    """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
                if sortkey == 'category':
                    sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            # pylint: disable=no-member
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "No search criteria")
                return redirect(reverse('products'))

            queries = Q(
                name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """
    view to show product details
    """

    product = get_object_or_404(Product, pk=product_id)
    """
    Adds the review models
    """
    if request.method == 'POST' and request.user.is_authenticated:
        stars = request.POST.get('stars', 3)
        content = request.POST.get('content', '')
        review = ProductReview.objects.create(
            product=product, user=request.user, stars=stars, content=content)

        return redirect('product_detail', product_id=product_id)
    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)


def delete_review(request, review_id):
    """
    Delete a product review
    """
    if request.method == 'POST' and request.user.is_authenticated:
        review = get_object_or_404(ProductReview, id=review_id)
        review.delete()

    messages.success(request, 'Your review has ben deleted!')
    return redirect(reverse('products'))


@login_required
def add_product(request):
    """
    Adds product to the store as a superuser
    """
    if not request.user.is_superuser:
        messages.error(request, 'Only store admins can access this page!')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect(reverse('products'))
        else:
            messages.error(
                request, 'Failed, check your form and try again!')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """
    edits product
    """
    if not request.user.is_superuser:
        messages.error(request, 'Only store admins can access this page!')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request, 'Failed to update product, Check that form is valid!')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You Are Editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """
    Delete a product from the store
    """
    if not request.user.is_superuser:
        messages.error(request, 'Only store admins can access this page!')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()

    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))
