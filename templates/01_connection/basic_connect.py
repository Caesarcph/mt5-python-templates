import MetaTrader5 as mt5

def connect_mt5(
    path: str = None,
    login: int = None,
    password: str = None,
    server: str = None,
    timeout: int = 60000
) -> bool:
    """
    Connect to MT5 terminal with comprehensive error handling.
    
    Args:
        path: Path to terminal64.exe (auto-detect if None)
        login: Account number (use terminal default if None)
        password: Account password
        server: Broker server name
        timeout: Connection timeout in ms
    
    Returns:
        True if connected successfully
    """
    # Build kwargs dynamically to avoid passing None for arguments that don't accept it
    # Although mt5.initialize handles None for path, others might be tricky.
    # The safest way is to pass what is provided.
    kwargs = {'timeout': timeout}
    if path: kwargs['path'] = path
    if login: kwargs['login'] = login
    if password: kwargs['password'] = password
    if server: kwargs['server'] = server

    # Initialize MT5
    if not mt5.initialize(**kwargs):
        error = mt5.last_error()
        print(f"MT5 initialization failed: {error}")
        return False
    
    # Verify connection
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to get account info")
        mt5.shutdown()
        return False
    
    print(f"Connected to {account_info.server}")
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:,.2f}")
    print(f"Leverage: 1:{account_info.leverage}")
    
    return True

def disconnect_mt5():
    """Safely disconnect from MT5."""
    mt5.shutdown()
    print("Disconnected from MT5")

# Usage
if __name__ == "__main__":
    if connect_mt5():
        # Your trading logic here
        disconnect_mt5()
