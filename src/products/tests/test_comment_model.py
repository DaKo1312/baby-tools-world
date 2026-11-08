from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from btw_app.utils import log_execution
from products.models import Category, Comment, Product

User = get_user_model()


class CommentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Base fixtures
        cls.category = Category.objects.create(name="Test Category", slug="test-category")
        cls.product = Product.objects.create(
            name="Test Product",
            price="19.99",
            category=cls.category,
        )
        cls.user = User.objects.create_user(username="tester", email="tester@example.com", password="pass1234")
        cls.text_content = "This is a test comment."
        cls.valid_rating = 5

    # SUCCESS TESTS
    @log_execution
    def test_successful_comment_creation_minimal(self):
        comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            rating=self.valid_rating,
        )
        comment.full_clean()
        self.assertEqual(Comment.objects.count(), 1)
        stored = Comment.objects.first()
        self.assertEqual(stored.product, self.product)
        self.assertEqual(stored.user, self.user)
        self.assertEqual(stored.rating, self.valid_rating)
        self.assertEqual(stored.text, "")  # text is optional and defaults to empty
        self.assertIsNotNone(stored.created_at)
        self.assertIsNotNone(stored.updated_at)

    @log_execution
    def test_successful_comment_creation_with_text(self):
        comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            text=self.text_content,
            rating=self.valid_rating,
        )
        comment.full_clean()
        self.assertEqual(Comment.objects.count(), 1)
        stored = Comment.objects.first()
        self.assertEqual(stored.text, self.text_content)
        self.assertEqual(stored.rating, self.valid_rating)

    @log_execution
    def test_successful_guest_comment_creation(self):
        comment = Comment.objects.create(
            product=self.product,
            guest_name="Guest User",
            guest_email="guest@example.com",
            text=self.text_content,
            rating=self.valid_rating,
        )
        comment.full_clean()
        self.assertEqual(Comment.objects.count(), 1)
        stored = Comment.objects.first()
        self.assertEqual(stored.guest_name, "Guest User")
        self.assertEqual(stored.guest_email, "guest@example.com")
        self.assertIsNone(stored.user)

    # FAILURE TESTS
    @log_execution
    def test_failure_comment_creation_without_product(self):
        with self.assertRaises(ValidationError) as ctx:
            comment = Comment(
                user=self.user,
                text=self.text_content,
                rating=self.valid_rating,
            )
            comment.full_clean()
            comment.save()
        self.assertEqual(ctx.exception.message_dict, {"product": ["This field cannot be null."]})
        self.assertEqual(Comment.objects.count(), 0)

    @log_execution
    def test_failure_comment_creation_without_rating(self):
        with self.assertRaises(ValidationError) as ctx:
            comment = Comment(
                product=self.product,
                user=self.user,
                text=self.text_content,
            )
            comment.full_clean()
            comment.save()
        self.assertEqual(ctx.exception.message_dict, {"rating": ["This field cannot be null."]})
        self.assertEqual(Comment.objects.count(), 0)

    @log_execution
    def test_failure_comment_creation_with_invalid_rating_low(self):
        with self.assertRaises(ValidationError) as ctx:
            comment = Comment(
                product=self.product,
                user=self.user,
                text=self.text_content,
                rating=0,  # min is 1
            )
            comment.full_clean()
        self.assertEqual(ctx.exception.message_dict, {"rating": ["Ensure this value is greater than or equal to 1."]})
        self.assertEqual(Comment.objects.count(), 0)

    @log_execution
    def test_failure_comment_creation_with_invalid_rating_high(self):
        with self.assertRaises(ValidationError) as ctx:
            comment = Comment(
                product=self.product,
                user=self.user,
                text=self.text_content,
                rating=6,  # max is 5
            )
            comment.full_clean()
        self.assertEqual(ctx.exception.message_dict, {"rating": ["Ensure this value is less than or equal to 5."]})
        self.assertEqual(Comment.objects.count(), 0)

    @log_execution
    def test_failure_duplicate_user_product_comment(self):
        # First comment should succeed
        Comment.objects.create(
            product=self.product,
            user=self.user,
            rating=self.valid_rating,
        )
        self.assertEqual(Comment.objects.count(), 1)

        # Second comment from same user for same product should fail
        with self.assertRaises(ValidationError) as ctx:
            comment = Comment(
                product=self.product,
                user=self.user,
                rating=4,
            )
            comment.full_clean()
            comment.save()
        self.assertEqual(
            ctx.exception.message_dict, {"__all__": ["Constraint “unique_user_product_comment” is violated."]}
        )
        self.assertEqual(Comment.objects.count(), 1)

    @log_execution
    def test_comment_string_representation_with_user(self):
        comment = Comment.objects.create(
            product=self.product,
            user=self.user,
            text=self.text_content,
            rating=self.valid_rating,
        )
        # Based on actual __str__ method: f"{who} - {self.rating}★"
        expected_str = f"{self.user.username} - {self.valid_rating}★"
        self.assertEqual(str(comment), expected_str)

    @log_execution
    def test_comment_string_representation_with_guest(self):
        guest_name = "Guest User"
        comment = Comment.objects.create(
            product=self.product,
            guest_name=guest_name,
            rating=self.valid_rating,
        )
        expected_str = f"{guest_name} - {self.valid_rating}★"
        self.assertEqual(str(comment), expected_str)

    @log_execution
    def test_comment_string_representation_anonymous_guest(self):
        comment = Comment.objects.create(
            product=self.product,
            rating=self.valid_rating,
        )
        expected_str = f"Guest - {self.valid_rating}★"
        self.assertEqual(str(comment), expected_str)
