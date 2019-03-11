from rest_framework import serializers
from user.models import User, Group


class UserShowSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='get_role_display', read_only=True)
    role = serializers.CharField(write_only=True)
    group_name = serializers.CharField(source='user_group.name', read_only=True)
    user_group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), write_only=True)
    passwd = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = "__all__"
        # depth = 1



class GroupSerializer(serializers.ModelSerializer):

    # 包含对象列表 [obj, obj]
    # users = serializers.StringRelatedField(many=True)
    # 包含主键列表 [id, id, ]
    # users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # 包含指定字段 [name, name]
    # users = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Group
        # fields = ('name', 'alias', 'desc', 'users')
        fields = "__all__"