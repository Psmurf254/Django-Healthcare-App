import json
import logging
import base64
import requests
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from config import settings
from web_project import TemplateLayout
from apps.api.specialists.models import Transaction, Appointment

logger = logging.getLogger(__name__)


class ApiTransactionPayView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        transaction = self.get_transaction(self.kwargs['pk'])
        context['transaction'] = transaction
        return context

    def get_access_token(self):
        consumer_key = settings.CONSUMER_KEY
        consumer_secret = settings.CONSUMER_SECRETE
        api_url = settings.API_URL

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
            messages.error(request, "Failed to get access token")
            raise Exception(error_message)

    def post(self, request, pk):
        transaction = self.get_transaction(pk)
        phone_number = request.POST.get('phone_number')
        amount = transaction.amount
        appointment_id = str(transaction.appointment.id)
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if appointment:
            transaction = get_object_or_404(Transaction, appointment=appointment)

        if not isinstance(amount, int):
            amount = int(amount)
        if not phone_number:
            messages.error(request, 'Phone number is required')
            return redirect(reverse_lazy('app-api-transactions-pay', kwargs={'pk': transaction.id}))
        elif not amount:
            messages.error(request, 'Amount is required')
            return redirect(reverse_lazy('app-api-transactions-pay', kwargs={'pk': transaction.id}))
        else:
            try:
                payload = {
                    "BusinessShortCode": settings.BUSINESS_SHORT_CODE,
                    "Password": settings.PAYMENT_PASSWORD,
                    "Timestamp": settings.TIMESTAMP,
                    "TransactionType": settings.TRANSACTION_TYPE,
                    "Amount": amount,
                    "PartyA": phone_number,
                    "PartyB": settings.PARTY_B,
                    "PhoneNumber": phone_number,
                    "CallBackURL": f"{settings.CALLBACK_URL_BASE}{appointment_id}/",
                    "AccountReference": settings.ACCOUNT_REFERENCE,
                    "TransactionDesc": settings.TRANSACTION_DESC,

                }
                try:
                    print('payload', payload)
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
                    messages.success(request, "STK Initiated successfully")
                    return redirect(reverse_lazy('app-api-payment-webhook', kwargs={'pk': appointment_id}))
                else:

                    messages.error(request, "STK push failed. Please try again later")
                    return redirect(reverse_lazy('app-api-transactions-pay', kwargs={'pk': transaction.id}))

            except Exception as e:
                messages.error(request, f"Error initiating STK push {e}")
                return redirect(reverse_lazy('app-api-transactions-pay', kwargs={'pk': transaction.id}))

    def get_transaction(self, pk):
        return get_object_or_404(Transaction, pk=pk)

    def transaction_exists(self, cleaned_data, current_transaction):
        matching_transactions = Transaction.objects.filter(
            Q(reference=cleaned_data['reference']) &
            Q(amount=cleaned_data['total']) &
            Q(status=cleaned_data['status'])
        ).exclude(pk=current_transaction.pk)
        return matching_transactions.exists()


@method_decorator(csrf_exempt, name='dispatch')
class ApiPaymentWebhookView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = kwargs.get('pk')
        appointment = get_object_or_404(Appointment, pk=pk)
        transaction = get_object_or_404(Transaction, appointment=appointment)
        context['transaction'] = transaction
        return context

    def post(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            response_data = json.loads(request.body)
            logger.info(f"Webhook received data: {response_data}")

            # Process the response data
            stk_callback = response_data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc', 'Unknown error')

            # Process the metadata to extract necessary information
            metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            transaction_details = {item.get('Name'): item.get('Value') for item in metadata if 'Value' in item}
            transaction_id = transaction_details.get('MpesaReceiptNumber', None)
            phone_number = transaction_details.get('PhoneNumber', None)
            amount = transaction_details.get('Amount', None)

            # Ensure transaction_id and appointment_id are present
            appointment = get_object_or_404(Appointment, pk=pk)
            if not appointment:
                raise ValueError('appointment_id parameter is missing in the request URL')

            # Handle successful payment
            if result_code == 0:
                transaction = get_object_or_404(Transaction, appointment__id=appointment.id)
                transaction.status = 'Paid'
                transaction.reference = transaction_id
                transaction.phone_number = phone_number
                transaction.amount = amount
                transaction.save()

                # Update appointment payment status
                appointment.payment_status = True
                appointment.save()

                logger.info(f"Payment successful: {transaction_id}")
                messages.success(request, 'Transaction completed')
                return redirect(reverse_lazy('app-api-payment-success', kwargs={'pk': transaction.id}))
            elif result_code == 1032:
                # Handle request cancelled by user
                transaction = get_object_or_404(Transaction, appointment__id=appointment.id)
                transaction.status = 'Cancelled'
                transaction.save()
                logger.warning(transaction)

                logger.warning('Payment request cancelled by user')
                messages.error(request, 'Payment request cancelled by user')
                return redirect(reverse_lazy('app-api-payment-failed', kwargs={'pk': pk}))
            else:
                # Handle failed payment
                logger.error(f"Payment failed: {result_desc}")
                return JsonResponse({'success': False, 'message': 'Payment failed'}, status=400)

        except ValueError as ve:
            logger.error(f"Missing parameter: {str(ve)}")
            return JsonResponse({'success': False, 'message': str(ve)}, status=400)

        except Exception as e:
            logger.error(f"Error processing payment webhook: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Error processing payment webhook'}, status=500)


class ApiTransactionSuccessView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        pk = kwargs.get('pk')
        transaction = get_object_or_404(Transaction, pk=pk)
        context['transaction'] = transaction
        return context


class ApiTransactionFailedView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        pk = kwargs.get('pk')
        transaction = get_object_or_404(Transaction, pk=pk)
        context['transaction'] = transaction
        return context


class ApiCheckTransactionStatusView(TemplateView):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        transaction = get_object_or_404(Transaction, pk=pk)
        if transaction.status == 'Paid':
            return JsonResponse({'status': 'Paid'})
        elif transaction.status == 'Cancelled':
            return JsonResponse({'status': 'Cancelled'})
        else:
            return JsonResponse({'status': 'Due'})


class TransactionPayView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        transaction = get_object_or_404(Transaction, pk=kwargs['pk'])
        context['transaction'] = transaction
        return context
