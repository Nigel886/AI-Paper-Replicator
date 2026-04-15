import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models

class VIPEncoder(nn.Module):
    """
    VIP Encoder based on ResNet backbone.
    The goal is to produce embeddings where -L2 distance maps to a value function.
    """
    def __init__(self, backbone="resnet50", embedding_dim=1024):
        super(VIPEncoder, self).__init__()
        # Load standard backbone (usually ResNet50 for VIP)
        base_model = getattr(models, backbone)(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        
        # Remove the classification head
        self.backbone = nn.Sequential(*list(base_model.children())[:-1])
        
        # Projection head to embedding space
        self.projector = nn.Sequential(
            nn.Flatten(),
            nn.Linear(base_model.fc.in_features, embedding_dim),
            nn.LayerNorm(embedding_dim)
        )

    def forward(self, x):
        # [B, 3, H, W] -> [B, 2048, 1, 1]
        features = self.backbone(x)
        # [B, 2048, 1, 1] -> [B, embedding_dim]
        embeddings = self.projector(features)
        return embeddings

class VIPLoss(nn.Module):
    """
    Implementation of the Value-Implicit objective (Equation 3/5).
    Optimizes representation phi such that V(phi(s), phi(g)) = -||phi(s) - phi(g)||
    """
    def __init__(self, gamma=0.98):
        super(VIPLoss, self).__init__()
        self.gamma = gamma

    def value_fn(self, state_emb, goal_emb):
        """Implicit Value Function: Negative L2 Distance"""
        # [B, D], [B, D] -> [B]
        return -torch.norm(state_emb - goal_emb, p=2, dim=-1)

    def forward(self, obs, next_obs, goal_obs, init_obs):
        """
        Args:
            obs: current observation embeddings [B, D]
            next_obs: next observation embeddings [B, D]
            goal_obs: goal observation embeddings [B, D]
            init_obs: initial observation embeddings [B, D]
        """
        # Calculate values for the TD-error and initial state objective
        v_curr = self.value_fn(obs, goal_obs)       # [B]
        v_next = self.value_fn(next_obs, goal_obs)  # [B]
        v_init = self.value_fn(init_obs, goal_obs)  # [B]

        # Reward is defined as -1 for all non-goal transitions in the paper
        reward = -1.0
        
        # TD-Error: r + gamma * V(s') - V(s)
        # [B]
        td_error = reward + self.gamma * v_next - v_curr
        
        # Equation 5: (1 - gamma) * E[V(s_0)] + log E[exp(TD_error)]
        # We use logsumexp for numerical stability of the expectation over the batch
        term1 = (1 - self.gamma) * v_init.mean()
        term2 = torch.logsumexp(td_error, dim=0) - torch.log(torch.tensor(td_error.size(0)))
        
        # VIP Loss (Minimize this)
        loss = term1 + term2
        return -loss # Negative because Eq 3 is a Max-Min problem (we maximize w.r.t phi)

# --- Example Usage ---
if __name__ == "__main__":
    # Hyperparameters
    batch_sz, c, h, w = 8, 3, 224, 224
    
    # Initialize Model & Loss
    model = VIPEncoder(embedding_dim=1024)
    criterion = VIPLoss(gamma=0.98)
    
    # Dummy data representing a video snippet: [Initial, Current, Next, Goal/Last]
    img_init = torch.randn(batch_sz, c, h, w)
    img_curr = torch.randn(batch_sz, c, h, w)
    img_next = torch.randn(batch_sz, c, h, w)
    img_goal = torch.randn(batch_sz, c, h, w)
    
    # Forward pass
    z_init = model(img_init)  # [B, 1024]
    z_curr = model(img_curr)  # [B, 1024]
    z_next = model(img_next)  # [B, 1024]
    z_goal = model(img_goal)  # [B, 1024]
    
    # Compute Loss
    loss = criterion(z_curr, z_next, z_goal, z_init)
    
    print(f"VIP Loss: {loss.item():.4f}")