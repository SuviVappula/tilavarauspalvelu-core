# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['ReservationUnitQueryTestCase::test_filtering_by_active_application_rounds 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'applicationRounds': [
                            {
                                'nameFi': 'Test Round'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_is_draft_false 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'isDraft': False,
                        'nameFi': 'test name fi'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_is_draft_true 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'isDraft': True,
                        'nameFi': 'Draft reservation unit'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_is_visible_false 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_is_visible_true 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'publishBegins': '2021-05-03T00:00:00+00:00',
                        'publishEnds': '2021-05-10T00:00:00+00:00'
                    }
                },
                {
                    'node': {
                        'nameFi': 'show me',
                        'publishBegins': None,
                        'publishEnds': None
                    }
                },
                {
                    'node': {
                        'nameFi': 'show me too!',
                        'publishBegins': '2021-04-28T00:00:00+00:00',
                        'publishEnds': '2021-05-13T00:00:00+00:00'
                    }
                },
                {
                    'node': {
                        'nameFi': 'Take me in!',
                        'publishBegins': '2021-04-28T00:00:00+00:00',
                        'publishEnds': None
                    }
                },
                {
                    'node': {
                        'nameFi': 'Take me in too!',
                        'publishBegins': None,
                        'publishEnds': '2021-05-08T00:00:00+00:00'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_keyword_group 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'keywordGroups': [
                            {
                                'nameFi': 'Sports'
                            }
                        ],
                        'nameFi': 'test name fi'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_max_persons 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'maxPersons': 110,
                        'nameFi': 'test name fi'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_max_persons_not_found 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_multiple_keyword_groups 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'keywordGroups': [
                            {
                                'nameFi': 'Test group'
                            }
                        ],
                        'nameFi': 'test name fi'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_multiple_purposes 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'purposes': [
                            {
                                'nameFi': 'Test purpose'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_multiple_reservation_states 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservations': [
                            {
                                'begin': '2021-05-03T00:00:00+00:00',
                                'end': '2021-05-03T01:00:00+00:00',
                                'state': 'CREATED'
                            },
                            {
                                'begin': '2021-05-03T01:00:00+00:00',
                                'end': '2021-05-03T02:00:00+00:00',
                                'state': 'CONFIRMED'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_multiple_types 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservationUnitType': {
                            'nameFi': 'test type fi'
                        }
                    }
                },
                {
                    'node': {
                        'nameFi': 'Other reservation unit',
                        'reservationUnitType': {
                            'nameFi': 'Other type'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_multiple_units 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'unit': {
                            'nameFi': 'test unit fi'
                        }
                    }
                },
                {
                    'node': {
                        'nameFi': 'Other reservation unit',
                        'unit': {
                            'nameFi': 'Other unit'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_purpose 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'purposes': [
                            {
                                'nameFi': 'Test purpose'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_reservation_state 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservations': [
                            {
                                'begin': '2021-05-03T00:00:00+00:00',
                                'end': '2021-05-03T01:00:00+00:00',
                                'state': 'CREATED'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_reservation_timestamps 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservations': [
                            {
                                'begin': '2021-05-03T00:00:00+00:00',
                                'end': '2021-05-03T01:00:00+00:00',
                                'state': 'CREATED'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_type 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservationUnitType': {
                            'nameFi': 'test type fi'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_filtering_by_unit 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'unit': {
                            'nameFi': 'test unit fi'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_getting_hauki_url_is_none_when_regular_user 1'] = {
    'data': {
        'reservationUnitByPk': {
            'haukiUrl': {
                'url': None
            },
            'nameFi': 'test name fi'
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_getting_manually_given_surface_area 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'surfaceArea': '500.00'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_getting_reservation_units 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'additionalInstructionsEn': 'Additional instructions',
                        'additionalInstructionsFi': 'Lisäohjeita',
                        'additionalInstructionsSv': 'Ytterligare instruktioner',
                        'applicationRounds': [
                        ],
                        'bufferTimeAfter': 900,
                        'bufferTimeBefore': 900,
                        'cancellationRule': {
                            'nameEn': 'en',
                            'nameFi': 'fi',
                            'nameSv': 'sv'
                        },
                        'contactInformationFi': '',
                        'descriptionFi': '',
                        'equipment': [
                        ],
                        'highestPrice': '20.00',
                        'images': [
                        ],
                        'location': None,
                        'lowestPrice': '0.00',
                        'maxPersons': 110,
                        'maxReservationDuration': 86400,
                        'maxReservationsPerUser': 5,
                        'metadataSet': {
                            'name': 'Test form',
                            'requiredFields': [
                            ],
                            'supportedFields': [
                            ]
                        },
                        'minReservationDuration': 600,
                        'nameFi': 'test name fi',
                        'priceUnit': 'PER_HOUR',
                        'publishBegins': '2021-05-03T00:00:00+00:00',
                        'publishEnds': '2021-05-10T00:00:00+00:00',
                        'purposes': [
                        ],
                        'requireIntroduction': False,
                        'requireReservationHandling': False,
                        'reservationBegins': '2021-05-03T00:00:00+00:00',
                        'reservationEnds': '2021-05-03T00:00:00+00:00',
                        'reservationStartInterval': 'INTERVAL_30_MINS',
                        'reservationUnitType': {
                            'nameFi': 'test type fi'
                        },
                        'reservations': [
                        ],
                        'resources': [
                        ],
                        'services': [
                            {
                                'bufferTimeAfter': 1800,
                                'bufferTimeBefore': 900,
                                'nameFi': 'Test Service'
                            }
                        ],
                        'spaces': [
                            {
                                'nameFi': 'Large space'
                            },
                            {
                                'nameFi': 'Small space'
                            }
                        ],
                        'surfaceArea': '150.00',
                        'taxPercentage': {
                            'value': '24.00'
                        },
                        'termsOfUseFi': None
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_getting_terms 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'cancellationTerms': {
                            'textFi': 'Cancellation terms'
                        },
                        'paymentTerms': {
                            'textFi': 'Payment terms'
                        },
                        'serviceSpecificTerms': {
                            'textFi': 'Service-specific terms'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_hauki_url_for_admin 1'] = {
    'data': {
        'reservationUnitByPk': {
            'haukiUrl': {
                'url': 'https://test.com/resource/origin%3A3774af34-9916-40f2-acc7-68db5a627710/?hsa_source=origin&hsa_username=amin.general%40foo.com&hsa_organization=ORGANISATION&hsa_created_at=2021-05-03T00%3A00%3A00%2B00%3A00&hsa_valid_until=2021-05-03T00%3A30%3A00%2B00%3A00&hsa_resource=origin%3A3774af34-9916-40f2-acc7-68db5a627710&hsa_has_organization_rights=true&hsa_signature=33d060cef23cf643241390af20ff12fee22b71d9d0c65c86e7ae5617d429df97'
            },
            'nameFi': 'test name fi'
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_hauki_url_for_unit_manager 1'] = {
    'data': {
        'reservationUnitByPk': {
            'haukiUrl': {
                'url': 'https://test.com/resource/origin%3A3774af34-9916-40f2-acc7-68db5a627710/?hsa_source=origin&hsa_username=unit.admin%40foo.com&hsa_organization=ORGANISATION&hsa_created_at=2021-05-03T00%3A00%3A00%2B00%3A00&hsa_valid_until=2021-05-03T00%3A30%3A00%2B00%3A00&hsa_resource=origin%3A3774af34-9916-40f2-acc7-68db5a627710&hsa_has_organization_rights=true&hsa_signature=4fc177546e1d20a59564a088600053cd89afe6d992ffcc2cce2d6affeb19b10e'
            },
            'nameFi': 'test name fi'
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_order_by_name_en 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameEn': 'name_en'
                    }
                },
                {
                    'node': {
                        'nameEn': 'test name en'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_order_by_name_fi 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'name_fi'
                    }
                },
                {
                    'node': {
                        'nameFi': 'test name fi'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_order_by_name_sv 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameSv': 'name_sv'
                    }
                },
                {
                    'node': {
                        'nameSv': 'test name sv'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_order_by_type_en 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'reservationUnitType': {
                            'nameEn': 'test type en'
                        }
                    }
                },
                {
                    'node': {
                        'reservationUnitType': {
                            'nameEn': None
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_order_by_type_fi 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'reservationUnitType': {
                            'nameFi': 'name_fi'
                        }
                    }
                },
                {
                    'node': {
                        'reservationUnitType': {
                            'nameFi': 'test type fi'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_order_by_type_sv 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'reservationUnitType': {
                            'nameSv': 'test type sv'
                        }
                    }
                },
                {
                    'node': {
                        'reservationUnitType': {
                            'nameSv': None
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_order_by_unit 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'unit': {
                            'nameFi': 'test unit fi'
                        }
                    }
                },
                {
                    'node': {
                        'unit': {
                            'nameFi': 'testunit'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitQueryTestCase::test_order_by_unit_reverse_order 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'unit': {
                            'nameFi': 'testunit'
                        }
                    }
                },
                {
                    'node': {
                        'unit': {
                            'nameFi': 'test unit fi'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_reservation_unit_description_en 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'descriptionEn': 'Lorem ipsum en',
                        'nameFi': 'test name fi'
                    }
                },
                {
                    'node': {
                        'descriptionEn': 'Lorem ipsum en',
                        'nameFi': 'test name fi'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_reservation_unit_description_fi 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'descriptionFi': 'Lorem ipsum fi',
                        'nameFi': 'test name fi'
                    }
                },
                {
                    'node': {
                        'descriptionFi': 'Lorem ipsum fi',
                        'nameFi': 'test name fi'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_reservation_unit_description_sv 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'descriptionFi': 'Lorem ipsum fi',
                        'nameFi': 'test name fi'
                    }
                },
                {
                    'node': {
                        'descriptionFi': 'Lorem ipsum fi',
                        'nameFi': 'test name fi'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_reservation_unit_name_en 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameEn': 'test name en'
                    }
                },
                {
                    'node': {
                        'nameEn': 'test name en'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_reservation_unit_name_fi 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi'
                    }
                },
                {
                    'node': {
                        'nameFi': 'test name fi'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_reservation_unit_name_sv 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameSv': 'test name sv'
                    }
                },
                {
                    'node': {
                        'nameSv': 'test name sv'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_space_name_en 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'spaces': [
                            {
                                'nameEn': 'space name en'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_space_name_fi 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'spaces': [
                            {
                                'nameFi': 'space name fi'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_space_name_sv 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'spaces': [
                            {
                                'nameSv': 'space name sv'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_type_en 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservationUnitType': {
                            'nameEn': 'test type en'
                        }
                    }
                },
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservationUnitType': {
                            'nameEn': 'test type en'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_type_fi 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservationUnitType': {
                            'nameFi': 'test type fi'
                        }
                    }
                },
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservationUnitType': {
                            'nameFi': 'test type fi'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitsFilterTextSearchTestCase::test_filtering_by_type_sv 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservationUnitType': {
                            'nameSv': 'test type sv'
                        }
                    }
                },
                {
                    'node': {
                        'nameFi': 'test name fi',
                        'reservationUnitType': {
                            'nameSv': 'test type sv'
                        }
                    }
                }
            ]
        }
    }
}
