from lib.braintree.add_on_gateway import AddOnGateway
from lib.braintree.address_gateway import AddressGateway
from lib.braintree.credit_card_gateway import CreditCardGateway
from lib.braintree.customer_gateway import CustomerGateway
from lib.braintree.discount_gateway import DiscountGateway
from lib.braintree.merchant_account_gateway import MerchantAccountGateway
from lib.braintree.plan_gateway import PlanGateway
from lib.braintree.settlement_batch_summary_gateway import SettlementBatchSummaryGateway
from lib.braintree.subscription_gateway import SubscriptionGateway
from lib.braintree.transaction_gateway import TransactionGateway
from lib.braintree.transparent_redirect_gateway import TransparentRedirectGateway
from lib.braintree.credit_card_verification_gateway import CreditCardVerificationGateway
from lib.braintree.webhook_notification_gateway import WebhookNotificationGateway
from lib.braintree.webhook_testing_gateway import WebhookTestingGateway

class BraintreeGateway(object):
    def __init__(self, config):
        self.config = config
        self.add_on = AddOnGateway(self)
        self.address = AddressGateway(self)
        self.credit_card = CreditCardGateway(self)
        self.customer = CustomerGateway(self)
        self.discount = DiscountGateway(self)
        self.merchant_account = MerchantAccountGateway(self)
        self.plan = PlanGateway(self)
        self.settlement_batch_summary = SettlementBatchSummaryGateway(self)
        self.subscription = SubscriptionGateway(self)
        self.transaction = TransactionGateway(self)
        self.transparent_redirect = TransparentRedirectGateway(self)
        self.verification = CreditCardVerificationGateway(self)
        self.webhook_notification = WebhookNotificationGateway(self)
        self.webhook_testing = WebhookTestingGateway(self)
