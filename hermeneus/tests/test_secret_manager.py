# PROOF: [L3/テスト] <- hermeneus/tests/ Secret Manager 統合のテスト
"""
Hermēneus Secret Manager Integration Tests

Phase 3: Secret Manager (GCP/AWS) の統合テスト
"""

import os
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# モックの設定 (runtimeモジュールをインポートする前にモジュールレベルでモックする)
mock_gcp = MagicMock()
mock_secretmanager = MagicMock()
mock_gcp.secretmanager = mock_secretmanager
sys.modules['google.cloud'] = mock_gcp
sys.modules['google.cloud.secretmanager'] = mock_secretmanager

mock_boto3 = MagicMock()
sys.modules['boto3'] = mock_boto3

import hermeneus.src.runtime as runtime
from hermeneus.src.runtime import _get_secret


def setup_function():
    """各テスト前にキャッシュをクリアする"""
    runtime._SECRET_CACHE.clear()


def test_get_secret_env():
    """環境変数からシークレットを取得できるか"""
    with patch.dict(os.environ, {"TEST_KEY": "test_val"}):
        val = _get_secret("TEST_KEY")
        assert val == "test_val"


def test_get_secret_cache():
    """キャッシュが使われるか"""
    runtime._SECRET_CACHE["TEST_KEY"] = "cached_val"
    val = _get_secret("TEST_KEY")
    assert val == "cached_val"


def test_get_secret_gcp():
    """GCP Secret Manager からシークレットを取得できるか"""
    # 既存の設定を退避または上書き
    mock_client_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.payload.data.decode.return_value = "gcp_secret_val"
    mock_client_instance.access_secret_version.return_value = mock_response
    mock_secretmanager.SecretManagerServiceClient.return_value = mock_client_instance

    with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test_project"}, clear=True):
        val = _get_secret("GCP_TEST_KEY")

        assert val == "gcp_secret_val"
        mock_client_instance.access_secret_version.assert_called_once()
        args, kwargs = mock_client_instance.access_secret_version.call_args
        assert kwargs["request"]["name"] == "projects/test_project/secrets/GCP_TEST_KEY/versions/latest"

        # キャッシュが設定されていることの確認
        assert runtime._SECRET_CACHE["GCP_TEST_KEY"] == "gcp_secret_val"


def test_get_secret_aws():
    """AWS Secrets Manager からシークレットを取得できるか"""
    mock_client_instance = MagicMock()
    mock_client_instance.get_secret_value.return_value = {"SecretString": "aws_secret_val"}
    mock_boto3.client.return_value = mock_client_instance

    with patch.dict(os.environ, {"AWS_REGION": "us-east-1"}, clear=True):
        val = _get_secret("AWS_TEST_KEY")

        assert val == "aws_secret_val"
        mock_boto3.client.assert_called_with('secretsmanager', region_name='us-east-1')
        mock_client_instance.get_secret_value.assert_called_once_with(SecretId="AWS_TEST_KEY")

        # キャッシュが設定されていることの確認
        assert runtime._SECRET_CACHE["AWS_TEST_KEY"] == "aws_secret_val"


def test_get_secret_aws_json():
    """AWS Secrets Manager から JSON 形式のシークレットを取得できるか"""
    mock_client_instance = MagicMock()
    # JSON 形式で返す
    json_val = json.dumps({"AWS_JSON_KEY": "aws_json_secret_val", "other": "val"})
    mock_client_instance.get_secret_value.return_value = {"SecretString": json_val}
    mock_boto3.client.return_value = mock_client_instance

    with patch.dict(os.environ, {"AWS_REGION": "us-east-1"}, clear=True):
        val = _get_secret("AWS_JSON_KEY")

        assert val == "aws_json_secret_val"
        mock_boto3.client.assert_called_with('secretsmanager', region_name='us-east-1')
        mock_client_instance.get_secret_value.assert_called_once_with(SecretId="AWS_JSON_KEY")
