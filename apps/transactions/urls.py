from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.transactions.transaction_list.views import TransactionListView
from apps.transactions.transaction_add.views import TransactionAddView
from apps.transactions.transaction_pay.views import ApiTransactionPayView, TransactionPayView, ApiPaymentWebhookView, \
    ApiTransactionSuccessView, ApiCheckTransactionStatusView, ApiTransactionFailedView
from apps.transactions.transaction_update.views import TransactionUpdateView
from apps.transactions.transaction_delete.views import TransactionDeleteView

urlpatterns = [
    # Api
    path(
        "api-transactions/pay/<str:pk>",
        login_required(ApiTransactionPayView.as_view(template_name="app-api-transaction-pay.html")),
        name="app-api-transactions-pay",
    ),
    # Api
    path(
        "api-payment/webhook/<str:pk>/",
        (ApiPaymentWebhookView.as_view(template_name="app-api-transaction-waiting.html")),
        name="app-api-payment-webhook",
    ),
    path(
        "api-payment/success/<str:pk>/",
        (ApiTransactionSuccessView.as_view(template_name="app-api-payment-success.html")),
        name="app-api-payment-success",
    ),
    path(
        "api-payment/failed/<str:pk>/",
        (ApiTransactionFailedView.as_view(template_name="app-api-payment-failed.html")),
        name="app-api-payment-failed",
    ),
    path(
        "api-payment/check-status/<str:pk>/",
        (ApiCheckTransactionStatusView.as_view()),
        name="api-check-transaction-status",
    ),

    path(
        "transactions/list/",
        login_required(TransactionListView.as_view(template_name="transactions_list.html")),
        name="transactions",
    ),
    path(
        "transactions/add/",
        login_required(TransactionAddView.as_view(template_name="transactions_add.html")),
        name="transactions-add",
    ),
    path(
        "transactions/update/<str:pk>",
        login_required(TransactionUpdateView.as_view(template_name="transactions_update.html")),
        name="transactions-update",
    ),
    path(
        "transactions/pay/<str:pk>",
        login_required(TransactionPayView.as_view(template_name="transactions_pay.html")),
        name="transactions-pay",
    ),
    path(
        "transactions/delete/<str:pk>/",
        login_required(TransactionDeleteView.as_view()),
        name="transactions-delete",
    ),
]
