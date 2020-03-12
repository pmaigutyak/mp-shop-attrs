
from copy import deepcopy

from django import forms
from django.utils.translation import ugettext
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.functional import cached_property

from attributes.constants import ATTR_TYPE_SELECT
from attributes.models import (
    Attribute,
    AttributeValue,
    AttributeOption,
    VALUE_FIELDS)


class FilterAttributeForm(forms.Form):

    def __init__(self, attributes, *args, **kwargs):

        self._attributes = attributes

        super(FilterAttributeForm, self).__init__(*args, **kwargs)

        for attr in self._attributes:
            self.fields[attr.full_slug] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple, label=attr.name,
                required=False)

    def set_options(self, entries):

        if not entries:
            self.fields = {}
            return

        choices = {attr.id: [] for attr in self._attributes}

        attr_values = AttributeValue.objects.filter(
            attr__in=self._attributes, entry__in=entries
        ).values_list('id', flat=True)

        options = AttributeOption.objects.filter(
            attr_values__in=attr_values).order_by('name').distinct()

        for option in options:
            choices[option.attr_id].append((option.id, option, ))

        for attr in self._attributes:
            if choices[attr.id]:
                self.fields[attr.full_slug].choices = choices[attr.id]
            else:
                del self.fields[attr.full_slug]

    def get_value_ids(self):
        ids = []

        for attr in self._attributes:
            ids += self.data.getlist(attr.full_slug)

        return ids

    def _get_available_options(self):

        added_options = []

        options = {attr.pk: [] for attr in self._attributes}

        attr_values = AttributeValue.objects.filter(
            attribute__in=self._attributes, entry__in=self._entries
        ).select_related('value_option')

        for value in attr_values:

            option = value.value_option

            if option not in added_options:
                added_options.append(option)
                options[value.attribute_id].append(option)

        return options


class EntryFormMixin(object):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

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
                        attr.full_slug: ugettext('{} is required').format(
                            attr.name)
                    })

        return data

    def save(self, commit=True):

        entry = super().save(commit)

        if self._is_attr_fields_initialized:

            if 'category' in self.changed_data:
                entry.attr_values.all().delete()

            for attr in self._attributes:

                if attr.full_slug in self.cleaned_data:
                    value = self.cleaned_data[attr.full_slug]
                    attr.save_value(self.instance, value)

        return entry

    def _build_attr_fields(self):

        fields = self.fields = deepcopy(self.base_fields)

        for attr in self._attributes:

            fields[attr.full_slug] = self._build_attr_field(attr)

            if attr.has_options:
                label = attr.name + ugettext(' [New value]')
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
        return list(Attribute.objects.for_categories([self.instance.category]))

    def _get_option_field_name(self, attr):
        return 'option_' + attr.full_slug
