
def get_address(server: str, port: int) -> str:
    """Combines a server and a port to form an address.

    Parameters
    ----------
    server : str
        Hostname of the server (e.g. "localhost").
    port : int
        Which port to connect to on the host.

    Returns
    -------
    str
        A fully-formed address to conenct to (e.g. localhost:8081).
    """
    address = f"{server}:{port!s}"
    return address
