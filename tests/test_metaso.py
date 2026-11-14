import importlib.util
import unittest
from unittest.mock import patch
import io
import json
import tempfile
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'metaso-video/scripts/metaso.py'
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

class NewFeaturesTest(unittest.TestCase):
    payload = ModelsTest.payload
    def test_regeneration_modes(self):
        metaso.validate_regeneration({'model': 'MiniMax-H3', 'resolution': '2K', 'source_task_id': '123'})
        content = [{'type': 'text', 'text': 'original prompt'}, {'type': 'video_url', 'video_url': {'url': 'https://example.com/a.mp4'}, 'role': 'base_video'}]
        metaso.validate_regeneration({'model': 'MiniMax-H3', 'resolution': '2K', 'content': content})
        for payload in ({'model': 'MiniMax-H3', 'resolution': '2K'},
                        {'model': 'MiniMax-H3', 'resolution': '2K', 'source_task_id': '123', 'content': content},
                        {'model': 'MiniMax-H3', 'resolution': '2K', 'content': content + content[-1:]},
                        {'model': 'seedance-2.5', 'resolution': '2K', 'source_task_id': '123'}):
            with self.assertRaises(ValueError):
                metaso.validate_regeneration(payload)

    def test_balance_and_regeneration_route(self):
        for argv, expected in [(['metaso.py', 'balance'], '/v2/credits/balance'),
                               (['metaso.py', 'regenerate', '--task-id', '123', '--submit'], '/v2/video_regeneration')]:
            with self.subTest(argv=argv), patch.object(metaso.sys, 'argv', argv), patch.object(metaso, 'api', return_value={}) as api, patch('sys.stdout', new_callable=io.StringIO):
                metaso.main()
                self.assertEqual(api.call_args.args[0], expected)

    def test_regenerate_preview_never_calls_api(self):
        with patch.object(metaso.sys, 'argv', ['metaso.py', 'regenerate', '--task-id', '123']), patch.object(metaso, 'api') as api, patch('sys.stdout', new_callable=io.StringIO) as output:
            metaso.main()
            api.assert_not_called()
            self.assertEqual(json.loads(output.getvalue())['request']['source_task_id'], '123')

    def test_upload_preview_never_uploads(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'image.png'
            f.write_bytes(b'image')
            with patch.object(metaso.sys, 'argv', ['metaso.py', 'upload', str(f)]), patch.object(metaso, 'upload') as upload, patch('sys.stdout', new_callable=io.StringIO):
                metaso.main()
                upload.assert_not_called()

    def test_upload_multipart(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'image.png'
            f.write_bytes(b'image-data')
            with patch.object(metaso, 'load_key', return_value='test-key'), patch.object(metaso.urllib.request, 'urlopen') as urlopen:
                response = urlopen.return_value.__enter__.return_value
                response.read.return_value = json.dumps({'file': {'file_id': 123}}).encode()
                result = metaso.upload(f)
                request = urlopen.call_args.args[0]
                self.assertTrue(request.full_url.endswith('/v1/files/upload'))
                self.assertIn(b'video_generation_input', request.data)
                self.assertIn(b'image-data', request.data)
                self.assertEqual(result['url'], 'mm_file://123')

    def test_existing_h3_settings(self):
        metaso.validate(self.payload('MiniMax-H3', '768P', 30))
        metaso.validate(self.payload('MiniMax-H3', '512p', 30))
        with self.assertRaises(ValueError):
            metaso.validate(self.payload('MiniMax-H3', '2K', 16))

    def test_new_models_and_boundaries(self):
        metaso.validate(self.payload('seedance-2.0-fast', '720p', 15))
        metaso.validate(self.payload('seedance-2.5', '1080p', 30))
        for model, resolution, duration in [('seedance-2.0-fast', '1080p', 4),
                                            ('seedance-2.0-fast', '720p', 16),
                                            ('seedance-2.5', '4k', 4),
                                            ('seedance-2.5', '720p', 31)]:
            with self.subTest(model=model, resolution=resolution, duration=duration):
                with self.assertRaises(ValueError):
                    metaso.validate(self.payload(model, resolution, duration))

if __name__ == '__main__':
    unittest.main()
