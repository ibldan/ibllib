"""
"Extended QC" comprises a set of data quality control tests for various parts of the pipeline.
Currently the ExtendedQC object collects the following classes:

- ONEQC: Checks that a session's extracted ALF files conform to the ALF specification,
namely that objects have the correct shape and matching length.
- BpodQC: Checks on data extracted from Bonsai/Bpod.  Amoung other things, checks tha delays 
between trial events are within a tolerance specified by the proscribed task structure

Example: Run full QC for a given session and view the results
eid = 'c94463ed-57da-4f02-8406-46f2f03924f3'
ext = ExtendedQC(eid, lazy=False)
ext.compute_all_qc()
print(ext.frame)

TODO Integrate ephys QC 
"""
import logging

import numpy as np

from alf.io import is_uuid_string
from ibllib.qc.bpodqc_metrics import BpodQC
from ibllib.qc.oneqc_metrics import ONEQC
from oneibl.one import ONE

log = logging.getLogger("ibllib")


class ExtendedQC(object):
    def __init__(self, eid=None, one=None, lazy=True):
        self.one = one or ONE()
        self.eid = eid if is_uuid_string(eid) else None

        self.bpodqc = None
        self.oneqc = None
        self.frame = None

        if not lazy:
            self.compute_all_qc()
            self.build_extended_qc_frame()

    def compute_all_qc(self):
        self.bpodqc = BpodQC(self.eid, one=self.one, lazy=False)
        self.oneqc = ONEQC(
            self.eid, one=self.one, bpod_ntrials=self.bpodqc.bpod_ntrials, lazy=False
        )

    def build_extended_qc_frame(self):
        if self.bpodqc is None:
            self.compute_all_qc()
        # Get bpod and one qc frames
        extended_qc = {}
        # Make average bool pass for bpodqc.metrics frame
        # def average_frame(frame):
        #     return {k: np.nanmean(v) for k, v in frame.items()}
        average_bpod_frame = (lambda frame: {k: np.nanmean(v) for k, v in frame.items()})(
            self.bpodqc.passed
        )
        # aggregate them
        extended_qc.update(self.oneqc.passed)
        extended_qc.update(average_bpod_frame)
        # Ensure None instead of NaNs
        for k, v in extended_qc.items():
            if v is not None and np.isnan(v):
                extended_qc[k] = None

        self.frame = extended_qc

    def read_extended_qc(self):
        return self.one.alyx.rest("sessions", "read", id=self.eid)["extended_qc"]

    def update_extended_qc(self):
        if self.frame is None:
            log.warning("ExtendedQC frame is not built yet, nothing to update")
            return

        out = self.one.alyx.json_field_update(
            endpoint="sessions", uuid=self.eid, field_name="extended_qc", data=self.frame
        )
        return out
