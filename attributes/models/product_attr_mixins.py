
from django.db import models
from django.utils.translation import ugettext_lazy as _

from attributes.models import ProductAttr, ProductAttrService


class ProductCategoryAttrMixin(object):

    def get_attributes(self):
        return ProductAttr.objects.filter(categories__in=[self])


class ProductAttrMixin(object):

    attributes = models.ManyToManyField(
        'attributes.ProductAttr', through='ProductAttrValue',
        verbose_name=_("Attributes"))

    def __init__(self, *args, **kwargs):

        super(ProductAttrMixin, self).__init__(*args, **kwargs)

        self.attr = ProductAttrService(self)

    def save(self, *args, **kwargs):

        is_new = bool(not self.pk)

        super(ProductAttrMixin, self).save(*args, **kwargs)

        if not is_new:
            self.attr.save()