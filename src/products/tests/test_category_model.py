from django.core.exceptions import ValidationError
from django.test import TestCase

from btw_app.utils import log_execution
from products.models import Category


class CategoryTestCase(TestCase):

    @classmethod
    def setUpTestData(self):
        self.test_category_name = "Test Category"
        self.test_category_slug = "test-category"
        self.test_category_description = "This is a test category description."

    # SUCCESS TEST CASES
    @log_execution
    def test_successful_category_creation_without_description(self):
        # Test the creation of a category
        category = Category.objects.create(name=self.test_category_name, slug=self.test_category_slug)
        category.full_clean()
        self.assertEqual(Category.objects.count(), 1)
        # Ensure name is unique
        self.assertTrue(Category.objects.filter(name=self.test_category_name).exists())
        # Ensure slug is unique
        self.assertTrue(Category.objects.filter(slug=self.test_category_slug).exists())
        self.assertEqual(Category.objects.first().name, self.test_category_name)
        # Ensure description is None
        self.assertIsNone(Category.objects.first().description)
        # Ensure created_at is set
        self.assertIsNotNone(Category.objects.first().created_at)
        # Ensure updated_at is set
        self.assertIsNotNone(Category.objects.first().updated_at)

    @log_execution
    def test_successful_category_creation_with_description(self):
        # Test the creation of a category with a description
        category = Category.objects.create(
            name=self.test_category_name, description=self.test_category_description, slug=self.test_category_slug
        )
        category.full_clean()
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.first().description, self.test_category_description)
        # Ensure name is unique
        self.assertTrue(Category.objects.filter(name=self.test_category_name).exists())
        # Ensure slug is unique
        self.assertTrue(Category.objects.filter(slug=self.test_category_slug).exists())

    # FAILURE TEST CASES
    @log_execution
    def test_failure_category_creation_without_name(self):
        # Test the failure of category creation without a name
        with self.assertRaises(ValidationError) as ctx:
            category = Category(slug=self.test_category_slug)
            category.full_clean()  # Validate before saving
            category.save()

        self.assertEqual(ctx.exception.message_dict, {"name": ["This field cannot be blank."]})
        self.assertEqual(Category.objects.count(), 0)

    @log_execution
    def test_failure_category_creation_without_slug(self):
        # Test the failure of category creation without a slug
        with self.assertRaises(ValidationError) as ctx:
            category = Category(name=self.test_category_name)
            category.full_clean()  # Validate before saving
            category.save()

        self.assertEqual(ctx.exception.message_dict, {"slug": ["This field cannot be blank."]})
        self.assertEqual(Category.objects.count(), 0)

    @log_execution
    def test_failure_category_creation_with_duplicate_name(self):
        Category.objects.create(name=self.test_category_name, slug=self.test_category_slug)
        with self.assertRaises(ValidationError) as ctx:
            duplicate_category = Category(name=self.test_category_name, slug="unique-slug")
            duplicate_category.full_clean()
            duplicate_category.save()
        # Ensure only one category exists
        self.assertEqual(ctx.exception.message_dict, {"name": ["Category with this Name already exists."]})
        self.assertEqual(Category.objects.count(), 1)

    @log_execution
    def test_failure_category_creation_with_too_long_name(self):
        long_name = "a" * 51
        with self.assertRaises(ValidationError) as ctx:
            category = Category(name=long_name, slug=self.test_category_slug)
            category.full_clean()
            category.save()
        # Ensure no categories were created
        self.assertEqual(
            ctx.exception.message_dict, {"name": ["Ensure this value has at most 50 characters (it has 51)."]}
        )
        self.assertEqual(Category.objects.count(), 0)

    @log_execution
    def test_failure_category_creation_with_too_long_slug(self):
        long_slug = "a" * 51
        with self.assertRaises(ValidationError) as ctx:
            category = Category(name=self.test_category_name, slug=long_slug)
            category.full_clean()
            category.save()
        # Ensure no categories were created
        self.assertEqual(
            ctx.exception.message_dict, {"slug": ["Ensure this value has at most 50 characters (it has 51)."]}
        )
        self.assertEqual(Category.objects.count(), 0)

    @log_execution
    def test_failure_category_creation_with_duplicate_slug(self):
        Category.objects.create(name=self.test_category_name, slug=self.test_category_slug)
        with self.assertRaises(ValidationError) as ctx:
            duplicate_category = Category(name="Unique Name", slug=self.test_category_slug)
            duplicate_category.full_clean()
            duplicate_category.save()
        # Ensure only one category exists
        self.assertEqual(ctx.exception.message_dict, {"slug": ["Category with this Slug already exists."]})
        self.assertEqual(Category.objects.count(), 1)

    @log_execution
    def test_category_string_representation(self):
        category = Category.objects.create(name=self.test_category_name, slug=self.test_category_slug)
        # Ensure __str__ method works correctly
        self.assertEqual(str(category), self.test_category_name)
        self.assertEqual(str(category), self.test_category_name)
