
from importlib import import_module

from django.apps import apps
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ordered_model.admin import OrderedModelAdmin

from attributes.admin.forms import ProductAttrForm, ProductAttrOptionInline
from attributes.models import ProductAttr


def _get_product_attr_admin_base_class():

    if apps.is_installed('modeltranslation'):
        return import_module('modeltranslation.admin').TranslationAdmin

    return admin.ModelAdmin


class ProductAttrAdmin(
        OrderedModelAdmin, _get_product_attr_admin_base_class()):

    form = ProductAttrForm
    inlines = [ProductAttrOptionInline]

    list_display = [
        'name', 'get_category_list', 'slug', 'get_type', 'is_required',
        'is_visible', 'is_filter', 'move_up_down_links']
    search_fields = ['name', 'slug']
    list_filter = ['categories', 'type', 'is_required']
    filter_horizontal = ['categories']

    def get_category_list(self, item):
        return ', '.join([c.name for c in item.categories.all()])

    get_category_list.short_description = _('Product categories')

    def get_type(self, item):
        return item.get_type_display()

    get_type.short_description = _('Type')


class ProductAdminMixin(object):

    """
    Workaround of django admin form dynamically loaded fields bug.
    Dynamically loaded fields should be registered in ModelAdmin.fields attr.
    """
    def render_change_form(self, request, context, **kwargs):

        form = context['adminform'].form

        fieldsets = self.fieldsets or [(None, {'fields': form.fields.keys()})]

        context['adminform'] = admin.helpers.AdminForm(
            form, fieldsets, self.prepopulated_fields, model_admin=self)

        return super(ProductAdminMixin, self).render_change_form(
            request, context, **kwargs)


admin.site.register(ProductAttr, ProductAttrAdmin)
