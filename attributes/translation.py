
from modeltranslation.translator import translator, TranslationOptions

from attributes.models import ProductAttr, ProductAttrOption


class ProductAttrTranslationOptions(TranslationOptions):

    fields = ('name', )


class ProductAttrOptionTranslationOptions(TranslationOptions):

    fields = ('name', )


translator.register(ProductAttr, ProductAttrTranslationOptions)
translator.register(ProductAttrOption, ProductAttrOptionTranslationOptions)
