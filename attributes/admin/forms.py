
from importlib import import_module

from django.apps import apps
from django import forms
from django.contrib import admin
from django.conf import settings

from slugify import slugify_url

from attributes.models import ProductAttr, ProductAttrOption


def _get_attr_option_inline_base_class():

    if apps.is_installed('modeltranslation'):
        return import_module('modeltranslation.admin').TranslationTabularInline

    return admin.TabularInline


class ProductAttrOptionInline(_get_attr_option_inline_base_class()):

    model = ProductAttrOption
    extra = 0


class ProductAttrForm(forms.ModelForm):

    def clean_slug(self):

        data = self.cleaned_data

        if data.get('slug'):
            return data['slug']

        if apps.is_installed('modeltranslation'):
            name = data.get('name_{}'.format(settings.LANGUAGE_CODE))
        else:
            name = data.get('name')

        return slugify_url(name, separator='_')

    class Meta:
        model = ProductAttr
        fields = [
            'categories', 'name', 'slug', 'type', 'is_required', 'is_visible',
            'is_filter'
        ]
