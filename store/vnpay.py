import hmac
import hashlib
import urllib.parse


def hmacsha512(key, data):
    return hmac.new(
        key.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()


def build_payment_url(payment_url, params, secret_key):
    params = {
        k: str(v)
        for k, v in params.items()
        if v not in [None, ""]
        and k not in ["vnp_SecureHash", "vnp_SecureHashType"]
    }

    sorted_params = sorted(params.items())

    query_string = "&".join(
        f"{urllib.parse.quote_plus(k)}={urllib.parse.quote_plus(v)}"
        for k, v in sorted_params
    )

    secure_hash = hmacsha512(secret_key, query_string)

    return f"{payment_url}?{query_string}&vnp_SecureHash={secure_hash}"


def verify_vnpay_signature(data, secret_key):
    secure_hash = data.get("vnp_SecureHash")

    if not secure_hash:
        return False

    params = data.copy()
    params.pop("vnp_SecureHash", None)
    params.pop("vnp_SecureHashType", None)

    params = {
        k: str(v)
        for k, v in params.items()
        if v not in [None, ""]
    }

    sorted_params = sorted(params.items())

    query_string = "&".join(
        f"{urllib.parse.quote_plus(k)}={urllib.parse.quote_plus(v)}"
        for k, v in sorted_params
    )

    check_hash = hmacsha512(secret_key, query_string)

    return hmac.compare_digest(
        check_hash.lower(),
        secure_hash.lower()
    )

