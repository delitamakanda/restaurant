def response_handler(data, status_code=200, message="Success"):
    """
    Function to handle API responses.

    Args:
        data (dict): Response data.
        status_code (int, optional): HTTP status code. Defaults to 200.
        message (str, optional): Response message. Defaults to "Success".

    Returns:
        dict: API response.
    """
    return {"status_code": status_code, "message": message, "data": data}
