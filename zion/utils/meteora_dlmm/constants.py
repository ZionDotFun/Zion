from solders.pubkey import Pubkey  # type: ignore

from .helpers import BN

ILM_BASE = Pubkey.from_string("MFGQxwAmB91SwuYX36okv2Qmdc9aMuHTwWGUrp4AtB1");

MAX_BIN_ARRAY_SIZE = BN(70)
BIN_ARRAY_BITMAP_SIZE = BN(512)

LBCLMM_PROGRAM_IDS = {
    "devnet": "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo",
    "localhost": "LbVRzDTvBDEcrthxfZ4RL6yiq3uZw8bS6MwtdY6UhFQ",
    "mainnet-beta": "LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo",
}
