from braintree.exceptions.braintree_error import BraintreeError

class NotFoundError(BraintreeError):
    """
    Raised when an object is not found in the gateway, such as a Transaction.find("bad_id").

    https://www.braintreepayments.com/docs/python/general/exceptions#not_found_error
    """
    pass
