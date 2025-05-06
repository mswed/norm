# Mock data that represents what would be returned from Shotgrid
MOCK_DATA = {
    'Shot': {
        29338: {
            'code': 'ABC_030_010',
            'sg_head_in': 1001,
            'created_by': {'type': 'HumanUser', 'id': 123, 'name': 'Bob Robertson'},
            'tasks': [
                {'type': 'Task', 'id': 456, 'name': 'anim'},
                {'type': 'Task', 'id': 457, 'name': 'comp'},
            ],
            'project': {'type': 'Project', 'id': 101, 'name': 'A Fake Project'},
        }
    },
    'HumanUser': {123: {'name': 'Bob Robertson', 'email': 'b.robertson@studio.com'}},
    'Task': {
        456: {'content': 'anim', 'entity': {'type': 'Shot', 'id': 29338, 'name': 'ABC_030_010'}},
        457: {'content': 'comp', 'entity': {'type': 'Shot', 'id': 29338, 'name': 'ABC_030_010'}},
    },
    'Project': {101: {'name': 'A Fake Project', 'code': 'FPR'}},
}

# Mock schema data (May want to replace it with the full schema from SG)
MOCK_SCHEMA = {
    'Shot': {
        'code': {
            'data_type': {'value': 'text'},
            'editable': {'value': True},
            'name': {'value': 'code'},
        },
        'sg_head_in': {
            'data_type': {'value': 'number'},
            'editable': {'value': True},
            'name': {'value': 'sg_head_in'},
        },
        'created_by': {
            'data_type': {'value': 'entity'},
            'editable': {'value': False},
            'name': {'value': 'created_by'},
        },
        'tasks': {
            'data_type': {'value': 'multi_entity'},
            'editable': {'value': True},
            'name': {'value': 'tasks'},
        },
        'project': {
            'data_type': {'value': 'entity'},
            'editable': {'value': True},
            'name': {'value': 'project'},
        },
        'id': {
            'data_type': {'value': 'number'},
            'editable': {'value': False},
            'name': {'value': 'id'},
        },
        'description': {
            'data_type': {'value': 'text'},
            'editable': {'value': True},
            'name': {'value': 'description'},
        },
    },
    'HumanUser': {
        'name': {
            'data_type': {'value': 'text'},
            'editable': {'value': True},
            'name': {'value': 'name'},
        },
        'email': {
            'data_type': {'value': 'text'},
            'editable': {'value': True},
            'name': {'value': 'email'},
        },
        'id': {
            'data_type': {'value': 'number'},
            'editable': {'value': False},
            'name': {'value': 'id'},
        },
    },
    'Task': {
        'content': {
            'data_type': {'value': 'text'},
            'editable': {'value': True},
            'name': {'value': 'content'},
        },
        'entity': {
            'data_type': {'value': 'entity'},
            'editable': {'value': True},
            'name': {'value': 'entity'},
        },
        'id': {
            'data_type': {'value': 'number'},
            'editable': {'value': False},
            'name': {'value': 'id'},
        },
    },
    'Project': {
        'name': {
            'data_type': {'value': 'text'},
            'editable': {'value': True},
            'name': {'value': 'name'},
        },
        'code': {
            'data_type': {'value': 'text'},
            'editable': {'value': True},
            'name': {'value': 'code'},
        },
        'id': {
            'data_type': {'value': 'number'},
            'editable': {'value': False},
            'name': {'value': 'id'},
        },
    },
}
