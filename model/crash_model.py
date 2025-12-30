import mindspore as ms
import mindspore.nn as nn

class CrashModel(nn.Cell):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Dense(6, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Dense(16, 3)
        self.softmax = nn.Softmax(axis=1)

    def construct(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return self.softmax(x)
