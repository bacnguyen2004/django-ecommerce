from rest_framework import status
from rest_framework import serializers
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)

from store.api.serializers import (
    ProductSerializer,
    CategorySerializer,
    RegisterSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    CustomerTokenObtainPairSerializer,
)

from store.services.api.product_service import (
    get_products,
    get_product_by_id,
)

from store.services.api.category_service import (
    get_categories,
)

from store.services.api.auth_service import (
    register_user,
)
from store.services.api.order_service import (
    cancel_my_order,
    get_all_orders_for_admin,
    get_my_orders,
    create_order,
    get_my_order_detail,
    get_order_detail_for_admin,
)


class CustomerTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomerTokenObtainPairSerializer


@extend_schema(
    tags=["Products"],
    parameters=[
        OpenApiParameter("search", OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter("category", OpenApiTypes.INT, OpenApiParameter.QUERY),
        OpenApiParameter("min_price", OpenApiTypes.DECIMAL, OpenApiParameter.QUERY),
        OpenApiParameter("max_price", OpenApiTypes.DECIMAL, OpenApiParameter.QUERY),
    ],
    responses=ProductSerializer(many=True),
)
@api_view(["GET"])
def products_api(request):

    search = request.GET.get("search")
    category = request.GET.get("category")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    products = get_products(
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price,
    )

    paginator = PageNumberPagination()
    paginator.page_size = 5

    result_page = paginator.paginate_queryset(
        products,
        request
    )

    serializer = ProductSerializer(
        result_page,
        many=True,
        context={
            "request": request
        }
    )

    return paginator.get_paginated_response(
        serializer.data
    )


@extend_schema(
    tags=["Products"],
    responses=ProductSerializer,
)
@api_view(["GET"])
def product_detail_api(request, id):

    product = get_product_by_id(id)

    serializer = ProductSerializer(
        product,
        context={
            "request": request
        }
    )

    return Response(serializer.data)


@extend_schema(
    tags=["Categories"],
    responses=CategorySerializer(many=True),
)
@api_view(["GET"])
def category_api(request):

    categories = get_categories()

    serializer = CategorySerializer(
        categories,
        many=True,
        context={
            "request": request
        }
    )

    return Response(serializer.data)


@extend_schema(
    tags=["Auth"],
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(description="User registered successfully"),
        400: OpenApiResponse(description="Validation error"),
    },
)
@api_view(["POST"])
def register_api(request):

    serializer = RegisterSerializer(
        data=request.data
    )

    if serializer.is_valid():

        user = register_user(
            serializer.validated_data
        )

        return Response(
            {
                "message": "Đăng ký thành công",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@extend_schema(
    tags=["Auth"],
    responses=OpenApiResponse(description="Authenticated user profile"),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_api(request):

    user = request.user

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })


@extend_schema(
    tags=["Orders"],
    responses=OrderSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders_api(request):

    orders = get_my_orders(request.user)

    serializer = OrderSerializer(
        orders,
        many=True,
        context={
            "request": request
        }
    )

    return Response(serializer.data)


@extend_schema(
    methods=["GET"],
    tags=["Orders"],
    responses=OrderSerializer(many=True),
    description="Admin-only endpoint for listing every completed order.",
)
@extend_schema(
    methods=["POST"],
    tags=["Orders"],
    request=OrderCreateSerializer,
    responses={
        201: OpenApiResponse(description="Order created successfully"),
        400: OpenApiResponse(description="Validation error"),
    },
    description="Create an order for the authenticated customer.",
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def orders_api(request):
    if request.method == "GET":
        orders = get_all_orders_for_admin(request.user)

        serializer = OrderSerializer(
            orders,
            many=True,
            context={
                "request": request
            }
        )

        return Response(serializer.data)

    serializer = OrderCreateSerializer(
        data=request.data
    )

    if serializer.is_valid():

        order = create_order(
            user=request.user,
            products_data=serializer.validated_data["products"]
        )

        return Response(
            {
                "message": "Đặt hàng thành công",
                "order_id": order.id,
                "total_price": order.total_price,
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@extend_schema(
    tags=["Orders"],
    responses=OrderSerializer,
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_detail_api(request, id):

    order = get_my_order_detail(
        user=request.user,
        order_id=id
    )

    serializer = OrderSerializer(order)

    return Response(serializer.data)


@extend_schema(
    tags=["Orders"],
    responses=OrderSerializer,
    description="Admin-only endpoint for viewing any completed order.",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_order_detail_api(request, id):

    order = get_order_detail_for_admin(
        user=request.user,
        order_id=id
    )

    serializer = OrderSerializer(order)

    return Response(serializer.data)


@extend_schema(
    tags=["Orders"],
    request=None,
    responses={
        200: inline_serializer(
            name="OrderCancelResponse",
            fields={
                "message": serializers.CharField(),
                "order": OrderSerializer(),
            }
        ),
        400: OpenApiResponse(description="Order cannot be cancelled"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_order_api(request, id):

    order = cancel_my_order(
        user=request.user,
        order_id=id
    )

    serializer = OrderSerializer(
        order,
        context={
            "request": request
        }
    )

    return Response({
        "message": "Hủy đơn hàng thành công",
        "order": serializer.data,
    })


