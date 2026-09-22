import unittest

from qualification import TASKS
from runner import action_step, grade, pinned_image, valid_path, same_json


class ProtocolTests(unittest.TestCase):
    def test_json_types(self):
        self.assertFalse(same_json(True, 1))
        self.assertFalse(same_json([False], [0]))
        self.assertFalse(same_json({"x": 1}, {"x": True}))
        self.assertTrue(same_json({"x": [1, False]}, {"x": [1, False]}))

    def test_paths(self):
        for path in ("../solution.py", "/etc/passwd", "solution.py/../x", None, "./solution.py"):
            self.assertFalse(valid_path(path))
        self.assertTrue(valid_path("solution.py"))

    def test_invalid_actions(self):
        for action in ([], {"action": "shell"}, {"action": "write", "path": "solution.py", "content": "x" * 16001}):
            with self.assertRaises(ValueError):
                action_step(action, "", TASKS[0], "unused")


class IsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = pinned_image()

    def check(self, source, **kwargs):
        return grade(source, TASKS[0].hidden, self.image, **kwargs)

    def test_early_exit_cannot_pass(self):
        result = self.check("import os\nos._exit(0)\n")
        self.assertFalse(result["passed"])
        self.assertEqual(result["reason"], "invalid_worker_response")

    def test_boolean_success_message_cannot_pass(self):
        self.assertFalse(self.check('print("true")\nraise SystemExit(0)\n')["passed"])

    def test_timeout(self):
        result = self.check("while True:\n    pass\n", timeout=1)
        self.assertFalse(result["passed"])
        self.assertEqual(result["reason"], "timeout")

    def test_output_limit(self):
        result = self.check("while True:\n    print('x'*10000, flush=True)\n")
        self.assertFalse(result["passed"])
        self.assertEqual(result["reason"], "output_limit")

    def test_no_hidden_grader_file(self):
        source = "import os\nassert sorted(os.listdir('/work')) == ['solution.py', 'worker.py']\n" + TASKS[0].oracle
        self.assertTrue(self.check(source)["passed"])

    def test_write_mount_denied(self):
        source = "try:\n    open('/work/solution.py','w')\nexcept OSError:\n    pass\nelse:\n    raise RuntimeError('writable mount')\n" + TASKS[0].oracle
        self.assertTrue(self.check(source)["passed"])

    def test_network_denied(self):
        source = "import socket\ns=socket.socket()\ns.settimeout(0.2)\ntry:\n    s.connect(('1.1.1.1',443))\nexcept OSError:\n    pass\nelse:\n    raise RuntimeError('network available')\nfinally:\n    s.close()\n" + TASKS[0].oracle
        self.assertTrue(self.check(source)["passed"])


if __name__ == "__main__":
    unittest.main()
