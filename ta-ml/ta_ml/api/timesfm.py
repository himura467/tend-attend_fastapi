import timesfm
from ta_core.constants.constants import CHECKPOINT_PATH

from ta_ml.constants import timesfm as timesfm_constants


def initialize_timesfm() -> timesfm.TimesFm:
    return timesfm.TimesFm(
        hparams=timesfm.TimesFmHparams(
            backend=timesfm_constants.BACKEND,
            context_len=timesfm_constants.CONTEXT_LEN,
            horizon_len=timesfm_constants.HORIZON_LEN,
            num_layers=50,  # Usage に書いてあった値をそのまま使っているだけで特に意味はない
        ),
        checkpoint=timesfm.TimesFmCheckpoint(
            path=CHECKPOINT_PATH,
            huggingface_repo_id=timesfm_constants.CHECKPOINT_REPO_ID,
        ),
    )
