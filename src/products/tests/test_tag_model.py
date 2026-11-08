from django.core.exceptions import ValidationError
from django.test import TestCase

from btw_app.utils import log_execution
from products.models import Category, Product, Tag


class TagTestCase(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        """Provide the values that are shared by all test cases of this class."""
        cls.test_tag_name = "Organic"
        cls.test_other_tag_name = "Washable"
        cls.test_category = Category.objects.create(name="Test Category", slug="test-category")

    # SUCCESS TEST CASES
    @log_execution
    def test_successful_tag_creation(self) -> None:
        """A tag is created with a name, an automatic id and automatic timestamps."""
        tag = Tag.objects.create(name=self.test_tag_name)
        tag.full_clean()
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.first().name, self.test_tag_name)
        # Ensure the primary key is assigned by Django
        self.assertIsNotNone(tag.id)
        # Ensure the read-only timestamps are set automatically
        self.assertIsNotNone(tag.created_at)
        self.assertIsNotNone(tag.updated_at)

    @log_execution
    def test_tag_timestamps_are_read_only(self) -> None:
        """The timestamp fields are not editable and therefore never offered in a form."""
        created_at_field = Tag._meta.get_field("created_at")
        updated_at_field = Tag._meta.get_field("updated_at")
        self.assertFalse(created_at_field.editable)
        self.assertFalse(updated_at_field.editable)

    @log_execution
    def test_successful_tag_assignment_to_product(self) -> None:
        """Several tags can be assigned to a single product over the many-to-many relation."""
        product = Product.objects.create(name="Test Product", price="9.99", category=self.test_category)
        first_tag = Tag.objects.create(name=self.test_tag_name)
        second_tag = Tag.objects.create(name=self.test_other_tag_name)

        product.tags.set([first_tag, second_tag])

        self.assertEqual(product.tags.count(), 2)
        self.assertIn(first_tag, product.tags.all())
        self.assertIn(second_tag, product.tags.all())
        # Ensure the relation can also be followed in the other direction
        self.assertIn(product, first_tag.products.all())

    @log_execution
    def test_successful_product_creation_without_tags(self) -> None:
        """Tags are optional, so a product without any tags is valid."""
        product = Product.objects.create(name="Untagged Product", price="4.99", category=self.test_category)
        product.full_clean()
        self.assertEqual(product.tags.count(), 0)

    @log_execution
    def test_tag_string_representation(self) -> None:
        """The string representation of a tag is its name."""
        tag = Tag.objects.create(name=self.test_tag_name)
        self.assertEqual(str(tag), self.test_tag_name)

    # FAILURE TEST CASES
    @log_execution
    def test_failure_tag_creation_without_name(self) -> None:
        """A tag without a name is rejected by the validation."""
        with self.assertRaises(ValidationError) as ctx:
            tag = Tag()
            tag.full_clean()  # Validate before saving
            tag.save()

        self.assertEqual(ctx.exception.message_dict, {"name": ["This field cannot be blank."]})
        self.assertEqual(Tag.objects.count(), 0)

    @log_execution
    def test_failure_tag_creation_with_duplicate_name(self) -> None:
        """A second tag with an already existing name is rejected by the validation."""
        Tag.objects.create(name=self.test_tag_name)
        with self.assertRaises(ValidationError) as ctx:
            duplicate_tag = Tag(name=self.test_tag_name)
            duplicate_tag.full_clean()
            duplicate_tag.save()

        self.assertEqual(ctx.exception.message_dict, {"name": ["Tag with this Name already exists."]})
        # Ensure only the first tag exists
        self.assertEqual(Tag.objects.count(), 1)

    @log_execution
    def test_failure_tag_creation_with_too_long_name(self) -> None:
        """A tag name longer than 50 characters is rejected by the validation."""
        long_name = "a" * 51
        with self.assertRaises(ValidationError) as ctx:
            tag = Tag(name=long_name)
            tag.full_clean()
            tag.save()

        self.assertEqual(
            ctx.exception.message_dict, {"name": ["Ensure this value has at most 50 characters (it has 51)."]}
        )
        self.assertEqual(Tag.objects.count(), 0)
