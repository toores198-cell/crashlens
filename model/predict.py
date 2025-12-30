import mindspore as ms
from .crash_model import CrashModel

_model = CrashModel()

def predict_scenario(inputs):
    x = ms.Tensor([inputs], ms.float32)
    probs = _model(x).asnumpy()[0]

    return {
        "A": float(probs[0]),
        "B": float(probs[1]),
        "C": float(probs[2]),
    }
