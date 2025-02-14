def calculate_offset(client_send: float, server_recv: float, server_send: float, client_recv: float) -> float:
    return ((server_recv - client_send) + (server_send - client_recv)) / 2