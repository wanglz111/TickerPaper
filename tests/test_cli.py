import unittest

from eink_crypto.cli import build_images, create_sample_config


class CliTest(unittest.TestCase):
    def test_sample_config_builds_two_dashboard_images(self):
        config = create_sample_config()

        price_page, portfolio_page = build_images(config, use_sample=True)

        self.assertEqual(price_page.size, (400, 300))
        self.assertEqual(portfolio_page.size, (400, 300))
        self.assertEqual(price_page.mode, "1")
        self.assertEqual(portfolio_page.mode, "1")


if __name__ == "__main__":
    unittest.main()
