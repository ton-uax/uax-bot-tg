import os
from base64 import b64encode
#from os import EX_CANTCREAT
from pathlib import Path
from tonclient.client import TonClient, DEVNET_BASE_URL, MAINNET_BASE_URL
from tonclient import types
from tonclient.types import Abi


class TonCli(TonClient):
    def __init__(self, test=False):
        net_base_url = MAINNET_BASE_URL
        if test:
            net_base_url = DEVNET_BASE_URL
        self.config = types.ClientConfig()
        self.config.network.server_address = net_base_url
        super().__init__(config=self.config, is_async=False)

    def get_uax_balance(self, address):
        boc = self._wait_account(address)
        balance = self._run_getter(address, self._ABI('TokenWallet'), boc, '_balance')
        return balance['_balance']

    @staticmethod
    def _ABI(name):
        return Abi.from_path(Path.cwd() / 'api' / 'core' / 'apps' / 'ton' / 'abi' / f'{name}.abi.json')

    def _parse_boc(self, boc, what):
        fn = getattr(self.boc, f'parse_{what}')
        return fn(types.ParamsOfParse(boc)).parsed

    def _get_account(self, address):
        return self.net.query_collection(
            types.ParamsOfQueryCollection('accounts', 'boc', {"id": {"eq": address}})
        ).result[0]['boc']

    def _wait_account(self, address):
        return self.net.wait_for_collection(
            types.ParamsOfWaitForCollection('accounts', 'boc', {"id": {"eq": address}})
        ).result['boc']

    def _run_getter(self, address, abi, boc, getter, params=None):
        params = params or {}
        msg = self.abi.encode_message(
            params=types.ParamsOfEncodeMessage(
                abi=abi, signer=types.Signer.NoSigner(), address=address,
                call_set=types.CallSet(function_name=getter, input=params)))
        response = self.tvm.run_tvm(
            params=types.ParamsOfRunTvm(
                message=msg.message, abi=abi, account=boc)).decoded.output
        return response

    def _track_msg_onchain_execution(self, msg_or_params, shard_block_id, abi, tracker_cb):
        if isinstance(msg_or_params, types.ParamsOfEncodeMessage):
            msg = self.abi.encode_message(msg_or_params)
        else:
            msg = msg_or_params

        return self.processing.wait_for_transaction(types.ParamsOfWaitForTransaction(msg.message, shard_block_id, True, abi),
                                                   tracker_cb)

    def _send_onchain(self, msg_params, abi, tracker_cb=None):
        msg = self.abi.encode_message(msg_params)
        shard_block_id = self.processing.send_message(
            types.ParamsOfSendMessage(msg.message, bool(tracker_cb), abi), tracker_cb).shard_block_id
        return msg, shard_block_id

    def _run_onchain(self, address, abi, function_name, params, signer=types.Signer.NoSigner(), wait=True):
        def cb(event, code, err):
            # print(event)
            if code != 100 or err is not None:
                print(code)
                print(err)

        msg_params = types.ParamsOfEncodeMessage(
            abi=abi, signer=signer, address=address,
            call_set=types.CallSet(function_name=function_name, input=params))
        msg, shard_block_id = self._send_onchain(msg_params, abi, cb)
        if wait:
            return self._track_msg_onchain_execution(msg, shard_block_id, abi, cb)
        else:
            return msg, shard_block_id

    def test_net(self):
        CONSOLE = '0:cadfc09ba681f2159e479f031f146090c4cfd1264aeeeaee9e30d67890f9fbc6'

        def deploy_with_token(pubkey, tokens):
            res = self._run_onchain(
                CONSOLE, self._ABI('Console'),
                'deployTokenWalletWithTokens', {'key': f'0x{pubkey}', 'tokens': tokens})

            return f'0:'





