
from importlib import import_module
from copy import deepcopy

from django.apps import apps
from django import forms
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.functional import cached_property

from slugify import slugify_url

from attributes.constants import ATTR_TYPE_SELECT
from attributes.models import ProductAttr, ProductAttrOption, VALUE_FIELDS


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


class ProductFormMixin(object):

    def __init__(self, *args, **kwargs):

        super(ProductFormMixin, self).__init__(*args, **kwargs)

        self._is_attr_fields_initialized = False

        if self.instance.pk:
            self._build_attr_fields()

    def clean(self):
        data = self.cleaned_data

        if not self._is_attr_fields_initialized:
            return data

        for attr in self._attributes:

            if attr.has_options:
                new_option = data.get(self._get_option_field_name(attr))

                if new_option:
                    option, c = attr.options.get_or_create(name=new_option)
                    data[attr.full_slug] = option

                if not data.get(attr.full_slug) and attr.is_required:
                    raise ValidationError({
                        attr.full_slug: _('{} is required').format(attr.name)
                    })

        return data

    def save(self, commit=True):

        product = super(ProductFormMixin, self).save(commit)

        if self._is_attr_fields_initialized:

            if 'category' in self.changed_data:
                product.attr_values.all().delete()

            for attr in self._attributes:

                if attr.full_slug in self.cleaned_data:
                    value = self.cleaned_data[attr.full_slug]
                    attr.save_value(self.instance, value)

        return product

    def _build_attr_fields(self):

        fields = self.fields = deepcopy(self.base_fields)

        for attr in self._attributes:

            fields[attr.full_slug] = self._build_attr_field(attr)

            if attr.has_options:
                label = attr.name + unicode(_(' [New value]'))
                fields[self._get_option_field_name(attr)] = forms.CharField(
                    label=label, required=False)

            try:
                value = self.instance.attr_values.get(attr=attr).value
            except ObjectDoesNotExist:
                pass
            else:
                self.initial[attr.full_slug] = value

        self._is_attr_fields_initialized = True

    def _build_attr_field(self, attr):

        if attr.has_options:
            label = attr.name

            if attr.is_required:
                label += ' *'

            kwargs = {'label': label, 'required': False}
        else:
            kwargs = {'label': attr.name, 'required': attr.is_required}

        if attr.type is ATTR_TYPE_SELECT:
            kwargs['queryset'] = attr.options.all()
            return forms.ModelChoiceField(**kwargs)

        return VALUE_FIELDS[attr.type].formfield(**kwargs)

    @cached_property
    def _attributes(self):
        return list(
            ProductAttr.objects.for_categories([self.instance.category]))

    def _get_option_field_name(self, attr):
        return 'option_' + attr.full_slug