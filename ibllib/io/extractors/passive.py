"""
functions used in passive_script
"""
# Author: Gaelle C, Matt W
import numpy as np
import ibllib.io.raw_data_loaders as rawio


def get_spacer_times(spacer_template, jitter, ttl_signal, t_quiet):
    """
    :param spacer_template: list of indices where ttl signal changes
    :type spacer_template: array-like
    :param jitter: jitter (in seconds) for matching ttl_signal with spacer_template
    :type jitter: float
    :param ttl_signal:
    :type ttl_signal: array-like
    :param t_quiet: seconds between spacer and next stim
    :type t_quiet: float
    :return: times of spacer onset/offset
    :rtype: n_spacer x 2 np.ndarray; first col onset times, second col offset
    """
    diff_spacer_template = np.diff(spacer_template)
    # add jitter;
    # remove extreme values
    spacer_model = jitter + diff_spacer_template[2:-2]
    # diff ttl signal to compare to spacer_model
    dttl = np.diff(ttl_signal)
    # remove diffs larger than max diff in model to clean up signal
    dttl[dttl > np.max(spacer_model)] = 0
    # convolve cleaned diff ttl signal w/ spacer model
    conv_dttl = np.correlate(dttl, spacer_model, mode='full')
    # find spacer location
    thresh = 3.0
    idxs_spacer_middle = np.where(
        (conv_dttl[1:-2] < thresh) &
        (conv_dttl[2:-1] > thresh) &
        (conv_dttl[3:] < thresh))[0]
    # adjust indices for
    # - `np.where` call above
    # - length of spacer_model
    idxs_spacer_middle += 2 - int((np.floor(len(spacer_model) / 2)))
    # pull out spacer times (middle)
    ts_spacer_middle = ttl_signal[idxs_spacer_middle]
    # put beginning/end of spacer times into an array
    spacer_length = np.max(spacer_template)
    spacer_times = np.zeros(shape=(ts_spacer_middle.shape[0], 2))
    for i, t in enumerate(ts_spacer_middle):
        spacer_times[i, 0] = t - (spacer_length / 2) - t_quiet
        spacer_times[i, 1] = t + (spacer_length / 2) + t_quiet
    return spacer_times, conv_dttl


def reshape_RF(RF_file, meta):
    frame_array = np.fromfile(RF_file, dtype='uint8')
    y_pix, x_pix, _ = meta['VISUAL_STIM_1']['stim_file_shape']
    frames = np.transpose(
        np.reshape(frame_array, [y_pix, x_pix, -1], order='F'), [2, 1, 0])
    ttl_trace = frames[:, 0, 0]
    # todo test on reshape ?
    # todo find n ttl expected and return
    # Convert values to 0,1,-1 for simplicity
    ttl_01 = np.zeros(np.size(ttl_trace))
    ttl_01[np.where(ttl_trace == 0)] = -1
    ttl_01[np.where(ttl_trace == 255)] = 1

    # Find number of passage from [128 0] and [128 255]  (converted to 0,1,-1)
    d_ttl_01 = np.diff(ttl_01)
    id_raise = np.where(np.logical_and(ttl_01 == 0, np.append(d_ttl_01, 0) == 1))[0]
    id_fall = np.where(np.logical_and(ttl_01 == 0, np.append(d_ttl_01, 0) == -1))[0]

    n_ttl_expected = len(id_raise) + len(id_fall)

    return frames, ttl_trace, n_ttl_expected


def ephysCW_end(session_path):
    # return time (second) at which ephysCW ends
    bpod_raw = rawio.load_data(session_path)
    t_end_ephys = bpod_raw[-1]['behavior_data']['States timestamps']['exit_state'][0][-1] + 60
    return t_end_ephys


def truncate_ttl_signal(ttl, time_cutoff):
    '''
    :param ttl: dict with 2 keys (polarities and times), values in times in (s)
    :param time_cutoff: time of cutoff in (s)
    :return: dict with 2 keys (polarities and times), values in times in (s)
    '''
    ttl_trunk = dict()
    ttl_trunk['times'] = ttl['times'][ttl['times'] > time_cutoff]
    ttl_trunk['polarities'] = ttl['polarities'][ttl['times'] > time_cutoff]
    return ttl_trunk


def find_between(ttl, t_start_search, t_end_search):
    id_ttl = np.where(np.logical_and(ttl['times'] > t_start_search,
                                     ttl['times'] < t_end_search))[0]
    times_between = ttl['times'][id_ttl]
    return times_between


def check_n_ttl_between(n_exp, t_start_search, t_end_search, ttl):
    times_between = find_between(ttl=ttl,
                                 t_start_search=t_start_search,
                                 t_end_search=t_end_search)
    if len(times_between) != n_exp:
        raise ValueError('Incorrect number of pulses found')
    else:
        return times_between
