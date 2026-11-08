from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm
from .models import Category, Comment, Product


def product_list(request: HttpRequest, category_slug: str | None = None) -> HttpResponse:
    """Render the product overview, optionally restricted to a single category.

    Args:
        request: The incoming HTTP request.
        category_slug: The slug of the category to filter by. If it is omitted,
            the products of all categories are listed.

    Returns:
        HttpResponse: The rendered product overview page.
    """
    categories = Category.objects.all()
    products = Product.objects.select_related("category").annotate(
        avg_rating=Avg("comments__rating"), total_ratings=Count("comments")
    )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    return render(request, "products.html", {"categories": categories, "products": products})


def product_detail(request: HttpRequest, category_slug: str, pk: int) -> HttpResponse:
    """Render the details of a single product and handle its review form.

    A successful review submission is answered with a redirect to this view, so
    that a reload of the page does not submit the review a second time. The
    review form is always rendered with empty fields, which means that the
    rating stars and the comment text are cleared after a submission and stay
    cleared when the page is opened again.

    Args:
        request: The incoming HTTP request.
        category_slug: The slug of the category the product belongs to.
        pk: The primary key of the product.

    Returns:
        HttpResponse: The rendered product details page, or a redirect to this
            page after a review has been saved successfully.
    """
    product = get_object_or_404(
        Product.objects.select_related("category").annotate(
            avg_rating=Avg("comments__rating"), total_ratings=Count("comments")
        ),
        pk=pk,
        category__slug=category_slug,
    )

    related_products = (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk)
        .annotate(avg_rating=Avg("comments__rating"), total_ratings=Count("comments"))
        .order_by("-avg_rating", "-total_ratings", "name")[:8]
    )

    comments = product.comments.select_related("user").order_by("-created_at")

    if request.method == "POST":
        form = CommentForm(request.POST, initial={"user": request.user if request.user.is_authenticated else None})
        if form.is_valid():
            rating: int = form.cleaned_data["rating"]
            text: str = form.cleaned_data.get("text", "")

            if request.user.is_authenticated:
                # Upsert: update existing comment or create a new one
                comment, created = Comment.objects.get_or_create(
                    product=product, user=request.user, defaults={"rating": rating, "text": text}
                )
                if not created:
                    comment.rating = rating
                    comment.text = text
                    comment.save()
                messages.success(request, "Your rating was {}.".format("submitted" if created else "updated"))
            else:
                # Guest: create a new comment (no uniqueness constraint)
                comment = form.save(commit=False)
                comment.product = product
                comment.save()
                messages.success(request, "Thank you for your rating.")

            return redirect("product_detail", category_slug=category_slug, pk=product.pk)
    else:
        # The review form is never pre-filled, so that its fields are empty after a
        # submission and remain empty when the page is opened again.
        form = CommentForm()

    return render(
        request,
        "product.html",
        {"product": product, "comments": comments, "related_products": related_products, "form": form},
    )
