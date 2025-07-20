from __future__ import annotations

from datetime import datetime
from typing import Callable, Literal, Optional, Union
from urllib import parse

import requests

import frappe
from frappe.integrations.utils import create_request_log
from frappe.model.document import Document

from ..logger import etims_logger
from ..utils import update_last_request_date, update_navari_settings_with_token, reset_auth_password
from .remote_response_status_handlers import on_slade_error


class BaseEndpointsBuilder:
    """Abstract Endpoints Builder class"""

    def __init__(self) -> None:
        self.integration_request: str | Document | None = None
        self.error: str | Exception | None = None
        self._observers: list[ErrorObserver] = []
        self.doctype: str | Document | None = None
        self.document_name: str | None = None

    def attach(self, observer: ErrorObserver) -> None:
        """Attach an observer

        Args:
            observer (AbstractObserver): The observer to attach
        """
        self._observers.append(observer)

    def notify(self) -> None:
        """Notify all attached observers."""
        for observer in self._observers:
            observer.update(self)


class ErrorObserver:
    """Error observer class."""

    def update(self, notifier: BaseEndpointsBuilder) -> None:
        """Reacts to event from notifier

        Args:
            notifier (AbstractEndpointsBuilder): The event notifier object
        """
        if notifier.error:
            # TODO: Check why integration log is never updated
            update_integration_request(
                notifier.integration_request.name,
                status="Failed",
                output=None,
                error=notifier.error,
            )
            etims_logger.exception(notifier.error, exc_info=True)
            frappe.log_error(
                title="Fatal Error",
                message=notifier.error,
                reference_doctype=notifier.doctype,
                reference_name=notifier.document_name,
            )
            frappe.throw(
                """A Fatal Error was Encountered.
                Please check the Error Log for more details""",
                notifier.error,
                title="Fatal Error",
            )


class EndpointsBuilder(BaseEndpointsBuilder):
    """
    Base Endpoints Builder class.
    This class harbours common functionalities when communicating with etims servers
    """

    def __init__(self) -> None:
        super().__init__()
        self._url: str | None = None
        self._request_description: str | None = None
        self._payload: dict | None = None
        self._settings: dict | None = None
        self._headers: dict | None = None
        self._method: Literal["GET", "POST", "PATCH", "PUT"] | None = None
        self._success_callback_handler: Callable | None = None
        self._error_callback_handler: Callable | None = None

        self.attach(ErrorObserver())

    @property
    def method(self) -> Literal["GET", "POST", "PATCH", "PUT"] | None:
        """The HTTP method to use for the request."""
        return self._method

    @method.setter
    def method(self, new_method: Literal["GET", "POST", "PATCH", "PUT"]) -> None:
        self._method = new_method

    @property
    def url(self) -> str | None:
        return self._url

    @url.setter
    def url(self, new_url: str) -> None:
        self._url = new_url

    @property
    def route_path(self) -> str | None:
        return self._route_path

    @route_path.setter
    def route_path(self, new_route_path: str) -> None:
        self._route_path = new_route_path

    @property
    def request_description(self) -> str | None:
        return self._request_description

    @request_description.setter
    def request_description(self, new_request_description: str) -> None:
        self._request_description = new_request_description

    @property
    def payload(self) -> dict | None:
        return self._payload

    @payload.setter
    def payload(self, new_payload: dict) -> None:
        self._payload = new_payload
        
    @property
    def settings(self) -> dict | None:
        return self._settings
    
    @settings.setter
    def settings(self, new_settings: dict) -> None:
        self._settings = new_settings

    @property
    def headers(self) -> dict | None:
        return self._headers

    @headers.setter
    def headers(self, new_headers: dict) -> None:
        self._headers = new_headers

    @property
    def success_callback(self) -> Callable | None:
        return self._success_callback_handler

    @success_callback.setter
    def success_callback(self, callback: Callable) -> None:
        self._success_callback_handler = callback

    @property
    def error_callback(self) -> Callable | None:
        return self._error_callback_handler

    @error_callback.setter
    def error_callback(
        self,
        callback: Callable[[dict | str, str, str, str], None],
    ) -> None:
        self._error_callback_handler = callback

    def refresh_token(self) -> str:
        """Fetch a new token and update the headers."""
        try:
            settings = update_navari_settings_with_token(self._settings.name)

            if settings:
                new_token = settings.access_token
                self._headers["Authorization"] = f"Bearer {new_token}"
                return new_token
            else:
                frappe.throw(
                    "Failed to refresh token",
                    frappe.AuthenticationError,
                )
        except requests.exceptions.RequestException as error:
            frappe.throw(f"Error refreshing token: {error}", frappe.AuthenticationError)

    def make_remote_call(
        self,
        doctype: Document | str | None = None,
        document_name: str | None = None,
        retrying: bool = False,
    ) -> str | None:
        """Handles communication to Slade360 servers."""
        if (
            self._url is None
            or self._headers is None
            or self._method is None
            or self._success_callback_handler is None
        ):
            frappe.throw(
                """Please ensure all required parameters (URL, headers, method, success, and error callbacks) are set.""",
                frappe.MandatoryError,
                title="Setup Error",
                is_minimizable=True,
            )

        self.doctype, self.document_name = doctype, document_name
        parsed_url = parse.urlparse(self._url)
        route_path = f"/{parsed_url.path.split('/')[-1]}"

        if not retrying:
            try:
                self.integration_request = create_request_log(
                    data=self._payload,
                    request_description=self._request_description,
                    is_remote_request=True,
                    service_name=self._request_description,
                    request_headers=self._headers,
                    url=self._url,
                    reference_docname=document_name,
                    reference_doctype=doctype,
                )
            except frappe.LinkValidationError:
                # Retry without passing reference_docname if document doesn't exist
                self.integration_request = create_request_log(
                    data=self._payload,
                    request_description=self._request_description,
                    is_remote_request=True,
                    service_name=self._request_description,
                    request_headers=self._headers,
                    url=self._url,
                    reference_doctype=doctype,
                )

        try:
            if self._method == "POST":
                response = requests.post(
                    self._url, json=self._payload, headers=self._headers
                )
            elif self._method == "GET":
                # self._payload["page_size"] = 15000
                response = requests.get(
                    self._url, headers=self._headers, params=self._payload
                )

            elif self._method == "PATCH":
                patch_id = self._payload.pop("id", None)
                if patch_id and f"/{patch_id}/" not in self._url:
                    self._url = f"{self._url.rstrip('/')}/{patch_id}/"
                response = requests.patch(
                    self._url, json=self._payload, headers=self._headers
                )
            elif self._method == "PUT":
                put_id = self._payload.pop("id", None)
                if put_id and f"/{put_id}/" not in self._url:
                    self._url = f"{self._url.rstrip('/')}/{put_id}/"
                response = requests.put(
                    self._url, json=self._payload, headers=self._headers
                )

            response_data = get_response_data(response)
            update_last_request_date(datetime.now(), self._route_path)

            if response.status_code in {200, 201}:
                self._success_callback_handler(
                    response=response_data, document_name=document_name, doctype=doctype
                )

                current_page = response_data.get("current_page", None)
                total_pages = response_data.get("total_pages", 0)

                update_integration_request(
                    self.integration_request.name,
                    status="Completed",
                    output=str(response_data),
                    error=None,
                    request_description=(
                        f"Page {current_page} of {total_pages}"
                        if int(total_pages) > 1
                        else None
                    ),
                )
            else:
                if isinstance(response_data, str):
                    error = response_data
                elif isinstance(response_data, list):
                    error = response_data[0]
                else:
                    error = str(response_data)
                    
                if "could not decode json: Expecting value: line 1 column 1 (char 0)" in error:
                    reset_auth_password(self._settings.name)
                    
                update_integration_request(
                    self.integration_request.name,
                    status="Failed",
                    output=None,
                    error=error,
                )
                on_slade_error(
                    response_data,
                    url=route_path,
                    doctype=doctype,
                    document_name=document_name,
                )
                if self._error_callback_handler:
                    self._error_callback_handler(
                        response_data,
                        url=route_path,
                        doctype=doctype,
                        document_name=document_name,
                    )
                    
                if response.status_code == 401 and not retrying:
                    # Optionally, you can refresh token and retry here if needed
                    self.refresh_token()
                    self.make_remote_call(doctype, document_name, retrying=True)
                

                   
            return response_data

        except Exception as error:
            frappe.log_error(
                title="eTims Error",
                message=error,
                reference_doctype=self.doctype,
                reference_name=self.document_name,
            )
            # self.error = error
            # self.notify()
            return None


def get_response_data(response: requests.Response) -> Optional[Union[dict, str, bytes]]:
    content_type = response.headers.get("Content-Type", "").lower()

    if "application/json" in content_type:
        return response.json()
    elif "text/plain" in content_type or "text/html" in content_type:
        return response.text if response.text.strip() else None
    elif "application/xml" in content_type or "text/xml" in content_type:
        return response.text if response.text.strip() else None
    elif (
        "application/octet-stream" in content_type
        or "application/pdf" in content_type
        or "application/zip" in content_type
    ):
        return response.content

    return None


def update_integration_request(
    integration_request: str,
    status: Literal["Completed", "Failed"],
    output: str | None = None,
    error: str | None = None,
    request_description: str | None = None,
) -> None:
    """Updates the given integration request record.

    Args:
        integration_request (str): The provided integration request.
        status (Literal["Completed", "Failed"]): The new status of the request.
        output (str | None, optional): The response message, if any. Defaults to None.
        error (str | None, optional): The error message, if any. Defaults to None.
    """
    doc = frappe.get_doc("Integration Request", integration_request, for_update=True)

    if error:
        doc.error = error if doc.error is None or "null" else (doc.error + "\n" + error)

    if output:
        doc.output = (
            output if doc.output is None or "null" else (doc.output + "\n" + output)
        )

    if request_description:
        doc.request_description = (
            request_description
            if doc.request_description is None
            else (doc.request_description + " - " + request_description)
        )

    doc.status = status

    doc.save(ignore_permissions=True)
