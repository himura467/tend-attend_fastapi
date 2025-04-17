import timesfm
from ta_core.constants.constants import CHECKPOINT_PATH

from ta_ml.constants import models

tfm = timesfm.TimesFm(
    hparams=timesfm.TimesFmHparams(
        backend=models.BACKEND,
        context_len=models.CONTEXT_LEN,
        horizon_len=models.HORIZON_LEN,
        num_layers=50,  # Usage に書いてあった値をそのまま使っているだけで特に意味はない
    ),
    checkpoint=timesfm.TimesFmCheckpoint(
        path=CHECKPOINT_PATH,
        huggingface_repo_id=models.CHECKPOINT_REPO_ID,
    ),
)
