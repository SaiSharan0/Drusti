from __future__ import annotations
"""
Grad-CAM — gradient-weighted class activation mapping for ResNet-50.
"""
import os
import uuid
import numpy as np
try:
    import cv2
    import torch
    import torch.nn.functional as F
except ImportError:
    pass
from PIL import Image
from typing import Optional, Tuple


class GradCAM:
    """
    Grad-CAM for PyTorch ResNet-50.
    Hooks into the final convolutional layer to compute gradient-based attention maps.
    """

    def __init__(self, model: torch.nn.Module, target_layer_name: str = "layer4"):
        self.model = model
        self.target_layer_name = target_layer_name
        self._feature_maps: Optional[torch.Tensor] = None
        self._gradients: Optional[torch.Tensor] = None
        self._hooks = []
        self._register_hooks()

    def _register_hooks(self):
        target_layer = dict(self.model.named_modules()).get(self.target_layer_name)
        if target_layer is None:
            raise ValueError(f"Layer '{self.target_layer_name}' not found in model.")

        def forward_hook(module, input, output):
            self._feature_maps = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self._gradients = grad_output[0].detach()

        self._hooks.append(target_layer.register_forward_hook(forward_hook))
        self._hooks.append(target_layer.register_full_backward_hook(backward_hook))

    def remove_hooks(self):
        for h in self._hooks:
            h.remove()

    def compute(
        self, input_tensor: torch.Tensor, target_class: int
    ) -> np.ndarray:
        """
        Compute Grad-CAM heatmap for target_class.
        Returns numpy array of shape (H, W) with values in [0, 1].
        """
        self.model.eval()
        output = self.model(input_tensor)

        self.model.zero_grad()
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1.0
        output.backward(gradient=one_hot)

        gradients = self._gradients  # (1, C, H, W)
        feature_maps = self._feature_maps  # (1, C, H, W)

        # Global average pooling of gradients
        weights = gradients.mean(dim=[2, 3], keepdim=True)  # (1, C, 1, 1)
        cam = (weights * feature_maps).sum(dim=1, keepdim=True)  # (1, 1, H, W)
        cam = F.relu(cam)

        # Normalise to [0, 1]
        cam = cam.squeeze().cpu().numpy()
        if cam.max() > 0:
            cam = cam / cam.max()

        return cam

    def generate_overlay(
        self,
        original_image: Image.Image,
        heatmap: np.ndarray,
        alpha: float = 0.4,
    ) -> Image.Image:
        """Overlay heatmap on the original image."""
        orig_w, orig_h = original_image.size
        heatmap_resized = cv2.resize(heatmap, (orig_w, orig_h))

        # Apply colormap
        heatmap_uint8 = np.uint8(255 * heatmap_resized)
        colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        colored_rgb = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)

        orig_np = np.array(original_image.convert("RGB"))
        blended = (alpha * colored_rgb + (1 - alpha) * orig_np).astype(np.uint8)
        return Image.fromarray(blended)


def generate_and_save_gradcam(
    model: torch.nn.Module,
    input_tensor: torch.Tensor,
    original_image: Image.Image,
    target_class: int,
    output_dir: str,
) -> str:
    """
    Generate Grad-CAM overlay and save to disk.
    Returns the saved file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    cam_obj = GradCAM(model)
    heatmap = cam_obj.compute(input_tensor, target_class)
    overlay = cam_obj.generate_overlay(original_image, heatmap)
    cam_obj.remove_hooks()

    filename = f"gradcam_{uuid.uuid4().hex}.png"
    filepath = os.path.join(output_dir, filename)
    overlay.save(filepath)
    return filepath
