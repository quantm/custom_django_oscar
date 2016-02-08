from decimal import Decimal as D
from apps.shipping.methods import FixedPrice, Free
from oscar.apps.shipping.repository import Repository as CoreRepository

##fedex shipping
from fedex.services.rate_service import FedexRateServiceRequest
from fedex.config import FedexConfig


class Repository(CoreRepository):

    def get_shipping_methods(self, user, basket, shipping_addr=None, **kwargs):

            if shipping_addr:
                        config = FedexConfig(key='YvEfQwGwT1TvCU2h', password='eayWJmve6AlmIdLA4CbGvS2sh', account_number='510087763', meter_number='118597992', use_test_server=True)
                        ##rate request
                        rate_request = FedexRateServiceRequest(config)
                        rate_request.RequestedShipment.DropoffType = 'REGULAR_PICKUP'
                        rate_request.RequestedShipment.ServiceType = 'FEDEX_GROUND'
                        rate_request.RequestedShipment.PackagingType = 'YOUR_PACKAGING'
                        rate_request.RequestedShipment.PackageDetail = 'INDIVIDUAL_PACKAGES'

                        # Shipper's address
                        rate_request.RequestedShipment.Shipper.Address.PostalCode = '29631'
                        rate_request.RequestedShipment.Shipper.Address.CountryCode = 'US'
                        rate_request.RequestedShipment.Shipper.Address.Residential = False

                        # Recipient address
                        rate_request.RequestedShipment.Recipient.Address.PostalCode = shipping_addr.postcode
                        rate_request.RequestedShipment.Recipient.Address.CountryCode = shipping_addr.country_id
                        rate_request.RequestedShipment.EdtRequestType = 'NONE'
                        rate_request.RequestedShipment.ShippingChargesPayment.PaymentType = 'SENDER'

                        package1_weight = rate_request.create_wsdl_object_of_type('Weight')
                        # Weight, in LB.
                        package1_weight.Value = 10.0
                        package1_weight.Units = "LB"

                        package1 = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
                        package1.Weight = package1_weight
                        package1.PhysicalPackaging = 'BOX'
                        rate_request.add_package(package1)
                        rate_request.send_request()
                        for rate_detail in rate_request.response.RateReplyDetails[0].RatedShipmentDetails:
                            fedex_price = rate_detail.ShipmentRateDetail.TotalNetFedExCharge.Amount
                        ##set tax here (1.00)
                        methods = [FixedPrice(D(fedex_price), D(fedex_price+1.00))]
                        return self.prime_methods(basket, methods)
            else:
                        methods = [Free()]
                        return self.prime_methods(basket, methods)

    def find_by_code(self, code, basket):
        for method in self.methods:
            if code == method.code:
                return self.prime_method(basket, method)
