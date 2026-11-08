from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from btw_app.utils import log_execution
from products.models import Category, Product


class ProductTestCase(TestCase):

    @classmethod
    def setUpTestData(self):
        self.test_category = Category.objects.create(name="Test Category", slug="test-category")
        self.test_product_name = "Test Product"
        self.test_product_description = "This is a test product description."
        self.test_product_price = Decimal("19.99")

    @log_execution
    def test_successful_product_creation(self):
        # Test the creation of a product
        product = Product.objects.create(
            name=self.test_product_name,
            description=self.test_product_description,
            price=self.test_product_price,
            category=self.test_category,
        )
        product.full_clean()
        self.assertEqual(Product.objects.count(), 1)
        # check if product attributes are set correctly
        self.assertEqual(Product.objects.first().name, self.test_product_name)
        self.assertEqual(Product.objects.first().description, self.test_product_description)
        self.assertEqual(Product.objects.first().price, self.test_product_price)
        self.assertEqual(Product.objects.first().category, self.test_category)
        # Ensure created_at, updated_at are set
        self.assertIsNotNone(Product.objects.first().created_at)
        self.assertIsNotNone(Product.objects.first().updated_at)

    @log_execution
    def test_product_category_relationship(self):
        # Test the relationship between product and category
        product = Product.objects.create(
            name=self.test_product_name, price=self.test_product_price, category=self.test_category
        )
        product.full_clean()
        self.assertEqual(product.category.name, self.test_category.name)
        self.assertTrue(Category.objects.filter(name=product.category.name).exists())

    @log_execution
    def test_failure_product_creation_without_name(self):
        # Test the failure of product creation without a name
        with self.assertRaises(ValidationError) as ctx:
            product = Product(
                description=self.test_product_description, price=self.test_product_price, category=self.test_category
            )
            product.full_clean()
            product.save()
        self.assertEqual(ctx.exception.message_dict, {"name": ["This field cannot be blank."]})
        self.assertEqual(Product.objects.count(), 0)

    @log_execution
    def test_failure_product_creation_without_price(self):
        # Test the failure of product creation without a price
        with self.assertRaises(ValidationError) as ctx:
            product = Product(
                name=self.test_product_name, description=self.test_product_description, category=self.test_category
            )
            product.full_clean()
            product.save()
        self.assertEqual(ctx.exception.message_dict, {"price": ["This field cannot be null."]})
        self.assertEqual(Product.objects.count(), 0)

    @log_execution
    def test_failure_product_creation_with_invalid_price(self):
        # Test the failure of product creation with an invalid price
        with self.assertRaises(ValidationError) as ctx:
            product = Product(
                name=self.test_product_name,
                description=self.test_product_description,
                price=-10.00,  # Invalid price
                category=self.test_category,
            )
            product.full_clean()
            product.save()
        self.assertEqual(ctx.exception.message_dict, {"price": ["Ensure this value is greater than or equal to 0.00."]})
        self.assertEqual(Product.objects.count(), 0)

    @log_execution
    def test_failure_product_creation_with_too_high_price(self):
        # Test the failure of product creation
        # with a price exceeding max_digits
        with self.assertRaises(ValidationError) as ctx:
            product = Product(
                name=self.test_product_name,
                description=self.test_product_description,
                price=Decimal("1000000.00"),  # Exceeds max_digits
                category=self.test_category,
            )
            product.full_clean()
            product.save()
        self.assertEqual(
            ctx.exception.message_dict, {"price": ["Ensure that there are no more than 6 digits in total."]}
        )
        self.assertEqual(Product.objects.count(), 0)

    @log_execution
    def test_product_string_representation(self):
        # Test the string representation of a product
        product = Product.objects.create(
            name=self.test_product_name, price=self.test_product_price, category=self.test_category
        )
        self.assertEqual(str(product), self.test_product_name)
        self.assertEqual(str(product), self.test_product_name)
