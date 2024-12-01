from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def handle_pagination(page, per_page, queryset):
    """
    Function to handle pagination for a given queryset.

    Args:
        page (int): Current page number.
        per_page (int): Number of items per page.
        queryset (QuerySet): Django queryset to paginate.

    Returns:
        Paginator: Paginated queryset.
    """
    paginator = Paginator(queryset, per_page)
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj
