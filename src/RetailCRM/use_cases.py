from enum import Enum

from src.RetailCRM.schemas import GetClientsWithParams, CreateClient, GetClientOrdersWithParams, Order, OrderPayment
from src.RetailCRM.utils import httpx_request, RequestTypes
from src.config import settings


class EndpointURL(Enum):
    GET_CLIENTS_LIST = "/api/v5/customers"
    CREATE_CLIENT = "/api/v5/customers/create"
    GET_CLIENTS_ORDERS = "/api/v5/orders"
    MAKE_ORDER = "/api/v5/orders/create"
    MAKE_PAYMENT = "/api/v5/orders/payments/create"


class UserUseCases:
    async def get_clients_list(self, data: GetClientsWithParams):
        url = f'{settings.BASE_URL}{EndpointURL.GET_CLIENTS_LIST.value}'
        return await httpx_request(url=url, params=data.get_str_data())

    async def create_client(self, data: CreateClient):
        url = f'{settings.BASE_URL}{EndpointURL.CREATE_CLIENT.value}'
        return await httpx_request(url=url, data=data.get_str_data(), request_type=RequestTypes.POST)

    async def get_client_orders(self, data: GetClientOrdersWithParams):
        url = f'{settings.BASE_URL}{EndpointURL.GET_CLIENTS_ORDERS.value}'
        return await httpx_request(url=url, params=data.get_str_data())

    async def make_order(self, data: Order):
        url = f'{settings.BASE_URL}{EndpointURL.MAKE_ORDER.value}'
        return await httpx_request(url=url, data=data.get_str_data(), request_type=RequestTypes.POST)

    async def make_payment(self, data: OrderPayment):
        url = f'{settings.BASE_URL}{EndpointURL.MAKE_PAYMENT.value}'
        return await httpx_request(url=url, data=data.get_str_data(), request_type=RequestTypes.POST)
