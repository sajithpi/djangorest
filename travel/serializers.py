from rest_framework import serializers
from . models import TravelAim, TravelPlan, TravelRequest

class TravelAimSerializers(serializers.ModelSerializer):

    class Meta:
        model = TravelAim
        fields = ['id','name']

    def to_representation(self, instance):
        request = self.context['request']
        device= request.query_params.get('device','web')

        if device == 'web':
            print(f"device is webbbb")
            return {
                'label':instance.name,
                'value':instance.name
            }
        else:
            return super.to_representation(instance)
        

class TravelPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = TravelPlan
        fields = ['id', 'user', 'latitude', 'longitude', 'travel_date', 'days', 'description']

class TripRequestSerializer(serializers.ModelSerializer):

    # trip_id = serializers.SerializerMethodField()
    class Meta:
        model = TravelRequest
        fields = ['id','trip','requested_user','description','status']

    def create(self, validated_data):
        # Handle the creation logic here
        user = self.context['request'].user
        validated_data['requested_user'] = user
        trip_request = TravelRequest.objects.create(**validated_data)
        return trip_request
    # def get_trip_id(self, obj):
    #     return obj.trip.id if obj.trip else None

    def update(self, instance, validated_data):
        # Handle the update logic here
        user = self.context['request'].user
        validated_data['requested_user'] = user
        instance.trip = validated_data.get('trip', instance.trip)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance