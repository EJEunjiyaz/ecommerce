from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_mongoengine.viewsets import ModelViewSet

from scraper.shopee import shopee_scrape, shopee_scrape_variation
from website.models import ShopeeItem, ProductCategory
from website.serializer import ShopeeItemSerializer, ProductCategorySerializer


@api_view(['POST'])
def post_shopee_item_variations(request):
    url = request.data['url']
    product_name, available_options, variation1, variation2 = shopee_scrape_variation(url)
    # print(product_name, available_options, variation1, variation2)

    json = [
        {
            "name": product_name
        },
        {
            "key": available_options[0],
            "value": variation1
        },
        {
            "key": available_options[1],
            "value": variation2
        }
    ]
    print(json)
    return Response(json)


@api_view(['POST'])
def post_shopee_item(request):
    url = request.data['url']
    category = request.data['category']
    print(f"Currently scraping from {url}")
    product_name, product_image, store_name, store_link, store_avatar, variations_list, rating_score, rating_voter, product_sold = shopee_scrape(
        url)

    variations = []
    for variation in variations_list:
        # print("variation", variation)
        options = []
        for key, value in variation.items():
            # print(f"key {key} value {value}")
            option_dict = {"key": key, "value": value}
            options.append(option_dict)
        variations.append(options)
    data = {
        "name": product_name,
        "url": url,
        "image": product_image,
        "store_name": store_name,
        "variations": variations,
        "rating": {
            "avg_star": rating_score,
            "voter": rating_voter
        },
        "sold": product_sold,
        "category": category
    }
    try:
        option1 = request.data['option1']
        data["option1"] = option1
    except:
        pass
    try:
        option2 = request.data['option2']
        data["option2"] = option2
    except:
        pass
    print(data)

    shopee_item_serializer = ShopeeItemSerializer(data=data)
    shopee_item_serializer.is_valid(raise_exception=True)
    shopee_item_serializer.save()
    return Response(shopee_item_serializer.data)


class ShopeeItemByCategory(APIView):
    def get(self, request):
        category = request.query_params['category']
        queryset = ShopeeItem.objects.all().filter(category=category)
        for i in queryset:
            print(i.values())
        # serializer = ShopeeItemSerializer(queryset, many=True)
        # print(serializer.data[0])


# class StoreViewSet(ModelViewSet):
#     queryset = Store.objects.all()
#     serializer_class = ShopeeItemSerializer


class ProductCategoryViewSet(ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ShopeeItemViewSet(ModelViewSet):
    queryset = ShopeeItem.objects.all()
    serializer_class = ShopeeItemSerializer
