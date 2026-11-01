from rest_framework import serializers


class RouteRequestSerializer(serializers.Serializer):
    origin = serializers.CharField()
    destination = serializers.CharField()
    departure_time = serializers.DateTimeField()
    load_weight_lb = serializers.FloatField(min_value=0)
