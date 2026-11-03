import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'metaso-h3/scripts/metaso.py'
spec = importlib.util.spec_from_file_location('metaso', path)
metaso = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metaso)

class ModelsTest(unittest.TestCase):
    def payload(self, model, resolution, duration):
        return {'model': model, 'resolution': resolution, 'duration': duration,
                'content': [{'type': 'text', 'text': 'a bird flies'}]}

    def test_seedance_models_accept_published_settings(self):
        for model, resolution in [('seedance-2.0-mini', '720p'), ('seedance-2.0', '4k')]:
            with self.subTest(model=model):
                metaso.validate(self.payload(model, resolution, 15))

    def test_seedance_rejects_unsupported_settings(self):
        for model, resolution, duration in [('seedance-2.0-mini', '4k', 4), ('seedance-2.0', '720p', 16)]:
            with self.subTest(model=model, resolution=resolution, duration=duration):
                with self.assertRaises(ValueError):
                    metaso.validate(self.payload(model, resolution, duration))

    def test_existing_h3_settings(self):
        metaso.validate(self.payload('MiniMax-H3', '768P', 30))
        with self.assertRaises(ValueError):
            metaso.validate(self.payload('MiniMax-H3', '2K', 16))

if __name__ == '__main__':
    unittest.main()
