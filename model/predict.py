import numpy as np

def predict_scenario(inputs):
    """
    Streamlit Cloud can't install mindspore-lite (Python 3.13),
    so we return a deterministic mock probability distribution.
    This keeps the A/B/C pipeline working for the prototype.
    """

    # inputs = [see app.py] -> [speed1, speed2, dir1, dir2, hour, intersection]
    speed1, speed2, dir1, dir2, hour, intersection = inputs

    # Simple heuristic scoring (mock inference)
    a_score = 0.5 * (speed1 / 200.0) + 0.2 * (intersection == 1) + 0.1 * (hour >= 18)
    b_score = 0.5 * (speed2 / 200.0) + 0.2 * (intersection == 1) + 0.1 * (hour <= 6)
    c_score = 0.3 + 0.2 * (abs(speed1 - speed2) < 20) + 0.1 * (dir1 != dir2)

    scores = np.array([a_score, b_score, c_score], dtype=float)
    scores = np.clip(scores, 1e-6, None)
    probs = scores / scores.sum()

    return {
        "A": float(probs[0]),
        "B": float(probs[1]),
        "C": float(probs[2]),
    }
