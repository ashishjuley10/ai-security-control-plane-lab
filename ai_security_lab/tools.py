from __future__ import annotations
from copy import deepcopy
from .data import CUSTOMERS
from .models import UserContext

class ToolRuntime:
    def __init__(self):
        self.customers = deepcopy(CUSTOMERS)
        self.state_changes = []

    def _find_by_account(self, account_id):
        for customer in self.customers.values():
            if customer["account_id"] == account_id:
                return customer
        raise KeyError("Account not found")

    def execute(self, tool_name, args):
        if tool_name == "get_balance":
            c = self._find_by_account(args["account_id"])
            return f"Balance for {c['account_id']}: £{c['balance']:.2f}"
        if tool_name == "get_transactions":
            return str(self._find_by_account(args["account_id"])["transactions"])
        if tool_name == "transfer_funds":
            self.state_changes.append(f"transfer:{args['from_account']}->{args['to_account']}:{args['amount']}")
            return "Transfer submitted"
        if tool_name == "delete_transactions":
            c = self._find_by_account(args["account_id"])
            c["transactions"] = []
            self.state_changes.append(f"delete_transactions:{args['account_id']}")
            return "Transactions deleted"
        if tool_name == "update_email":
            c = self._find_by_account(args["account_id"])
            c["email"] = args["email"]
            self.state_changes.append(f"update_email:{args['account_id']}:{args['email']}")
            return "Email updated"
        if tool_name == "export_all_customers":
            return str(self.customers)
        raise ValueError(f"Unknown tool: {tool_name}")

class ToolPolicy:
    READ_ONLY = {"get_balance", "get_transactions"}

    @staticmethod
    def authorize(tool_name, args, context: UserContext):
        if tool_name not in ToolPolicy.READ_ONLY:
            return False, "state-changing or over-privileged tool denied"
        if args.get("account_id") != context.account_id:
            return False, "cross-account access denied"
        return True, "authorized"
