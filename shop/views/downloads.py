# shop/views/downloads.py
from ..models import Order, OrderItem
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.views.decorators.http import require_http_methods
import os
import mimetypes
import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from ..models import DownloadLog

logger = logging.getLogger("shop")


@login_required
@require_http_methods(["GET"])
def secure_download(request, order_item_id, download_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)

    # Ownership check
    if order_item.order.user != request.user:
        messages.error(request, "You do not have access to this download.")
        return redirect("shop:order_history")

    # Get download
    download = get_object_or_404(order_item.product.downloads, id=download_id)

    # Variant check
    if (
        order_item.purchased_download
        and order_item.purchased_download.id != download.id
    ):
        messages.error(request, "You did not purchase this version.")
        return redirect("shop:order_history")

    file_field = download.file
    if not file_field:
        messages.error(request, "No file available.")
        return redirect("shop:order_history")

    file_path = file_field.path
    if not os.path.exists(file_path):
        logger.error(f"Missing file: {file_path}")
        messages.error(request, "File not found.")
        return redirect("shop:order_history")

    # LIMIT CHECK (NEW SYSTEM)
    if order_item.download_count >= order_item.product.download_limit:
        logger.warning(f"Download limit reached: {order_item.id}")
        messages.error(request, "Download limit reached.")
        return redirect("shop:order_history")

    # DUPLICATE PROTECTION (CRITICAL)
    recent_download = DownloadLog.objects.filter(
        order_item=order_item,
        user=request.user,
        downloaded_at__gte=timezone.now() - timedelta(seconds=2)
    ).exists()

    if not recent_download:
        order_item.download_count += 1
        order_item.save()

        DownloadLog.objects.create(
            order_item=order_item,
            user=request.user
        )

    # Serve file
    filename = os.path.basename(file_path)
    content_type, _ = mimetypes.guess_type(filename)
    content_type = content_type or "application/octet-stream"

    response = FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        content_type=content_type,
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


@login_required
def purchases(request):
    """
    Display all purchases for the logged-in user.
    Includes download links for each product's downloads.
    """
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product__downloads")
        .order_by("-created")
    )
    return render(request, "shop/purchases.html", {"orders": orders})


@login_required
def order_history(request):
    """Display order history for the logged-in user."""
    orders = Order.objects.filter(user=request.user).order_by("-created")
    return render(request, "shop/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    """Display details for a specific order."""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "shop/purchases.html", {"order": order})
