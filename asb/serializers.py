
from rest_framework import serializers
from .models import Host, Group

class HostSerializer(serializers.ModelSerializer):
    # group = serializers.CharField(source='')
    class Meta:
        model = Host
        fields = "__all__"
        # fields = ['id', 'name', 'desc', 'ip', 'port', 'user', 'create_time', 'create_user', 'groups']
        depth = 1


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = "__all__"