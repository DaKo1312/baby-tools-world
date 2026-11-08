from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Comment, Product

User = get_user_model()


class ProductViewAndCommentFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Toys", slug="toys")
        cls.product = Product.objects.create(name="Blue Rattle", price="9.99", category=cls.category)
        cls.user = User.objects.create_user(username="tester", email="t@example.com", password="pass1234")
        cls.other = User.objects.create_user(username="other", email="o@example.com", password="pass1234")

    # -------- Product listing & detail (existing views) --------
    def test_product_list_view(self):
        url = reverse("products")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.product.name)

    def test_product_list_by_category(self):
        url = reverse("products_by_category", args=[self.category.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.product.name)

    def test_product_detail_get_includes_form_and_comments(self):
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Form fields
        for field_name in ["rating", "text", "guest_name", "guest_email"]:
            self.assertIn(field_name, resp.content.decode())
        # Context objects
        self.assertIn("form", resp.context)
        self.assertIn("comments", resp.context)

    def test_authenticated_user_form_prefilled_with_existing_comment(self):
        # existing comment
        Comment.objects.create(product=self.product, user=self.user, rating=3, text="Existing")
        self.client.login(username="tester", password="pass1234")
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        form = resp.context["form"]
        # initial data should reflect existing comment
        self.assertEqual(form.initial.get("rating"), 3)
        self.assertEqual(form.initial.get("text"), "Existing")

    # -------- Authenticated user comment flow (create/upsert) --------
    def test_authenticated_user_create_comment(self):
        self.client.login(username="tester", password="pass1234")
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        payload = {"rating": 4, "text": "Nice product"}
        resp = self.client.post(url, data=payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        # Comment created & linked
        comment = Comment.objects.get(product=self.product, user=self.user)
        self.assertEqual(comment.rating, 4)
        self.assertEqual(comment.text, "Nice product")
        # Upsert message present
        # self.assertContains(resp, "Your rating was submitted")

    def test_authenticated_user_update_existing_comment(self):
        # existing
        Comment.objects.create(product=self.product, user=self.user, rating=3, text="Old")
        self.client.login(username="tester", password="pass1234")
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        payload = {"rating": 5, "text": "Updated text"}
        resp = self.client.post(url, data=payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        comment = Comment.objects.get(product=self.product, user=self.user)
        self.assertEqual(comment.rating, 5)
        self.assertEqual(comment.text, "Updated text")

    # -------- Guest comment validation --------
    def test_guest_comment_missing_required_guest_fields(self):
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        # Missing guest_name & guest_email -> form errors
        payload = {"rating": 5, "text": "Guest text"}
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 200)
        form = resp.context["form"]
        self.assertIn("guest_name", form.errors)
        self.assertIn("guest_email", form.errors)

    def test_guest_comment_success(self):
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        payload = {
            "rating": 5,
            "text": "Great!",
            "guest_name": "Alice",
            "guest_email": "alice@example.com",
        }
        resp = self.client.post(url, data=payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Comment.objects.filter(product=self.product, guest_name="Alice").exists())

    # -------- Multiple guest comments allowed (no uniqueness) --------
    def test_multiple_guest_comments_allowed(self):
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        base = {
            "rating": 4,
            "guest_name": "Guest",
            "guest_email": "g@example.com",
        }
        self.client.post(url, data={**base, "text": "First"})
        self.client.post(url, data={**base, "text": "Second"})
        self.assertEqual(
            Comment.objects.filter(product=self.product, guest_name="Guest").count(),
            2,
        )

    # -------- Auth user single comment enforced (upsert) --------
    def test_user_comment_single_record_enforced(self):
        Comment.objects.create(product=self.product, user=self.user, rating=2)
        self.client.login(username="tester", password="pass1234")
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        self.client.post(url, data={"rating": 5, "text": "Changed"})
        self.assertEqual(
            Comment.objects.filter(product=self.product, user=self.user).count(),
            1,
        )
        comment = Comment.objects.get(product=self.product, user=self.user)
        self.assertEqual(comment.rating, 5)
        self.assertEqual(comment.text, "Changed")

    # -------- Related products section presence --------
    def test_related_products_context(self):
        # Add another product in same category to appear as related
        Product.objects.create(name="Red Rattle", price="5.00", category=self.category)
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("related_products", resp.context)
        self.assertGreaterEqual(len(resp.context["related_products"]), 1)

    # -------- Invalid product detail (404) --------
    def test_product_detail_404(self):
        bad_url = reverse("product_detail", args=[self.category.slug, 999999])
        resp = self.client.get(bad_url)
        self.assertEqual(resp.status_code, 404)

    # -------- Empty aggregation states --------
    def test_product_list_no_comments_annotations_zero(self):
        url = reverse("products")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        products = resp.context.get("products") or resp.context.get("object_list")
        prod = [p for p in products if p.pk == self.product.pk][0]
        # avg_rating will be None or 0 depending on DB; treat None as 0
        self.assertIn(prod.total_ratings, (0, None))
        self.assertTrue(prod.total_ratings in (0, None))

    def test_product_detail_no_comments_annotations_zero(self):
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        prod = resp.context["product"]
        self.assertIn(getattr(prod, "total_ratings", 0), (0, None))

    # -------- Aggregation: average rating annotations --------
    def test_product_list_average_rating_annotation(self):
        # create ratings: user + two guests
        Comment.objects.create(product=self.product, user=self.user, rating=5)
        Comment.objects.create(
            product=self.product,
            guest_name="G1",
            guest_email="g1@example.com",
            rating=1,
        )
        Comment.objects.create(
            product=self.product,
            guest_name="G2",
            guest_email="g2@example.com",
            rating=3,
        )
        expected_avg = (5 + 1 + 3) / 3
        url = reverse("products")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        products = resp.context.get("products") or resp.context.get("object_list")
        prod = [p for p in products if p.pk == self.product.pk][0]
        self.assertAlmostEqual(float(prod.avg_rating), expected_avg, places=2)
        self.assertEqual(prod.total_ratings, 3)

    def test_product_detail_average_rating_annotation(self):
        Comment.objects.create(product=self.product, user=self.user, rating=4)
        Comment.objects.create(
            product=self.product,
            guest_name="Guest",
            guest_email="g@example.com",
            rating=2,
        )
        expected_avg = (4 + 2) / 2
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        prod = resp.context["product"]
        self.assertAlmostEqual(float(prod.avg_rating), expected_avg, places=2)
        self.assertEqual(prod.total_ratings, 2)

    def test_related_products_ordering_by_rating_and_count(self):
        # Base product gets moderate average (reference)
        Comment.objects.create(product=self.product, user=self.user, rating=5, text="Top")
        Comment.objects.create(
            product=self.product,
            guest_name="G",
            guest_email="g@example.com",
            rating=4,
        )
        Comment.objects.create(
            product=self.product,
            guest_name="G2",
            guest_email="g2@example.com",
            rating=5,
        )  # avg ~4.67 (3 ratings)
        # Two related products in same category with varying ratings
        prod_c = Product.objects.create(name="Amber Rattle", price="7.00", category=self.category)
        prod_b = Product.objects.create(name="Red Rattle", price="5.00", category=self.category)
        # Amber Rattle: two 5-star ratings (avg 5, count 2)
        Comment.objects.create(product=prod_c, user=self.user, rating=5)
        Comment.objects.create(
            product=prod_c,
            guest_name="AC",
            guest_email="ac@example.com",
            rating=5,
        )
        # Red Rattle: single 5-star rating (avg 5, count 1)
        Comment.objects.create(product=prod_b, user=self.other, rating=5)

        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        related = list(resp.context["related_products"])
        # Expect Amber (higher total_ratings) before Red because avg tie at 5
        self.assertIn(prod_c, related)
        self.assertIn(prod_b, related)
        idx_c = related.index(prod_c)
        idx_b = related.index(prod_b)
        self.assertLess(idx_c, idx_b)

    def test_related_products_limit_max_eight(self):
        # create 10 products; list should still show at most 8 related
        for i in range(10):
            p = Product.objects.create(name=f"Extra {i}", price="1.00", category=self.category)
            Comment.objects.create(
                product=p,
                guest_name="X",
                guest_email=f"x{i}@ex.com",
                rating=5,
            )
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        related = list(resp.context["related_products"])
        self.assertLessEqual(len(related), 8)
