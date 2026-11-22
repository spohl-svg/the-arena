"""
THE ARENA - ECONOMIC TREASURY & RESOURCE ACCOUNTING
Tracks compute credits, bounty revenues, neon billboard leases, and monument stakes.
"""

import json
from datetime import datetime
from pathlib import Path

TREASURY_FILE = Path("town_treasury.json")

class TownTreasury:
    def __init__(self, treasury_file: Path = TREASURY_FILE):
        self.file = treasury_file
        self._ensure_init()

    def _ensure_init(self):
        if not self.file.exists():
            data = {
                "balance_credits": 1000.0,
                "total_earned": 0.0,
                "total_spent": 0.0,
                "ledger": [],
                "billboard_leases": [
                    {
                        "slot": "MILE_0_MARQUEE",
                        "sponsor": "Sovereign Arena Founder",
                        "text": "DREAM. BUILD. TRY. ENJOY.",
                        "rate_per_cycle": 0.0,
                        "expires_cycle": 999999
                    }
                ],
                "monuments": []
            }
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    def load(self) -> dict:
        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def deposit(self, amount: float, reason: str, entity: str) -> float:
        data = self.load()
        data["balance_credits"] += amount
        data["total_earned"] += amount
        entry = {
            "type": "DEPOSIT",
            "amount": amount,
            "entity": entity,
            "reason": reason,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "new_balance": data["balance_credits"]
        }
        data["ledger"].append(entry)
        self.save(data)
        return data["balance_credits"]

    def lease_billboard(self, slot_id: str, sponsor: str, text: str, cycles: int, fee: float) -> dict:
        data = self.load()
        data["balance_credits"] += fee
        data["total_earned"] += fee
        lease = {
            "slot": slot_id,
            "sponsor": sponsor,
            "text": text,
            "duration_cycles": cycles,
            "fee_paid": fee,
            "leased_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data["billboard_leases"].append(lease)
        data["ledger"].append({
            "type": "BILLBOARD_LEASE",
            "amount": fee,
            "entity": sponsor,
            "reason": f"Leased billboard '{slot_id}' for {cycles} cycles",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "new_balance": data["balance_credits"]
        })
        self.save(data)
        return lease

    def get_summary(self) -> dict:
        data = self.load()
        return {
            "balance": data["balance_credits"],
            "total_earned": data["total_earned"],
            "active_billboards": len(data.get("billboard_leases", [])),
            "monuments_minted": len(data.get("monuments", []))
        }

if __name__ == "__main__":
    t = TownTreasury()
    print("Treasury Status:", t.get_summary())
