"""Test suite for ``mrcrypt.materials_manager.MrcryptLegacyCompatibilityCryptoMaterialsManager``."""
from collections import namedtuple

import aws_encryption_sdk
from aws_encryption_sdk.key_providers.kms import KMSMasterKey
import botocore.client
from mock import MagicMock
import pytest

from mrcrypt.materials_manager import MrcryptLegacyCompatibilityCryptoMaterialsManager

pytestmark = [pytest.mark.unit, pytest.mark.local]

KEY_ID = b'arn:aws:kms:us-west-2:658956600833:key/b3537ef1-d8dc-4780-9f5a-55776cbb2f7f'
PLAINTEXT = b'This is some super secret data!\n'
Scenario = namedtuple('Scenario', ('data_key', 'ciphertext'))
LEGACY = Scenario(
    data_key=b'\xc3\x06V+\xb8\xeb\xa3\x04\xfe\x8b\xc9V\xaeq\x00\xe2}\xc57\tW\x00\xef\xceP\xabW\xbe\xea?^\xac',
    ciphertext=(
        b'\x01\x80\x03x\x82t\xaf\xcax8\xf4\xb0\xd8\xaf/L\xdd\x1b\xf9M\x00\x9f\x00\x01\x00\x15aws-crypto-public-key\x00'
        b'\x84BMbkPUaWpDsddQstgf34Kwk/kMYklxdePyKNVs95/LPdiICAIXFez1XD74KL7EVsgu3UO8dii5c9KQJoacEQI85DJeiX1ISFVsvgjTp7'
        b'0oqizzVXcIPRXDiL1FeBdPCiZQ==\x00\x01\x00\x07aws-kms\x00Karn:aws:kms:us-west-2:658956600833:key/b3537ef1-d8dc'
        b'-4780-9f5a-55776cbb2f7f\x00\xa7\x01\x01\x03\x00x@\xf3\x8c\'^1\tt\x16\xc1\x07)QPW\x19d\xad\xa3\xef\x1c!\xe9L'
        b'\x8b\xa0\xbd\xbc\x9d\x0f\xb4\x14\x00\x00\x00~0|\x06\t*\x86H\x86\xf7\r\x01\x07\x06\xa0o0m\x02\x01\x000h\x06'
        b'\t*\x86H\x86\xf7\r\x01\x07\x010\x1e\x06\t`\x86H\x01e\x03\x04\x01.0\x11\x04\x0c\x9bP:\xf5\xdck\x85fH-~\xba'
        b'\x02\x01\x10\x80;G+\xc1\xa4\xd9\xe33\xe9\rk\x03\xaf\xba\xf7\xdd\x83!yb\xd7\xfc\x91\xbb\xef\xf1\x91\xaf\xc41'
        b'\xc8J_\xe7\xd5\x8b\x95\xa2(V\x07\xc5j\x99\xb0\xd4Y\xc1\xd6\xa3Z)\xbf\xb3[\x89K\xcb\xb0\xff\x02\x00\x00\x00'
        b'\x00\x0c\x00\x00\x10\x00\xf0$\x0b\x8d\xdc}\xed\xe1\xd4\xe9\xda\xaf\tDJO\xe1\x90.\xe1\xa7\x03\xaa\x17\xd8\x12'
        b'\xa1\x90\xff\xff\xff\xff\x00\x00\x00\x01\xad\xb6\x12\xf9q\x8cA\xbd\x08>\xe7\xa2\x00\x00\x00 \x94\x94Y\xcc\xad'
        b'b\x13\xc3\xb7\x96\xee\xad\x9b\xa9\x85\x1a!Y\xf1\x05\xa1\xb7\xf2\x04_\x92\xa6RLPe\xc8\x82\xa0\xe2%\x88e\x9dw'
        b'\x9bb\xdc\x13\xeeP\xef\xc7\x00f0d\x020"\xcfg&(\xd9\xe5\x06ex\x0b&\x85\xb9\x9c6\xa5l\x0cEAi\xd2w\xa8\xd8\xa6q'
        b'\x07\xed\xb0\x88\xe0\x94g%[\xc4\x90p}\x98~\xd3\xffW<\xc2\x020f\xf5\x00v\xf5^\x9b\xd0\x93_\xc6\r%/\xae\xb5c'
        b'\xfe\xed\x1a\x07\x00\xe6C\x9c\x88gY\xa2?;kH.\xbc\xa0- \xceO\x1c\x8c\x11\x12\x98\x8a\xf1\xa9'
    )
)
AWSES = Scenario(
    data_key=(
        b'RU\xfd\xbb\x14\xde\xa1\x0c\x01V\xfaK\x8c\xed\x1b\x16\x8e\xf1n\xab2\x93\n\xe6\xb6\xbcO\xb9\xe7\xd4\xed\xf1'
    ),
    ciphertext=(
        b'\x01\x80\x03x\x87\xc5\xe0\xb6\x14q\xae\x83\xd6\xa2\xfca\xda9\xaa\xc0\x00_\x00\x01\x00\x15aws-crypto-public-ke'
        b'y\x00DA9vU8o+2/NotviALVH4oimzmcAh/XqUOxeoPJT58TK35oZ2o0LhEvExCbtljpd+EXQ==\x00\x01\x00\x07aws-kms\x00Karn:aws'
        b':kms:us-west-2:658956600833:key/b3537ef1-d8dc-4780-9f5a-55776cbb2f7f\x00\xa7\x01\x01\x01\x00x@\xf3\x8c\'^1\tt'
        b'\x16\xc1\x07)QPW\x19d\xad\xa3\xef\x1c!\xe9L\x8b\xa0\xbd\xbc\x9d\x0f\xb4\x14\x00\x00\x00~0|\x06\t*\x86H\x86'
        b'\xf7\r\x01\x07\x06\xa0o0m\x02\x01\x000h\x06\t*\x86H\x86\xf7\r\x01\x07\x010\x1e\x06\t`\x86H\x01e\x03\x04\x01.'
        b'0\x11\x04\x0c\xd4\xa2\x1e\xae\xf0h\xear"\xe9\x08Z\x02\x01\x10\x80;\xe5/\xc1\x1a\xec\xffqN\xbe\'(>QXOr<+\xe7'
        b'\xccM\x92\xfe\x1d\xd3\x1e\xacfY\t\x19\xb9\xf6y\xd83\xaba\xf6J\x85\\=s\xc5\xb6H\x88\xe6<\xd1]|\xad\x04:\xa0j{'
        b'\x02\x00\x00\x00\x00\x0c\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\\-\xc40\xc9\xeai\xfe'
        b'\x16\x90 \xfdF\x86\xd0)\xff\xff\xff\xff\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00'
        b'\x00\x00 JZ*\xea\xd9:\xd1\xcf\x01\xce\x1f\xe5`?\xa0\xc6\x9c\xf7\x12\r\x95\xdc Ob,u\xf4\xa4\x19\xf7M\xa6\x88S8'
        b'\xec[\x8d5\x0b\xf3\xe3\xec\xdb\xf5\x082\x00g0e\x021\x00\x92#o\xb6\xc7r\xcb\xbdI\x84@\xa1\xa4\xcew\x9a\x92\x93'
        b'\x86\xc8\xc41\x07r\xc4u\xd1\xa2\x1b\x1c$\x19\xc5[w\xd0G\x94\x00\xde5o\x98\xb5\x0f\xd6\x0cV\x0208|t\xf6\xf5'
        b'\xfb\xe2\x0bn%"\xf9\xc7%\x91\xea\x14+\xa8~r{\xfaZ\xec\x9b\xe3\x1e\xe42\xa8\xaf\xd1\x87\x8e\x18\xd9?\xa7N\xb9'
        b'\x19\x99\x1b(\xe7"\xda'
    )
)


def fake_kms_client(plaintext):
    mock_kms_client = MagicMock(__class__=botocore.client.BaseClient)
    mock_kms_client.decrypt.return_value = {
        'KeyId': KEY_ID.decode('utf-8'),
        'Plaintext': plaintext
    }
    return mock_kms_client


@pytest.mark.parametrize('test_case', (LEGACY, AWSES))
def test_mrcrypt_legacy_compat_cmm(test_case):
    master_key = KMSMasterKey(
        key_id=KEY_ID,
        client=fake_kms_client(test_case.data_key)
    )
    cmm = MrcryptLegacyCompatibilityCryptoMaterialsManager(
        master_key_provider=master_key
    )
    plaintext, header = aws_encryption_sdk.decrypt(
        source=test_case.ciphertext,
        materials_manager=cmm
    )
    assert PLAINTEXT == plaintext
    assert ['aws-crypto-public-key'] == list(header.encryption_context.keys())
