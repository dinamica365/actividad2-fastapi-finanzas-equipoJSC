from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _request_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return exc.code, parsed


class ApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.port = _free_port()
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "smart_portfolio_api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(cls.port),
                "--log-level",
                "error",
            ],
            cwd=ROOT_DIR,
        )
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                status, payload = _request_json("GET", f"{cls.base_url}/health")
                if status == 200 and payload.get("api_alive"):
                    return
            except Exception:
                time.sleep(0.5)
        cls.tearDownClass()
        raise RuntimeError("API server did not start in time.")

    @classmethod
    def tearDownClass(cls) -> None:
        process = getattr(cls, "process", None)
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()

    def test_health_reports_model_ready(self) -> None:
        status, payload = _request_json("GET", f"{self.base_url}/health")
        self.assertEqual(status, 200)
        self.assertTrue(payload["api_alive"])
        self.assertTrue(payload["model_available"])
        self.assertEqual(payload["status"], "ok")
        self.assertIn("model_version", payload)

    def test_market_data_returns_local_records(self) -> None:
        status, payload = _request_json("GET", f"{self.base_url}/market-data/BTC-USD")
        self.assertEqual(status, 200)
        self.assertEqual(payload["symbol"], "BTC-USD")
        self.assertEqual(payload["source"], "cache")
        self.assertGreater(len(payload["records"]), 0)
        self.assertIn("close", payload["records"][0])

    def test_model_metadata_returns_expected_fields(self) -> None:
        status, payload = _request_json("GET", f"{self.base_url}/model/metadata")
        self.assertEqual(status, 200)
        self.assertEqual(payload["model_version"], "logistic_momentum_v1")
        self.assertEqual(payload["prediction_horizon"], 1)
        self.assertIn("BTC-USD", payload["symbols_used"])

    def test_predict_returns_up_or_down(self) -> None:
        status, payload = _request_json(
            "POST",
            f"{self.base_url}/predict",
            {
                "symbol": "BTC-USD",
                "prediction_horizon": 1,
                "use_cached_data": True,
            },
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["symbol"], "BTC-USD")
        self.assertIn(payload["prediction"], {"up", "down"})
        self.assertGreaterEqual(payload["probability_up"], 0.0)
        self.assertLessEqual(payload["probability_up"], 1.0)
        self.assertEqual(payload["prediction_horizon"], "next_day")


if __name__ == "__main__":
    unittest.main()
