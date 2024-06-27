from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.transactions.transaction_list.views import TransactionListView
from apps.transactions.transaction_add.views import TransactionAddView
from apps.transactions.transaction_pay.views import TransactionPayView
from apps.transactions.transaction_update.views import TransactionUpdateView
from apps.transactions.transaction_delete.views import TransactionDeleteView

urlpatterns = [
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
    path (
        "transactions/update/<str:pk>",
        login_required(TransactionUpdateView.as_view(template_name="transactions_update.html")),
        name="transactions-update",
    ),
    path(
        "transactions/pay/<str:pk>",
        login_required(TransactionPayView.as_view(template_name="transactions_pay.html")),
        name="transactions-pay",
    ),
    path (
        "transactions/delete/<str:pk>/",
        login_required(TransactionDeleteView.as_view()),
        name="transactions-delete",
    ),
]
