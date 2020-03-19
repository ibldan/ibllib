'''
Programmatically add new water administrations for the week-end onto the Alyx database via ONE.
'''
#  Author: Olivier Winter

from oneibl.one import ONE

one = ONE(base_url='https://dev.alyx.internationalbrainlab.org')

dates = ['2018-11-19T12:00', '2018-11-22T12:00', '2018-11-23T12:00']

# subject_details = one.alyx.rest('subjects', 'list', '?alive=True&project=ibl_neuropixel_brainwide_01&water_restricted=True')

sub = ['IBL_1',
       'IBL_10',
       'IBL_11',
       'IBL_12',
       'IBL_13',
       'IBL_14',
       'IBL_15',
       'IBL_16',
       'IBL_17',
       'IBL_33',
       'IBL_34',
       'IBL_35',
       'IBL_36',
       'IBL_43',
       'IBL_44',
       'IBL_45',
       'IBL_46',
       'IBL_47']

for dat in dates:
    for s in sub:
        wa_ = {
            'subject': s,
            'date_time': dat,
            'water_type': 'Hydrogel 5% Citric Acid',
            'user': 'valeria',
            'adlib': True}
        # Do not use the example on anything else than alyx-dev !
        if one.alyx._base_url == 'https://dev.alyx.internationalbrainlab.org':
            rep = one.alyx.rest('water-administrations', 'create', data=wa_)
