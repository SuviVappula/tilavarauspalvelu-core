# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots['ReservationUnitTestCase::test_filtering_by_active_application_rounds 1'] = {
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

snapshots['ReservationUnitTestCase::test_filtering_by_is_draft_false 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'isDraft': False,
                        'nameFi': 'Test name'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_is_draft_true 1'] = {
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

snapshots['ReservationUnitTestCase::test_filtering_by_keyword_group 1'] = {
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
                        'nameFi': 'Test name'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_max_persons 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'maxPersons': 110,
                        'nameFi': 'Test name'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_max_persons_not_found 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_multiple_keyword_groups 1'] = {
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
                        'nameFi': 'Test name'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_multiple_purposes 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
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

snapshots['ReservationUnitTestCase::test_filtering_by_multiple_reservation_states 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
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

snapshots['ReservationUnitTestCase::test_filtering_by_multiple_types 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
                        'reservationUnitType': {
                            'nameFi': 'Test type'
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

snapshots['ReservationUnitTestCase::test_filtering_by_multiple_units 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
                        'unit': {
                            'nameFi': 'Test unit'
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

snapshots['ReservationUnitTestCase::test_filtering_by_purpose 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
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

snapshots['ReservationUnitTestCase::test_filtering_by_reservation_state 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
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

snapshots['ReservationUnitTestCase::test_filtering_by_reservation_timestamps 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
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

snapshots['ReservationUnitTestCase::test_filtering_by_reservation_unit_description 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'descriptionFi': 'Lorem ipsum',
                        'nameFi': 'Test name'
                    }
                },
                {
                    'node': {
                        'descriptionFi': 'Lorem ipsum',
                        'nameFi': 'Test name'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_reservation_unit_name 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name'
                    }
                },
                {
                    'node': {
                        'nameFi': 'Test name'
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_space_name 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
                        'spaces': [
                            {
                                'nameFi': 'space name'
                            }
                        ]
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_type 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
                        'reservationUnitType': {
                            'nameFi': 'Test type'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_type_text 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
                        'reservationUnitType': {
                            'nameFi': 'Test type'
                        }
                    }
                },
                {
                    'node': {
                        'nameFi': 'Test name',
                        'reservationUnitType': {
                            'nameFi': 'Test type'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_filtering_by_unit 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'nameFi': 'Test name',
                        'unit': {
                            'nameFi': 'Test unit'
                        }
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_getting_hauki_url 1'] = {
    'data': {
        'reservationUnitByPk': {
            'haukiUrl': {
                'url': 'https://test.com/resource/origin:3774af34-9916-40f2-acc7-68db5a627710/?hsa_source=origin&hsa_username=AnonymousUser&hsa_organization=ORGANISATION&hsa_created_at=2021-05-03 00:00:00+00:00&hsa_valid_until=2021-05-03 00:30:00+00:00&hsa_resource=origin:3774af34-9916-40f2-acc7-68db5a627710&hsa_signature=8df8cd01df388f8f1aad70e82035eaae3a27d33c2f3e3583bb7f9bb7aca966f1'
            },
            'nameFi': 'Test name'
        }
    }
}

snapshots['ReservationUnitTestCase::test_getting_manually_given_surface_area 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'surfaceArea': 500
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_getting_reservation_units 1'] = {
    'data': {
        'reservationUnits': {
            'edges': [
                {
                    'node': {
                        'applicationRounds': [
                        ],
                        'cancellationRule': {
                            'nameEn': 'en',
                            'nameFi': 'fi',
                            'nameSv': 'sv'
                        },
                        'contactInformationFi': '',
                        'descriptionFi': '',
                        'equipment': [
                        ],
                        'images': [
                        ],
                        'location': None,
                        'maxPersons': 110,
                        'nameFi': 'Test name',
                        'purposes': [
                        ],
                        'requireIntroduction': False,
                        'reservationUnitType': {
                            'nameFi': 'Test type'
                        },
                        'reservations': [
                        ],
                        'resources': [
                        ],
                        'services': [
                        ],
                        'spaces': [
                            {
                                'nameFi': 'Large space'
                            },
                            {
                                'nameFi': 'Small space'
                            }
                        ],
                        'surfaceArea': 150,
                        'termsOfUseFi': None
                    }
                }
            ]
        }
    }
}

snapshots['ReservationUnitTestCase::test_getting_terms 1'] = {
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
