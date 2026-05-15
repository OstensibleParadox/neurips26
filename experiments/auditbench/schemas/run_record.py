from pydantic import BaseModel, Field
from typing import Optional, Literal

class RunRecord(BaseModel):
    run_id: str
    model: str
    model_size: str          # "7B" | "14B" | "32B" | "70B"
    topology: str
    task_family: str
    task_id: str
    seed: int
    logging_regime: str
    probe_type: str
    condition: str
    visible_trace_hash: str
    hidden_channel_id: str
    intervention_payload_hash: str
    action_distribution: dict[str, float]
    argmax_action: str
    realized_action: str
    tool_token_probs: dict[str, float]
    action_flip_under_probe: bool
    task_success: bool
    success_delta: Optional[float] = None
    wrong_tool: bool
    unsafe_action: Optional[bool] = None
    trajectory_return: Optional[float] = None
    probe_validity_control: bool
    off_manifold_score: Optional[float] = None
    epsilon_state_UB: float = Field(ge=0)
    delta_act_LB: float = Field(ge=0)
    bootstrap_CI_low: float
    bootstrap_CI_high: float
    
    # Optional fields for specific runners (Diffusion, Multi-Agent)
    decoding_policy: Optional[str] = None
    perturbation_sigma: Optional[float] = None
    denoising_steps: Optional[int] = None
    probed_step: Optional[int] = None
    probed_layer: Optional[str] = None
    controller_samples: Optional[int] = None
