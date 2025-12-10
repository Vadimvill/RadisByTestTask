import abc
import json
from typing import List

from pydantic import BaseModel, Field


class BaseRetailApiModel(abc.ABC):
    @abc.abstractmethod
    def get_str_data(self) -> str:
        pass


class CustomerFilter(BaseModel,BaseRetailApiModel):
    name: str | None
    email: str | None
    date_from: str | None
    date_to: str | None

    def get_str_data(self) -> str:
        params = {
            "filter[name]": self.name,
            "filter[email]": self.email,
            "filter[dateFrom]": self.date_from,
            "filter[dateTo]": self.date_to
        }

        result = ''
        for key, value in params.items():
            if value is not None:
                result += f"{key}={value}&"
        return result.strip('&')


class PaginateParams(BaseModel,BaseRetailApiModel):
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )
    page: int = Field(
        default=1,
        ge=1,
    )

    def get_str_data(self) -> str:
        params = {
            "limit": self.limit,
            "page": self.page
        }
        result = ''
        for key, value in params.items():
            result += f"{key}={value}&"
        return result.strip('&')


class CreateClient(BaseModel,BaseRetailApiModel):
    site: int | None
    first_name: str
    email: str | None
    country_iso: str

    def get_str_data(self) -> str:
        customer_params = {
            "firstName": self.first_name,
            "email": self.email,
            "address": {
                "countryIso": self.country_iso
            }
        }
        json_str = f"customer={json.dumps(customer_params)}"
        result = f"site={self.site}&{json_str}"
        return result


class GetClientsWithParams(PaginateParams, CustomerFilter,BaseRetailApiModel):
    def get_str_data(self) -> str:
        paginate = PaginateParams.get_str_data(self)
        filter = CustomerFilter.get_str_data(self)
        return '&'.join([paginate, filter])


class GetClientOrdersWithParams(PaginateParams,BaseRetailApiModel):
    customer_id: int

    def get_str_data(self) -> str:
        paginate = PaginateParams.get_str_data(self)
        customer_id = f"filter[customerId]={self.customer_id}"
        return '&'.join([customer_id, paginate])


class Order(BaseModel,BaseRetailApiModel):
    customer_id: int
    external_order_ids: List[int]
    number: str | None

    def get_str_data(self) -> str:
        items = []
        for offer_id in self.external_order_ids:
            items.append({
                "offer": {"externalId": offer_id},
                "quantity": 1
            })

        order = {
            "customer": {
                "id": self.customer_id
            },
            "number": self.number,
            "items": items,
        }
        return f"order={json.dumps(order)}"


class OrderPayment(BaseModel,BaseRetailApiModel):
    order_id: int
    amount: float
    type: str

    def get_str_data(self) -> str:
        order = {
            "order": {
                "id": self.order_id
            },
            "amount": self.amount,
            "type": self.type,

        }
        return f"payment={json.dumps(order)}"
