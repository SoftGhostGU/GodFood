# food_model.py
import torch
import torch.nn as nn
import torch.nn.functional as F
from federated_config import HIDDEN_DIM, OUTPUT_DIM

class FoodPreferenceModel(nn.Module):
    def __init__(self, input_dim):
        super(FoodPreferenceModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, HIDDEN_DIM)
        self.bn1 = nn.BatchNorm1d(HIDDEN_DIM)
        self.fc2 = nn.Linear(HIDDEN_DIM, HIDDEN_DIM // 2)
        self.bn2 = nn.BatchNorm1d(HIDDEN_DIM // 2)
        self.fc3 = nn.Linear(HIDDEN_DIM // 2, OUTPUT_DIM)

    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        x = F.dropout(x, p=0.3, training=self.training)
        x = F.relu(self.bn2(self.fc2(x)))
        x = F.dropout(x, p=0.3, training=self.training)
        x = self.fc3(x) # No softmax here, CrossEntropyLoss will handle it
        return x

def weights_to_json_serializable(state_dict):
    return {k: v.cpu().numpy().tolist() for k, v in state_dict.items()}

def weights_from_json_serializable(serializable_weights):
    return {k: torch.tensor(v) for k, v in serializable_weights.items()}