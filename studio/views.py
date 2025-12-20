from django.shortcuts import render
from django.shortcuts import get_object_or_404
from studio.models import Gallery, GalleryImage


def gallery_image_modal(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk, published=True)

    images = list(image.gallery.images.filter(published=True))
    index = images.index(image)

    context = {
        "image": image,
        "prev_image": images[index - 1] if index > 0 else None,
        "next_image": images[index + 1] if index < len(images) - 1 else None,
    }

    return render(request, "studio/gallery/modal.html", context)


def gallery_view(request, slug):
    gallery = get_object_or_404(Gallery, slug=slug, published=True)
    return render(
        request,
        "studio/gallery/gallery.html",
        {"gallery": gallery},
    )
