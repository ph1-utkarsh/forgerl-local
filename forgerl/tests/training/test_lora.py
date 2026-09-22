"""Numerical verification; run explicitly with MLX and Apple GPU access."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_flatten
from mlx_lm.tuner.lora import LoRALinear
import numpy as np
from training_math import assistant_token_loss


class LoRATests(unittest.TestCase):
    def test_gradient_matches_analytic_and_freezes_base(self):
        base = nn.Linear(3, 2, bias=False)
        base.weight = mx.array([[1., 2., 3.], [2., 0., -1.]])
        base.freeze()
        layer = LoRALinear.from_base(base, r=2, dropout=0, scale=1)
        layer.lora_a = mx.array([[0.1, 0.2], [0.3, -0.2], [0.2, 0.1]])
        layer.lora_b = mx.zeros((2, 2))
        x = mx.array([[1., 0., 1.], [0., 1., 1.]])
        target = mx.array([[0., 1.], [1., 0.]])
        np.testing.assert_array_equal(np.asarray(layer(x)), np.asarray(base(x)))
        objective = lambda network: mx.mean((network(x) - target) ** 2)
        loss, gradients = nn.value_and_grad(layer, objective)(layer)
        expected = 2 / target.size * np.asarray(layer.lora_a).T @ np.asarray(x).T @ np.asarray(base(x)-target)
        np.testing.assert_allclose(np.asarray(gradients["lora_b"]), expected, rtol=1e-5, atol=1e-6)
        np.testing.assert_array_equal(np.asarray(gradients["lora_a"]), np.zeros((3, 2)))
        self.assertEqual({name for name, _ in tree_flatten(gradients)}, {"lora_a", "lora_b"})
        original = np.asarray(base.weight).copy()
        before = loss.item()
        optim.SGD(learning_rate=0.01).update(layer, gradients)
        mx.eval(layer.parameters())
        np.testing.assert_array_equal(np.asarray(base.weight), original)
        self.assertLess(objective(layer).item(), before)

    def test_prompt_tokens_do_not_contribute(self):
        logits = mx.array([[[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]])
        labels = mx.array([[0, 1, 2]])
        altered_prompt = mx.array([[[0., 100., 0.], [0., 1., 0.], [0., 0., 1.]]])
        first = assistant_token_loss(logits, labels, 1).item()
        self.assertAlmostEqual(first, assistant_token_loss(altered_prompt, labels, 1).item(), places=6)
        expected = np.log(np.exp(1)+2)-1
        self.assertAlmostEqual(first, expected, places=6)
        wrong_response = mx.array([[[1., 0., 0.], [100., 0., 0.], [0., 0., 1.]]])
        self.assertGreater(assistant_token_loss(wrong_response, labels, 1).item(), first)

    def test_empty_assistant_span_rejected(self):
        with self.assertRaises(ValueError):
            assistant_token_loss(mx.zeros((1, 3, 4)), mx.array([[0, 0, 0]]), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
