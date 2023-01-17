from typing import List


def validate_json_arguments(request_data, keys: List[str]) -> bool:
    """
    Checks whether JSON contains all required keys.

    Parameters
    ----------
    request_data
        data from JSON
    keys: List[str]
        List of required keys

    Returns
    -------
    JSON_valid: bool
        True if JSON contains all required keys, else False
    """
    if request_data is None:
        return False

    for key in keys:
        if key not in request_data:
            return False
    return True


def check_string(string: str) -> bool:
    """
    Checks whether given argument is nonempty string.

    Parameters
    ----------
    string: str
        given argument

    Returns
    -------
    string_valid: bool
        True if given argument is nonempty string
    """
    if not isinstance(string, str):
        return False
    return string != "" and len(string) <= 100


def stats_coffee_query_to_list(query_result):
    """
    Generates list representing all queried coffee purchases.

    Parameters
    ----------
    query_result
        queried coffee purchases

    Returns
    -------
    queried_purchases
        List of objects representing coffee purchases
    """
    result = []
    for purchase in query_result:
        result.append({
            "user_id": purchase.user_id,
            "machine_id": purchase.machine_id,
            "timestamp": purchase.timestamp
        })
    return result
