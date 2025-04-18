from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Transaction, Withdrawal
from .serializers import TransactionSerializer, WithdrawalSerializer
from typing import Type, List, Dict, Any, Optional, Union
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
import logging

# Get a logger for this module
logger = logging.getLogger('agape.transactions')

# Create your views here.

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing transaction records.

    This viewset provides read-only access to transaction records belonging to the
    authenticated user. It does not allow creating, updating, or deleting transactions.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> List[Transaction]:
        """
        Get the list of transactions for the authenticated user.

        Returns:
            List[Transaction]: A queryset of transactions belonging to the current user
        """
        return Transaction.objects.filter(user=self.request.user)

class WithdrawalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing withdrawal requests.

    This viewset provides full CRUD operations for withdrawal requests, with additional
    actions for approving and rejecting withdrawals. Only staff members can approve
    or reject withdrawals.
    """
    serializer_class = WithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> List[Withdrawal]:
        """
        Get the list of withdrawals for the authenticated user.

        Returns:
            List[Withdrawal]: A queryset of withdrawals belonging to the current user
        """
        return Withdrawal.objects.filter(user=self.request.user)

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Create a new withdrawal request and associated transaction record.

        This method is called when a new withdrawal request is created. It creates
        a transaction record for the withdrawal and associates it with the user.

        Args:
            serializer: The serializer instance that validated the request data

        Returns:
            None
        """
        try:
            with transaction.atomic():
                withdrawal = serializer.save(user=self.request.user)

                # Create transaction record
                Transaction.objects.create(
                    user=self.request.user,
                    transaction_type='WITHDRAWAL',
                    amount=withdrawal.amount,
                    transaction_id=f"WD-{timezone.now().timestamp()}",
                    description=f"Withdrawal request for ${withdrawal.amount}"
                )

                logger.info(
                    f"Withdrawal request created: user={self.request.user.username}, "
                    f"amount=${withdrawal.amount}, type={withdrawal.withdrawal_type}"
                )
        except Exception as e:
            logger.error(
                f"Error creating withdrawal request: user={self.request.user.username}, "
                f"error={str(e)}"
            )
            raise

    @action(detail=True, methods=['post'])
    def approve(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Approve a withdrawal request.

        This action is only available to staff members. It changes the status of the
        withdrawal to 'APPROVED' and updates the associated transaction status.

        Args:
            request: The HTTP request
            pk: The primary key of the withdrawal to approve

        Returns:
            Response: The serialized withdrawal data

        Raises:
            HTTP 403: If the user is not a staff member
        """
        if not request.user.is_staff:
            logger.warning(
                f"Unauthorized approval attempt: user={request.user.username}, "
                f"withdrawal_id={pk}"
            )
            return Response(
                {"error": "Only staff members can approve withdrawals"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            withdrawal = self.get_object()

            # Log the initial state
            logger.info(
                f"Approving withdrawal: id={withdrawal.id}, user={withdrawal.user.username}, "
                f"amount=${withdrawal.amount}, current_status={withdrawal.status}"
            )

            if withdrawal.status != 'PENDING':
                logger.warning(
                    f"Cannot approve withdrawal with status {withdrawal.status}: "
                    f"id={withdrawal.id}, user={withdrawal.user.username}"
                )
                return Response(
                    {"error": f"Cannot approve withdrawal with status {withdrawal.status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                withdrawal.status = 'APPROVED'
                withdrawal.processed_at = timezone.now()
                withdrawal.save()

                # Update transaction status
                withdrawal.transaction.status = 'COMPLETED'
                withdrawal.transaction.completed_at = timezone.now()
                withdrawal.transaction.save()

            logger.info(
                f"Withdrawal approved: id={withdrawal.id}, user={withdrawal.user.username}, "
                f"amount=${withdrawal.amount}"
            )

            return Response(WithdrawalSerializer(withdrawal).data)

        except Exception as e:
            logger.error(
                f"Error approving withdrawal: id={pk}, error={str(e)}"
            )
            return Response(
                {"error": f"Error approving withdrawal: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def reject(self, request: Request, pk: Optional[int] = None) -> Response:
        """
        Reject a withdrawal request.

        This action is only available to staff members. It changes the status of the
        withdrawal to 'REJECTED' and updates the associated transaction status.

        Args:
            request: The HTTP request
            pk: The primary key of the withdrawal to reject

        Returns:
            Response: The serialized withdrawal data

        Raises:
            HTTP 403: If the user is not a staff member
        """
        if not request.user.is_staff:
            logger.warning(
                f"Unauthorized rejection attempt: user={request.user.username}, "
                f"withdrawal_id={pk}"
            )
            return Response(
                {"error": "Only staff members can reject withdrawals"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            withdrawal = self.get_object()

            # Log the initial state
            logger.info(
                f"Rejecting withdrawal: id={withdrawal.id}, user={withdrawal.user.username}, "
                f"amount=${withdrawal.amount}, current_status={withdrawal.status}"
            )

            if withdrawal.status != 'PENDING':
                logger.warning(
                    f"Cannot reject withdrawal with status {withdrawal.status}: "
                    f"id={withdrawal.id}, user={withdrawal.user.username}"
                )
                return Response(
                    {"error": f"Cannot reject withdrawal with status {withdrawal.status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                withdrawal.status = 'REJECTED'
                withdrawal.processed_at = timezone.now()
                withdrawal.save()

                # Update transaction status
                withdrawal.transaction.status = 'FAILED'
                withdrawal.transaction.completed_at = timezone.now()
                withdrawal.transaction.save()

            logger.info(
                f"Withdrawal rejected: id={withdrawal.id}, user={withdrawal.user.username}, "
                f"amount=${withdrawal.amount}"
            )

            return Response(WithdrawalSerializer(withdrawal).data)

        except Exception as e:
            logger.error(
                f"Error rejecting withdrawal: id={pk}, error={str(e)}"
            )
            return Response(
                {"error": f"Error rejecting withdrawal: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
