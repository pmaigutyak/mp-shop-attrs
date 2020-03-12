
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ordered_model.models import (
    OrderedModel,
    OrderedModelManager,
    OrderedModelQuerySet)

from attributes.models.attribute_value import AttributeValue
from attributes.settings import ATTRIBUTES_CATEGORY_MODEL
from attributes.constants import ATTR_TYPE_TEXT, ATTR_TYPE_SELECT, ATTR_TYPES


class AttributeQuerySet(OrderedModelQuerySet):

    def visible(self):
        return self.filter(is_visible=True)

    def for_filter(self):
        return self.filter(type=ATTR_TYPE_SELECT, is_filter=True)

    def for_categories(self, categories):
        return self.filter(categories__in=categories)


class AttributeManager(OrderedModelManager):

    def get_queryset(self):
        return AttributeQuerySet(self.model, using=self._db)

    def visible(self):
        return self.get_queryset().visible()

    def for_filter(self):
        return self.get_queryset().for_filter()

    def for_categories(self, categories):
        return self.get_queryset().for_categories(categories)


class Attribute(OrderedModel):

    categories = models.ManyToManyField(
        ATTRIBUTES_CATEGORY_MODEL,
        related_name='attributes',
        blank=True,
        verbose_name=_("Categories"))

    name = models.CharField(
        _('Name'),
        max_length=128)

    slug = models.CharField(
        _('Code'),
        max_length=255,
        db_index=True,
        blank=True,
        null=False)

    type = models.PositiveSmallIntegerField(
        choices=ATTR_TYPES,
        default=ATTR_TYPE_TEXT,
        null=False,
        verbose_name=_("Type"))

    is_required = models.BooleanField(
        _('Required'),
        default=False,
        help_text=_('You will not be able to update record without filling '
                    'this field'))

    is_visible = models.BooleanField(
        _('Is visible'),
        default=True,
        help_text=_('Display this attribute for users'))

    is_filter = models.BooleanField(
        _('Is filter'),
        default=False,
        help_text=_('Display this attribute in records filter'))

    objects = AttributeManager()

    @property
    def has_options(self):
        return self.type == ATTR_TYPE_SELECT

    @property
    def full_slug(self):
        return 'attr_' + self.slug

    def __str__(self):
        return self.name

    def save_value(self, entry, value):

        try:
            val_obj = AttributeValue.objects.get(entry=entry, attr=self)

            if not value:
                val_obj.delete()
                return None

            val_obj.value = value
            val_obj.save()

            return val_obj

        except AttributeValue.DoesNotExist:

            if not value:
                return None

            val_obj = AttributeValue(entry=entry, attr=self)
            val_obj.value = value
            val_obj.save()

            return val_obj

    class Meta:
        ordering = ['order']
        verbose_name = _('Attribute')
        verbose_name_plural = _('Attributes')
