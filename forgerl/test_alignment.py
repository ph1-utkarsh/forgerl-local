import unittest
from alignment_math import clipped_grpo_loss,dpo_loss,grouped_advantages,repair_reward

class AlignmentTests(unittest.TestCase):
    def test_dpo_prefers_margin(self):
        self.assertLess(dpo_loss(2,0,0,0),dpo_loss(0,2,0,0))
    def test_group_centered(self):
        values=grouped_advantages([1,0,0]); self.assertAlmostEqual(sum(values),0)
    def test_grpo_better_policy(self):
        self.assertLess(clipped_grpo_loss([.1,-.1],[0,0],[1,0]),clipped_grpo_loss([-.1,.1],[0,0],[1,0]))
    def test_reward(self):
        self.assertGreater(repair_reward(True,True,True,3),repair_reward(True,False,True,3))

if __name__=="__main__": unittest.main()
