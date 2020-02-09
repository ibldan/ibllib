import numpy as np
import matplotlib.pyplot as plt
from oneibl.one import ONE
from pathlib import Path
import alf.io
import ibllib.plots as iblplt


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def check_wheel_angle(eid):

    Plot = True

    one = ONE()
    #eid = 'e1023140-50c1-462a-b80e-5e05626d7f0e' # at least 9 bad cases

    #eid = one.search(subject='ZM_2104', date='2019-09-19', number=1) 
    Dataset_types=['wheel.position','wheel.timestamps','trials.feedback_times','trials.feedbackType']

    D = one.load(eid, dataset_types=Dataset_types, clobber=False, download_only=True)
    session_path = Path(D[0]).parent

    wheel = alf.io.load_object(session_path, '_ibl_wheel')
    trials = alf.io.load_object(session_path, '_ibl_trials')
    reward_success = trials['feedback_times'][trials['feedbackType'] == 1]
    reward_failure = trials['feedback_times'][trials['feedbackType'] == -1]

    if Plot:
        plt.plot(wheel['times'],wheel['position'], linestyle = '', marker = 'o')

        #iblplt.vertical_lines(trials['stimOn_times'], ymin=-100, ymax=100,
        #                      color='r', linewidth=0.5, label='stimOn_times')

        #iblplt.vertical_lines(reward_failure, ymin=-100, ymax=100,
        #                      color='b', linewidth=0.5, label='reward_failure')

        iblplt.vertical_lines(reward_success, ymin=-100, ymax=100,
                              color='k', linewidth=0.5, label='reward_success')

        plt.legend()   
        plt.xlabel('time [sec]')
        plt.ylabel('wheel linear displacement [cm]')
        plt.show()

    # get fraction of reward deliveries with silent wheel time_delay before the reward
    time_delay = 0.5

    bad_cases1 = []
    for rew in reward_success:
        
        left = wheel['times'][find_nearest(wheel['times'], rew - time_delay)]
        right = wheel['times'][find_nearest(wheel['times'], rew)]
      
        if left == right:
            if left < rew - time_delay:
                bad_cases1.append(rew) 
 
    if len(bad_cases1) == 0:
        print('Good news, no impossible case found.')
    else:
        print('Bad news, at least one impossible case found.')
        return len(bad_cases1)
