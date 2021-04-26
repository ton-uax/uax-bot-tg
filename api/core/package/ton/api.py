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
        self.console = ' '
        if test:
            net_base_url = DEVNET_BASE_URL
            self.CONSOLE = "0:10677a33d3a5edcb4b39a6beb43a124e73c62c70cbb99ed4f4e9d4b29c22f8be"
            self.ROOT = "0:397b4df5409c29d1c5ccc00f94706b9f025054262a509c827a9b99c270b99128"
            self.UAX_CODE_HASH = "5a2e419f76e68aa8fbd8f6dfba9c25c5fedc82c76801ab62c87b0ae7a738b4f2"
            self.MEDIUM = "0:f4e70848721e239245c6ab07bdae957021fa1a2ae421fdbc3f7e0467b5cec99e"
	bar = "foo"
        self.config = types.ClientConfig()
        self.config.network.server_address = net_base_url
        super().__init__(config=self.config, is_async=False)

    def deploy_with_key(self, pubkey):
        res = self._run_onchain(
            self.CONSOLE, self._ABI("Console"),
            "deployTokenWalletsWithKeys", {"keys": [f'0x{pubkey}']})
        account = self._make_account(self._TVC('TokenWallet'), self._ABI('TokenWallet'), pubkey)
        return f'0:{account.id}'

    def create_mnemonic_from_random(self):
        mnemonic = self.crypto.mnemonic_from_random(params=types.ParamsOfMnemonicFromRandom())
        return mnemonic.phrase

    def mnemonic_derive_sign_keys(self, phrase):
        params = types.ParamsOfMnemonicDeriveSignKeys(phrase=phrase)
        keypair = self.crypto.mnemonic_derive_sign_keys(
            params=params)
        return keypair

    def get_uax_balance(self, address):
        try:
            boc = self._wait_account(address)
        except:
            return 0
        balance = self._run_getter(address, self._ABI("TokenWallet"), boc, "_balance")
        return balance['_balance']

    def check_address(self, address):
        code_hash = self._query_account({'id': {'eq': address}}, 'code_hash')
        return code_hash == self.UAX_CODE_HASH

    def get_address(self, pubkey, wc=0):
        account = self._make_account(self._TVC('TokenWallet'), self._ABI('TokenWallet'), pubkey)
        return f'{wc}:{account.id}'

    def get_fee(self):
        params = {}
        msg = self.abi.encode_message(
            params=types.ParamsOfEncodeMessage(
                abi=self._ABI("Medium"), signer=types.Signer.NoSigner(), address=self.MEDIUM,
                call_set=types.CallSet(function_name="getStats", input=params)))
        response = self.tvm.run_tvm(
            params=types.ParamsOfRunTvm(
                message=msg.message, abi=self._ABI("Medium"), account=self._get_account(self.MEDIUM))).decoded.output
        return response["transferFee"]

    def _query_account(self, query, fields: types.Union[str, types.List[str]]):
        if isinstance(fields, types.List):
            fields = ','.join(fields)
        single_field = False
        if ',' not in fields:
            single_field = True
        result = self.net.query_collection(types.ParamsOfQueryCollection(
            'accounts', fields, query)).result
        if not result:
            return
        ret = result[0]
        if single_field:
            ret = ret[fields]
        return ret

    def send_tx(self,
                address_from: str,
                keypair: types.KeyPair,
                to: str,
                value: int):

        self._run_onchain(
            address_from, self._ABI('TokenWallet'), 'transferTokensExt', {"to": to, "val": value},
            types.Signer.Keys(keypair), wait=False
        )

    def get_keypair_from_mnemonic(self, mnemonic, child_index):
        master_xprv = self._get_master_xprv_from_mnemonic(mnemonic)
        hdkey = self.crypto.hdkey_derive_from_xprv(
            params=types.ParamsOfHDKeyDeriveFromXPrv(xprv=master_xprv, child_index=child_index, hardened=False))

        public = self.crypto.hdkey_public_from_xprv(params=types.ParamsOfHDKeyPublicFromXPrv(xprv=hdkey.xprv)).public
        secret = self.crypto.hdkey_secret_from_xprv(params=types.ParamsOfHDKeySecretFromXPrv(xprv=hdkey.xprv)).secret
        return types.KeyPair(public=public, secret=secret)

    def _get_master_xprv_from_mnemonic(self, mnemonic):
        params = types.ParamsOfHDKeyXPrvFromMnemonic(phrase=mnemonic)
        result = self.crypto.hdkey_xprv_from_mnemonic(params=params)
        return result.xprv

    @staticmethod
    def _ABI(name):
        return Abi.from_path(Path.cwd() / 'core' / 'package' / 'ton' / 'abi' / f'{name}.abi.json')

    @staticmethod
    def _TVC(name):
        path = (Path.cwd() / 'core' / 'package' / 'ton' / 'tvc' / f'{name}.tvc')
        return b64encode(path.read_bytes()).decode()

    def _parse_boc(self, boc, what):
        fn = getattr(self.boc, f'parse_{what}')
        return fn(types.ParamsOfParse(boc)).parsed

    def _get_account(self, address):
        return self.net.query_collection(
            types.ParamsOfQueryCollection('accounts', 'boc', {"id": {"eq": address}})
        ).result[0]['boc']

    def _make_account(self, tvc, abi, pubkey, init_data=None):
        init_data = init_data or {}
        src = types.StateInitSource.Tvc(tvc, pubkey, types.StateInitParams(abi, {}))
        account = self.abi.encode_account(types.ParamsOfEncodeAccount(src, 0, 0, 0))
        return account

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

    # Testnet method
    def deploy_with_token(self, pubkey, tokens):
        res = self._run_onchain(
            self.CONSOLE, self._ABI("Console"),
            "deployTokenWalletWithTokens", {"key": f"0x{pubkey}", "tokens": tokens})
        account = self._make_account(self._TVC('TokenWallet'), self._ABI('TokenWallet'), pubkey)
        return f'0:{account.id}'





