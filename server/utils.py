import websockets

async def find_free_port(coroutine, port = 8081):
    """
    Find a free port 

    Given a port number, checks it and each subsequent number, returning the
    first that is not in use.
    """
    port_in_use_err = 98
    tcp_highest_port = 65535
    while port < tcp_highest_port:
        try:
            async with websockets.serve(coroutine, "localhost", port):
                pass
            return port
        # Catch only the specific error from trying to open a port in use
        except OSError as e: 
            if e.errno == port_in_use_err:
                port += 1
            else: 
                raise e
    # Return None in near-impossible case of no free ports
