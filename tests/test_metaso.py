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
                self.assertEqual(result['file_id'], '123')

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

class ImageTest(unittest.TestCase):
    def test_image_defaults_and_custom_boundaries(self):
        for size in [None, "655360x1", "768x1376", "1280x512", "5000x4000", "7104x2368", "1025x1023", "1000x1000"]:
            payload = {"prompt": "a paper boat"}
            if size is not None:
                payload["size"] = size
            if size == "655360x1":
                with self.assertRaises(ValueError):
                    metaso.validate_image(payload)
            else:
                metaso.validate_image(payload)
        metaso.validate_image({"prompt": "x" * 2000, "size": "768x2304", "reference_file_ids": ["1", "2", "3"], "enhance_prompt": False})

    def test_invalid_image_requests(self):
        for fields in [{"prompt": ""}, {"prompt": "x" * 2001}, {"model": "MiniMax-H3"},
                       {"size": "100x100"}, {"size": "10000x10000"}, {"size": "4000x1000"},
                       {"size": "0x1000"}, {"size": "1024*1024"}, {"size": 1024},
                       {"reference_file_ids": ["1", "2", "3", "4"]},
                       {"reference_file_ids": [""]}, {"reference_file_ids": [1]},
                       {"reference_file_ids": "123"}, {"enhance_prompt": "false"}, {"seed": 12},
                       {"aspect_ratio": "16:9"}]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                metaso.validate_image({"prompt": "a boat", **fields})

    def test_image_submit_and_preview(self):
        idem = "80c893a0-8d62-4ed3-8c46-548ee84173ad"
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "image.json"
            payload = {"prompt": "a boat", "reference_file_ids": ["123"], "enhance_prompt": False}
            f.write_text(json.dumps(payload))
            for submit in [False, True]:
                argv = ["metaso.py", "image-create", str(f), "--idempotency-key", idem] + (["--submit"] if submit else [])
                with patch.object(metaso.sys, "argv", argv), patch.object(metaso, "api", return_value={"task_id": "1"}) as api, patch("sys.stdout", new_callable=io.StringIO) as output, patch("sys.stderr", new_callable=io.StringIO):
                    metaso.main()
                    if submit:
                        api.assert_called_once_with("/v2/image_generation", payload, idempotency_key=idem)
                    else:
                        api.assert_not_called()
                    self.assertEqual(json.loads(output.getvalue())["idempotency_key"], idem)

    def test_image_query_and_download(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "image.png"
            task = {"task": {"status": "succeeded", "content": {"url": "https://example.com/image.png"}}}
            with patch.object(metaso.sys, "argv", ["metaso.py", "image-download", "123", str(output)]), patch.object(metaso, "api", return_value=task) as api, patch.object(metaso.urllib.request, "urlopen") as fetch, patch("sys.stdout", new_callable=io.StringIO):
                fetch.return_value.__enter__.return_value = io.BytesIO(b"image bytes")
                metaso.main()
                api.assert_called_once_with("/v2/query/image_generation/123")
                fetch.assert_called_once_with("https://example.com/image.png", timeout=60)
                self.assertEqual(output.read_bytes(), b"image bytes")
                with self.assertRaises(FileExistsError):
                    metaso.main()

    def test_idempotency_header(self):
        idem = "80c893a0-8d62-4ed3-8c46-548ee84173ad"
        with patch.object(metaso, "load_key", return_value="test-key"), patch.object(metaso.urllib.request, "urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = b'{"task_id":"123"}'
            metaso.api("/v2/image_generation", {"prompt": "a boat"}, idempotency_key=idem)
            request = urlopen.call_args.args[0]
            self.assertEqual(request.get_header("Idempotency-key"), idem)
            self.assertEqual(request.get_header("Authorization"), "Bearer test-key")

if __name__ == '__main__':
    unittest.main()
