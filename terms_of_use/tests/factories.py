from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyText

from ..models import TermsOfUse


class TermsOfUseFactory(DjangoModelFactory):
    class Meta:
        model = "terms_of_use.TermsOfUse"

    name = FuzzyText()
    text = FuzzyText()
    terms_type = FuzzyChoice([terms_type for terms_type, _ in TermsOfUse.TERMS_TYPES])
