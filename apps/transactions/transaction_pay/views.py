import logging
from urllib import request
import requests
import base64
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.api.specialists.models import Transaction
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)
class TransactionPayView(PermissionRequiredMixin, TemplateView):
    permission_required = ("transactions.pay_transaction")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['transaction_id'] = self.get_transaction(self.kwargs['pk'])
        return context

    def get_access_token(self):
        consumer_key = 'jJBJkM31XGcvBP6rbdjdq0swCSm9eJFS'
        consumer_secret = 'KJmmfii1sbHiduyh'
        api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

        credentials = f"{consumer_key}:{consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode('utf-8')

        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            access_token = response.json().get('access_token')
            return access_token
        else:
            error_message = f"Failed to get access token: {response.status_code} - {response.text}"
            messages.error(request,f"Failed to get access token")
            raise Exception(error_message)

    def post(self, request, pk):
        transaction = self.get_transaction(pk)
        phone_number = request.POST.get('phone_number')
        amount = transaction.amount
        appointment_id = str(transaction.appointment.id)

        if not isinstance(amount, int):
            amount = int(amount)
        if not phone_number:
            messages.error(request, 'Phone number is required')
            return redirect('transactions')
        elif not amount:
            messages.error(request, 'Amount is required')
            return redirect('transaction_pay')
        else:
            # stk push
            try:
                payload = {
                    "BusinessShortCode": 174379,
                    "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjMwODI5MTEzNTEy",
                    "Timestamp": "20230829113512",
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": amount,
                    "PartyA": phone_number,
                    "PartyB": 174379,
                    "PhoneNumber": phone_number,
                    "CallBackURL": f"https://f1ed-2c0f-2a80-10ff-3b10-c03c-1536-8118-eec.ngrok-free.app/api"
                                   f"/payment_webhook/?appointment_id={appointment_id}",
                    "AccountReference": "Health 360",
                    "TransactionDesc": "Payment for Booking Services",
                    "appointment_id": appointment_id,
                }
                try:
                    access_token = self.get_access_token()
                except Exception as e:
                    logger.error(f"Error obtaining access token: {str(e)}")
                    return JsonResponse({'success': False, 'error': 'Failed to get access token'}, status=500)

                stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
                stk_push_headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}',
                }
                stk_push_response = requests.post(stk_push_url, json=payload, headers=stk_push_headers)

                if stk_push_response.status_code == 200:
                    messages.success(request, f"STK Initiated successfully ")
                    return redirect('transactions')
                else:
                   messages.error(request, f"stk push failed. Please try again later")
                   return redirect('transactions')

            except Exception as e:
                messages.error(request, f"Error initiating STK push {e}")
                return redirect('transactions')

    def get_transaction(self, pk):
        return get_object_or_404(Transaction, pk=pk)

    def transaction_exists(self, cleaned_data, current_transaction):
        matching_transactions = Transaction.objects.filter(
            Q(reference=cleaned_data['reference']) &
            Q(amount=cleaned_data['total']) &
            Q(status=cleaned_data['status'])
        ).exclude(pk=current_transaction.pk)
        return matching_transactions.exists()

