from modeltranslation.translator import TranslationOptions, translator

from .models import (
    Equipment,
    EquipmentCategory,
    Keyword,
    KeywordCategory,
    KeywordGroup,
    Period,
    Purpose,
    ReservationUnit,
    ReservationUnitCancellationRule,
    ReservationUnitType,
)


class ReservationUnitTranslationOptions(TranslationOptions):
    fields = [
        "name",
        "description",
        "terms_of_use",
        "contact_information",
        "additional_instructions",
    ]


class ReservationUnitTypeTranslationOptions(TranslationOptions):
    fields = ["name"]


class KeywordCategoryTranslationOptions(TranslationOptions):
    fields = ["name"]


class KeywordGroupTranslationOptions(TranslationOptions):
    fields = ["name"]


class KeywordTranslationOptions(TranslationOptions):
    fields = ["name"]


class PurposeTranslationOptions(TranslationOptions):
    fields = ["name"]


class PeriodTranslationOptions(TranslationOptions):
    fields = ["name", "description"]


class EquipmentTranslationOptions(TranslationOptions):
    fields = ["name"]


class EquipmentCategoryTranslationOptions(TranslationOptions):
    fields = ["name"]


class ReservationUnitCancellationRuleTranslationOptions(TranslationOptions):
    fields = ["name"]


translator.register(ReservationUnit, ReservationUnitTranslationOptions)
translator.register(ReservationUnitType, ReservationUnitTypeTranslationOptions)
translator.register(KeywordCategory, KeywordCategoryTranslationOptions)
translator.register(KeywordGroup, KeywordGroupTranslationOptions)
translator.register(Keyword, KeywordTranslationOptions)
translator.register(Purpose, PurposeTranslationOptions)
translator.register(Period, PeriodTranslationOptions)
translator.register(Equipment, EquipmentTranslationOptions)
translator.register(EquipmentCategory, EquipmentCategoryTranslationOptions)
translator.register(
    ReservationUnitCancellationRule, ReservationUnitCancellationRuleTranslationOptions
)
