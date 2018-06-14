# MP-Shop | Attributes

## Installation

### Install using PIP:
```
pip install django-mp-shop-attrs
```

### Add attributes to settings.py:
```
INSTALLED_APPS = [
    ...
    'attributes',
]
```

### Add attributes to product admin:
```
from attributes.admin import ProductAdminMixin
from attributes.forms import ProductFormMixin

class ProductForm(ProductFormMixin, forms.ModelForm):
    ...

class ProductAdmin(ProductAdminMixin, ModelAdmin):

    form = ProductForm
    ...

```

### App requires this packages:
* django
* awesome-slugify

### App compatible with:
* django-modeltranslation
* django-mptt
* django-suit
