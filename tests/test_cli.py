import unittest

from eink_crypto.cli import build_image, create_sample_config


class CliTest(unittest.TestCase):
    def test_sample_config_builds_single_price_image(self):
        config = create_sample_config()

        image = build_image(config, use_sample=True)

        self.assertEqual(config.page_id, 1)
        self.assertEqual(image.size, (400, 300))
        self.assertEqual(image.mode, "1")


if __name__ == "__main__":
    unittest.main()
