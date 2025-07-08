"""
Tests for the Ingredients API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Ingredient, Recipe)

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create(email=email, password=password)


class PublicIngredientApiTests(TestCase):
    """Test unauthenticated Ingredient API."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication required to retrieve ingredient"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test authenticated Ingredient API features."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Dhaniya')
        Ingredient.objects.create(user=self.user, name='Chilly')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test list of ingredient is limited to specific user."""
        user2 = create_user(email='user2@example.com', password='user2pass')

        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        Ingredient.objects.create(user=user2, name='Ginger')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Sugar')
        payload = {'name': 'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Clove')
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.all().filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test lisiting ingredients by those assigned to recipes."""
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=15,
            price=Decimal('5.99'),
            user=self.user,

        )
        recipe.ingredients.add(in1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""

        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = Recipe.objects.create(
            title='Egg Benedict',
            time_minutes=30,
            price=Decimal('7.99'),
            user=self.user,

        )

        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=10,
            price=Decimal('2.99'),
            user=self.user,
        )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
