
from importlib import import_module
from copy import deepcopy

from django.apps import apps
from django import forms
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from slugify import slugify_url

from attributes.constants import ATTR_TYPE_SELECT
from attributes.models import ProductAttr, ProductAttrOption, VALUE_FIELDS


def _get_attr_option_inline_base_class():

    if apps.is_installed('modeltranslation'):
        return import_module('modeltranslation.admin').TranslationTabularInline

    return admin.TabularInline


class ProductAttrOptionInline():

    model = ProductAttrOption
    extra = 0


class ProductAttrForm(forms.ModelForm):

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')

        if slug:
            return slug

        name = self.cleaned_data.get('name_%s' % settings.LANGUAGE_CODE)
        return slugify_url(name, separator='_')

    class Meta:
        model = ProductAttr
        fields = '__all__'


class ProductFormMixin(object):

    def __init__(self, *args, **kwargs):

        super(ProductFormMixin, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self._build_attr_fields()

    def get_option_field_name(self, attr):
        return 'option_' + attr.full_slug

    def clean(self):
        data = self.cleaned_data

        for attr in self.instance.attr.all():

            if attr.has_options:
                new_option = data.get(self.get_option_field_name(attr))

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

        if 'category' in self.changed_data:
            product.attr_values.all().delete()

        return product

    def _build_attr_fields(self):

        fields = self.fields = deepcopy(self.base_fields)

        for attr in self.instance.attr.all():

            fields[attr.full_slug] = self._build_attr_field(attr)

            if attr.has_options:
                label = attr.name + unicode(_(' [New value]'))
                fields[self.get_option_field_name(attr)] = forms.CharField(
                    label=label, required=False)

            try:
                value = self.instance.attr_values.get(attr=attr).value
            except ObjectDoesNotExist:
                pass
            else:
                self.initial[attr.full_slug] = value

    def _post_clean(self):

        for attr in self.instance.attr.all():

            if attr.full_slug in self.cleaned_data:
                value = self.cleaned_data[attr.full_slug]
                setattr(self.instance.attr, attr.slug, value)

        super(ProductFormMixin, self)._post_clean()

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