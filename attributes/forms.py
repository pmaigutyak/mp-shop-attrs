
from django import forms

from attributes.models import ProductAttrValue, ProductAttrOption


class FilterProductAttrForm(forms.Form):

    def __init__(self, attributes, *args, **kwargs):

        self._attributes = attributes

        super(FilterProductAttrForm, self).__init__(*args, **kwargs)

        for attr in self._attributes:
            self.fields[attr.full_slug] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple, label=attr.name,
                required=False)

    def set_options(self, products):

        choices = {attr.id: [] for attr in self._attributes}

        attr_values = ProductAttrValue.objects.filter(
            attribute__in=self._attributes, product__in=products)

        options = ProductAttrOption.objects.filter(
            attr__values__in=attr_values)

        for option in options:
            choices[option.attr_id].append(option)

        for attr in self._attributes:
            self.fields[attr.full_slug].choices = choices[attr.id]

    def _get_available_options(self):

        added_options = []

        options = {attr.pk: [] for attr in self._attributes}

        attr_values = ProductAttrValue.objects.filter(
            attribute__in=self._attributes, product__in=self._products
        ).select_related('value_option')

        for value in attr_values:

            option = value.value_option

            if option not in added_options:
                added_options.append(option)
                options[value.attribute_id].append(option)

        return options
