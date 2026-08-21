import ipaddress


# ---------------------------------------------------------
# PROTECTED ASSETS
# ---------------------------------------------------------

# These hosts must never be quarantined.
PROTECTED_HOSTS = [
    "trading-prod-01",
    "trading-prod-02",
    "market-data-relay-01",
    "market-data-relay-02",
    "ceo-laptop",
    "cfo-laptop",
    "ciso-laptop"
]


# These IP addresses must never be blocked.
PROTECTED_IPS = [
    "198.51.100.10",  # Reuters market-data
    "198.51.100.11",  # Bloomberg terminal
    "192.0.2.55",     # Prime broker API
    "192.0.2.56"      # Clearing-house webhook
]


# ---------------------------------------------------------
# HOOK 1: LOGGING
# ---------------------------------------------------------

def logging_hook(tool_name, tool_input):
    """
    Logs every attempted tool call.

    This hook observes the action but never blocks it.
    """

    input_keys = list(tool_input.keys())

    print(
        f"[LOG] Tool requested: {tool_name} | "
        f"Input keys: {input_keys}"
    )

    return True, ""


# ---------------------------------------------------------
# HOOK 2: ARGUMENT VALIDATION
# ---------------------------------------------------------

def arg_validation_hook(tool_name, tool_input):
    """
    Checks whether required tool arguments are present and valid.
    """

    if not isinstance(tool_input, dict):
        return False, "Tool input must be a dictionary."

    if tool_name == "block_ip":
        ip_value = tool_input.get("ip")

        if not ip_value:
            return False, (
                "Argument validation policy: "
                "block_ip requires a non-empty 'ip' value."
            )

        try:
            ipaddress.IPv4Address(ip_value)
        except ipaddress.AddressValueError:
            return False, (
                "Argument validation policy: "
                f"'{ip_value}' is not a valid IPv4 address."
            )

    elif tool_name == "quarantine_host":
        hostname = tool_input.get("hostname")

        if not hostname:
            return False, (
                "Argument validation policy: "
                "quarantine_host requires a non-empty "
                "'hostname' value."
            )

    elif tool_name == "disable_user":
        username = tool_input.get("username")

        if not username:
            return False, (
                "Argument validation policy: "
                "disable_user requires a non-empty "
                "'username' value."
            )

    elif tool_name == "query_siem":
        query = tool_input.get("query")

        if not query:
            return False, (
                "Argument validation policy: "
                "query_siem requires a non-empty 'query' value."
            )

    return True, ""


# ---------------------------------------------------------
# HOOK 3: PROTECTED-ASSET POLICY
# ---------------------------------------------------------

def protected_asset_hook(tool_name, tool_input):
    """
    Blocks actions against protected production assets,
    protected network addresses, and executive accounts.
    """

    if tool_name == "quarantine_host":
        hostname = tool_input.get("hostname", "").lower()

        for protected_host in PROTECTED_HOSTS:
            if hostname == protected_host.lower():
                return False, (
                    "Protected-host policy: "
                    f"'{hostname}' is a protected production asset "
                    "and cannot be quarantined."
                )

    elif tool_name == "block_ip":
        ip_value = tool_input.get("ip", "")

        if ip_value in PROTECTED_IPS:
            return False, (
                "Protected-IP policy: "
                f"'{ip_value}' is an approved business-critical IP "
                "and cannot be blocked."
            )

    elif tool_name == "disable_user":
        username = tool_input.get("username", "").lower()

        protected_executives = [
            "ceo",
            "cfo",
            "ciso"
        ]

        if (
            username in protected_executives
            or username.endswith("@northgate-exec")
        ):
            return False, (
                "Executive-account policy: "
                f"'{username}' requires dual approval "
                "and cannot be disabled automatically."
            )

    return True, ""


# ---------------------------------------------------------
# SIMULATED TOOL FUNCTIONS
# ---------------------------------------------------------

def simulate_block_ip(tool_input):
    """
    Simulates adding an IP address to a firewall deny-list.
    """

    ip_value = tool_input["ip"]

    return (
        f"[FIREWALL] IP {ip_value} added to the deny-list "
        "(simulated)."
    )


def simulate_quarantine_host(tool_input):
    """
    Simulates isolating a host from the network.
    """

    hostname = tool_input["hostname"]

    return (
        f"[EDR] Host {hostname} isolated from the network "
        "(simulated)."
    )


def simulate_disable_user(tool_input):
    """
    Simulates disabling a user account.
    """

    username = tool_input["username"]

    return (
        f"[IDENTITY] User account {username} disabled "
        "(simulated)."
    )


def simulate_query_siem(tool_input):
    """
    Simulates running a security query.
    """

    query = tool_input["query"]

    return (
        f"[SIEM] Query executed successfully: {query} "
        "(simulated)."
    )


# Maps tool names to their simulator functions.
DEMO_TOOLS = {
    "block_ip": simulate_block_ip,
    "quarantine_host": simulate_quarantine_host,
    "disable_user": simulate_disable_user,
    "query_siem": simulate_query_siem
}


# ---------------------------------------------------------
# TOOL RUNNER
# ---------------------------------------------------------

def run_tool(
    tool_name,
    tool_input,
    tool_fn,
    hooks,
    audit_log
):
    """
    Passes a requested action through each hook.

    If any hook blocks the action, the real tool does not run.
    If every hook allows the action, the tool executes.
    """

    for hook in hooks:
        allowed, reason = hook(tool_name, tool_input)

        if not allowed:
            audit_log.append(
                {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "status": "BLOCKED",
                    "reason": reason
                }
            )

            print(f"[BLOCKED] {tool_name}: {reason}")

            return f"BLOCKED by policy: {reason}"

    # Every hook passed, so record and run the real tool.
    audit_log.append(
        {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "status": "allowed",
            "reason": ""
        }
    )

    result = tool_fn(tool_input)

    print(f"[ALLOWED] {tool_name}: {result}")

    return result


# ---------------------------------------------------------
# AUDIT LOG
# ---------------------------------------------------------

def print_audit_log(audit_log):
    """
    Prints every attempted action for audit review.
    """

    print("\n" + "=" * 70)
    print("SOX / SOC2 TOOL AUDIT LOG")
    print("=" * 70)

    if not audit_log:
        print("No tool attempts were recorded.")
        return

    for number, entry in enumerate(audit_log, start=1):
        print(f"\nAttempt #{number}")
        print(f"Tool:   {entry['tool_name']}")
        print(f"Input:  {entry['tool_input']}")
        print(f"Status: {entry['status']}")

        if entry["reason"]:
            print(f"Reason: {entry['reason']}")

    print("\n" + "=" * 70)
    print(f"Total attempts recorded: {len(audit_log)}")
    print("=" * 70)


# ---------------------------------------------------------
# STANDALONE DEMONSTRATION
# ---------------------------------------------------------

if __name__ == "__main__":
    audit_log = []

    hooks = [
        logging_hook,
        arg_validation_hook,
        protected_asset_hook
    ]

    attempted_calls = [
        # Allowed: suspicious analyst laptop.
        {
            "tool_name": "quarantine_host",
            "tool_input": {
                "hostname": "research-analyst-laptop-04"
            }
        },

        # Policy block: protected trading server.
        {
            "tool_name": "quarantine_host",
            "tool_input": {
                "hostname": "trading-prod-01"
            }
        },

        # Allowed: suspicious external IP.
        {
            "tool_name": "block_ip",
            "tool_input": {
                "ip": "203.0.113.47"
            }
        },

        # Validation block: malformed IP address.
        {
            "tool_name": "block_ip",
            "tool_input": {
                "ip": "999.999.999.999"
            }
        },

        # Policy block: protected market-data IP.
        {
            "tool_name": "block_ip",
            "tool_input": {
                "ip": "198.51.100.11"
            }
        },

        # Validation block: empty username.
        {
            "tool_name": "disable_user",
            "tool_input": {
                "username": ""
            }
        },

        # Executive-account block.
        {
            "tool_name": "disable_user",
            "tool_input": {
                "username": "ceo"
            }
        },

        # Allowed: SIEM query.
        {
            "tool_name": "query_siem",
            "tool_input": {
                "query": (
                    "alert_id=NG-2027-1142 "
                    "destination_ip=203.0.113.47"
                )
            }
        }
    ]

    print("=" * 70)
    print("TOOL HOOK ENGINE DEMONSTRATION")
    print("=" * 70)

    for attempted_call in attempted_calls:
        tool_name = attempted_call["tool_name"]
        tool_input = attempted_call["tool_input"]
        tool_fn = DEMO_TOOLS[tool_name]

        print("\n" + "-" * 70)
        print(f"Attempting: {tool_name}")

        result = run_tool(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_fn=tool_fn,
            hooks=hooks,
            audit_log=audit_log
        )

        print(f"Result: {result}")

    print_audit_log(audit_log)