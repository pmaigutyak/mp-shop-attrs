
from attributes.models import ProductAttr


class ProductCategoryAttrMixin(object):

    def get_attributes(self):
        return ProductAttr.objects.filter(categories__in=[self])
