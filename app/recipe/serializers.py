"""Serializers for recipe API"""

from rest_framework import serializers

from core.models import (
    Recipe,
    Tag,
    )


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,

            )
            recipe.tags.add(tag_obj)


    def create_recipe(self, validate_data):
        """Create a recipe"""
        tags = validate_data.pop('tags', [])
        recipe = Recipe.objects.create(**validate_data)
        self._get_or_create_tags(tags, recipe)

    def update_recipe(self, instance, validate_data):
        """Update Recipe."""
        tags = validate_data.pop('tags', None)
        if tags is not None:
            instance.tag.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validate_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
