import timesfm

from ta_ml.constants import models

tfm = timesfm.TimesFm(
    hparams=timesfm.TimesFmHparams(
        backend=models.BACKEND,
        context_len=models.CONTEXT_LEN,
        horizon_len=models.HORIZON_LEN,
    ),
    checkpoint=timesfm.TimesFmCheckpoint(
        huggingface_repo_id=models.CHECKPOINT_REPO_ID,
    ),
)
