"""
Defines unit tests for this package.
"""
import os
from unittest import TestCase

from codalabtools.compute.worker import WorkerConfig

class ComputeConfigTests(TestCase):
    """Tests for WorkerConfig."""

    def no_config_test(self):
        """Loads non-existent config file."""
        cfg_path = os.path.join(os.getcwd(), "codalabtools", "compute", "foo.config")
        self.assertFalse(os.path.exists(cfg_path))
        with self.assertRaises(EnvironmentError):
            WorkerConfig(cfg_path)

    def sample_config_test(self):
        """Loads 'sample.config' in codalabtools\\compute."""
        cfg_path = os.path.join(os.getcwd(), "codalabtools", "compute", "sample.config")
        self.assertTrue(os.path.isfile(cfg_path))
        cfg = WorkerConfig(cfg_path)
        self.assertEqual(cfg_path, cfg.getFilename())
        self.assertEqual("storage account name", cfg.getAzureStorageAccountName())
        self.assertEqual("storage key", cfg.getAzureStorageAccountKey())
        self.assertEqual("service bus name", cfg.getAzureServiceBusNamespace())
        self.assertEqual("acs default key", cfg.getAzureServiceBusKey())
        self.assertEqual("owner", cfg.getAzureServiceBusIssuer())
        self.assertEqual("compute", cfg.getAzureServiceBusQueue())
        self.assertEqual("D:\\Temp", cfg.getLocalRoot())
        log_cfg_expected = {
            'version': 1,
            'formatters': {
                'simple': {
                    'format': '%(asctime)s %(levelname)s %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'DEBUG',
                    'formatter': 'simple',
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                'codalabtools': {
                    'level': 'DEBUG',
                    'handlers': ['console'],
                    'propagate': False
                }
            },
            'root': {
              'level': 'DEBUG',
              'handlers': ['console']
            }
        }
        self.assertDictEqual(log_cfg_expected, cfg.getLoggerDictConfig())
